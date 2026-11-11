import io
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status, Response, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.lead import Lead
from app.models.user import User
from app.models.compliance import SuppressionList
from app.schemas.lead import (
    LeadCreate, LeadUpdate, LeadResponse, LeadPagination, LeadVerifyResult
)
from app.security.auth import get_current_user, require_roles
from app.services.verification import verify_email_address
from app.services.classification import classifier_service
from app.services.compliance import is_suppressed
from app.services.audit import log_audit
from app.utils.csv_handler import parse_and_import_leads_csv, sanitize_csv_value

router = APIRouter(prefix="/leads", tags=["Leads"])

@router.get("", response_model=LeadPagination)
def list_leads(
    page: int = Query(1, ge=1),
    size: int = Query(15, ge=1, le=100),
    search: Optional[str] = None,
    sector: Optional[str] = None,
    region: Optional[str] = None,
    verification_status: Optional[str] = None,
    lead_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Lead)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Lead.company_name.ilike(search_pattern),
                Lead.contact_name.ilike(search_pattern),
                Lead.email.ilike(search_pattern),
                Lead.job_title.ilike(search_pattern)
            )
        )

    if sector and sector != "All":
        query = query.filter(Lead.sector == sector)

    if region and region != "All":
        query = query.filter(Lead.region == region)

    if verification_status and verification_status != "All":
        query = query.filter(Lead.email_verification_status == verification_status)

    if lead_status and lead_status != "All":
        query = query.filter(Lead.lead_status == lead_status)

    total = query.count()
    items = query.order_by(Lead.id.desc()).offset((page - 1) * size).limit(size).all()
    pages = (total + size - 1) // size if total > 0 else 1

    return LeadPagination(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(
    lead_in: LeadCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    clean_email = lead_in.email.lower().strip()

    # Check duplicate
    existing = db.query(Lead).filter(Lead.email == clean_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lead with email '{clean_email}' already exists in database (ID: {existing.id})."
        )

    # Check suppression
    suppressed, reason = is_suppressed(db, clean_email)
    if suppressed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{clean_email}' is on the Global Suppression List ({reason}) and cannot be imported."
        )

    # Classification
    if not lead_in.sector or lead_in.sector == "Other":
        classification = classifier_service.classify(
            company_name=lead_in.company_name,
            website=lead_in.website or "",
            job_title=lead_in.job_title or ""
        )
        sector = classification["sector"]
        confidence = classification["confidence"]
        clf_reason = classification["reason"]
    else:
        sector = lead_in.sector
        confidence = 0.90
        clf_reason = "Sector manually specified during lead creation"

    lead = Lead(
        company_name=lead_in.company_name.strip(),
        contact_name=lead_in.contact_name.strip(),
        job_title=lead_in.job_title.strip() if lead_in.job_title else None,
        email=clean_email,
        phone=lead_in.phone.strip() if lead_in.phone else None,
        website=lead_in.website.strip() if lead_in.website else None,
        sector=sector,
        region=lead_in.region.strip() if lead_in.region else None,
        source_type="manual",
        source_url=lead_in.source_url or "Manual Entry",
        collection_date=datetime.now(timezone.utc),
        lawful_basis_note=lead_in.lawful_basis_note,
        # Rule: Do not assume that an entered email address is verified
        email_verification_status="unknown",
        verification_details="Pending initial verification",
        lead_status="pending_review",
        classification_confidence=confidence,
        classification_reason=clf_reason
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    log_audit(
        db,
        actor_email=current_user.email,
        action="LEAD_CREATE",
        object_type="LEAD",
        object_id=str(lead.id),
        details=f"Created lead for company {lead.company_name} ({lead.email})",
        ip_address=request.client.host if request.client else None
    )

    return lead

@router.get("/export")
def export_leads_csv(
    sector: Optional[str] = None,
    lead_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Exports leads into a CSV file with Formula Injection Protection (CSV DDE hardening)."""
    query = db.query(Lead)
    if sector and sector != "All":
        query = query.filter(Lead.sector == sector)
    if lead_status and lead_status != "All":
        query = query.filter(Lead.lead_status == lead_status)

    leads = query.order_by(Lead.id.desc()).all()

    output = io.StringIO()
    headers = [
        "id", "company_name", "contact_name", "job_title", "email",
        "phone", "website", "sector", "region", "source_type",
        "email_verification_status", "lead_status", "lawful_basis_note", "created_at"
    ]
    output.write(",".join(headers) + "\n")

    for l in leads:
        row = [
            str(l.id),
            f'"{sanitize_csv_value(l.company_name)}"',
            f'"{sanitize_csv_value(l.contact_name)}"',
            f'"{sanitize_csv_value(l.job_title or "")}"',
            f'"{sanitize_csv_value(l.email)}"',
            f'"{sanitize_csv_value(l.phone or "")}"',
            f'"{sanitize_csv_value(l.website or "")}"',
            f'"{sanitize_csv_value(l.sector or "")}"',
            f'"{sanitize_csv_value(l.region or "")}"',
            f'"{sanitize_csv_value(l.source_type or "")}"',
            f'"{sanitize_csv_value(l.email_verification_status)}"',
            f'"{sanitize_csv_value(l.lead_status)}"',
            f'"{sanitize_csv_value(l.lawful_basis_note or "")}"',
            f'"{l.created_at.isoformat()}"'
        ]
        output.write(",".join(row) + "\n")

    log_audit(
        db,
        actor_email=current_user.email,
        action="LEAD_EXPORT_CSV",
        object_type="LEAD",
        details=f"Exported {len(leads)} leads with formula injection protection"
    )

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

@router.post("/import")
async def import_leads_csv(
    file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type invalid. Please upload a valid CSV (.csv) file."
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded CSV file is empty.")

    result = parse_and_import_leads_csv(
        file_bytes=file_bytes,
        db=db,
        source_name=file.filename
    )

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error"))

    log_audit(
        db,
        actor_email=current_user.email,
        action="CSV_IMPORT",
        object_type="LEAD",
        details=f"Imported CSV '{file.filename}': {result['imported']} imported, {result['duplicates']} duplicates, {result['suppressed']} suppressed, {result['invalid']} invalid.",
        ip_address=request.client.host if request and request.client else None
    )

    return result

@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead

@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    update_data = lead_update.model_dump(exclude_unset=True)

    # If updating email, ensure it's not a duplicate and not suppressed
    if "email" in update_data and update_data["email"]:
        new_email = update_data["email"].lower().strip()
        if new_email != lead.email:
            existing = db.query(Lead).filter(Lead.email == new_email).first()
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists in database.")
            suppressed, reason = is_suppressed(db, new_email)
            if suppressed:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email is suppressed: {reason}")
            lead.email = new_email
            # Reset verification status on email change
            lead.email_verification_status = "unknown"
            lead.verification_details = "Email modified. Verification required."

    for key, value in update_data.items():
        if key != "email" and value is not None:
            setattr(lead, key, value)

    lead.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(lead)

    log_audit(
        db,
        actor_email=current_user.email,
        action="LEAD_UPDATE",
        object_type="LEAD",
        object_id=str(lead.id),
        details=f"Updated lead {lead.id} ({lead.company_name})",
        ip_address=request.client.host if request.client else None
    )

    return lead

@router.delete("/{lead_id}")
def delete_lead(
    lead_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "reviewer"]))
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    company_name = lead.company_name
    email = lead.email

    db.delete(lead)
    db.commit()

    log_audit(
        db,
        actor_email=current_user.email,
        action="LEAD_DELETE",
        object_type="LEAD",
        object_id=str(lead_id),
        details=f"Deleted lead ID {lead_id} for company '{company_name}' ({email}). Note: suppression protections remain intact.",
        ip_address=request.client.host if request.client else None
    )

    return {"success": True, "message": f"Lead {lead_id} removed successfully"}

@router.post("/{lead_id}/verify", response_model=LeadVerifyResult)
def verify_lead(
    lead_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    result = verify_email_address(lead.email)
    lead.email_verification_status = result["status"]
    lead.verification_details = result["details"]
    lead.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(lead)

    log_audit(
        db,
        actor_email=current_user.email,
        action="LEAD_VERIFY",
        object_type="LEAD",
        object_id=str(lead.id),
        details=f"Verified lead {lead.id} ({lead.email}): result={result['status']}",
        ip_address=request.client.host if request.client else None
    )

    return LeadVerifyResult(
        lead_id=lead.id,
        email=lead.email,
        status=result["status"],
        details=result["details"],
        mx_records_found=result["mx_records_found"]
    )

@router.post("/{lead_id}/classify", response_model=LeadResponse)
def classify_lead_sector(
    lead_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    clf = classifier_service.classify(
        company_name=lead.company_name,
        website=lead.website or "",
        job_title=lead.job_title or ""
    )
    lead.sector = clf["sector"]
    lead.classification_confidence = clf["confidence"]
    lead.classification_reason = clf["reason"]
    lead.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(lead)

    log_audit(
        db,
        actor_email=current_user.email,
        action="LEAD_CLASSIFY",
        object_type="LEAD",
        object_id=str(lead.id),
        details=f"Classified lead {lead.id} into '{lead.sector}' (confidence: {lead.classification_confidence})",
        ip_address=request.client.host if request.client else None
    )

    return lead
