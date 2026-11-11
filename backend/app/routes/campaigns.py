from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.campaign import Campaign, CampaignApproval
from app.models.lead import Lead
from app.models.user import User
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse,
    CampaignApprovalRequest, CampaignPreviewResponse, CampaignEligibilityResponse
)
from app.security.auth import get_current_user, require_roles, create_unsubscribe_token
from app.services.compliance import validate_campaign_eligibility, is_suppressed
from app.services.audit import log_audit

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

@router.get("", response_model=List[CampaignResponse])
def list_campaigns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaigns = db.query(Campaign).order_by(Campaign.id.desc()).all()
    return campaigns

@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(
    campaign_in: CampaignCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Calculate initial target audience count
    audience_query = db.query(Lead).filter(
        Lead.lead_status == "approved",
        Lead.email_verification_status == "valid"
    )
    if campaign_in.sector and campaign_in.sector != "All":
        audience_query = audience_query.filter(Lead.sector == campaign_in.sector)
    
    target_count = audience_query.count()

    campaign = Campaign(
        name=campaign_in.name.strip(),
        subject=campaign_in.subject.strip(),
        body_template=campaign_in.body_template.strip(),
        sector=campaign_in.sector or "All",
        daily_limit=campaign_in.daily_limit or 50,
        target_audience_count=target_count,
        status="draft",
        created_by_id=current_user.id
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    log_audit(
        db,
        actor_email=current_user.email,
        action="CAMPAIGN_CREATE",
        object_type="CAMPAIGN",
        object_id=str(campaign.id),
        details=f"Created campaign '{campaign.name}' in draft status",
        ip_address=request.client.host if request.client else None
    )

    return campaign

@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    return campaign

@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    update_data = campaign_update.model_dump(exclude_unset=True)
    previous_status = campaign.status

    # Rule: Any modification to an approved campaign must reset its approval
    was_approved = (previous_status == "approved")

    for key, value in update_data.items():
        if value is not None:
            setattr(campaign, key, value)

    if was_approved and any(k in update_data for k in ["name", "subject", "body_template", "sector"]):
        campaign.status = "pending_approval"
        campaign.approved_by_id = None
        campaign.approved_at = None
        
        # Record approval reset audit
        reset_approval = CampaignApproval(
            campaign_id=campaign.id,
            reviewer_id=current_user.id,
            action="reset",
            notes="Approval revoked automatically due to campaign template modification."
        )
        db.add(reset_approval)

    # Recalculate audience count
    audience_query = db.query(Lead).filter(
        Lead.lead_status == "approved",
        Lead.email_verification_status == "valid"
    )
    if campaign.sector and campaign.sector != "All":
        audience_query = audience_query.filter(Lead.sector == campaign.sector)
    campaign.target_audience_count = audience_query.count()

    campaign.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(campaign)

    log_audit(
        db,
        actor_email=current_user.email,
        action="CAMPAIGN_UPDATE",
        object_type="CAMPAIGN",
        object_id=str(campaign.id),
        details=f"Updated campaign '{campaign.name}'. Approval status: {campaign.status}",
        ip_address=request.client.host if request.client else None
    )

    return campaign

@router.post("/{campaign_id}/approve")
def approve_campaign(
    campaign_id: int,
    approval_req: CampaignApprovalRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "reviewer"]))
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    # Strict Rule: The campaign creator must not approve their own production campaign!
    if campaign.created_by_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Four-Eyes Compliance Policy Violation: Campaign creator cannot approve their own campaign. A separate reviewer or admin must approve it."
        )

    if approval_req.action == "approve":
        campaign.status = "approved"
        campaign.approved_by_id = current_user.id
        campaign.approved_at = datetime.now(timezone.utc)
        approval_action = "approved"
    else:
        campaign.status = "draft"
        campaign.approved_by_id = None
        campaign.approved_at = None
        approval_action = "rejected"

    approval_record = CampaignApproval(
        campaign_id=campaign.id,
        reviewer_id=current_user.id,
        action=approval_action,
        notes=approval_req.notes or f"Campaign {approval_action} by reviewer."
    )
    db.add(approval_record)
    db.commit()
    db.refresh(campaign)

    log_audit(
        db,
        actor_email=current_user.email,
        action=f"CAMPAIGN_{approval_action.upper()}",
        object_type="CAMPAIGN",
        object_id=str(campaign.id),
        details=f"Campaign '{campaign.name}' marked {approval_action}. Notes: {approval_req.notes}",
        ip_address=request.client.host if request.client else None
    )

    return {
        "success": True,
        "campaign_id": campaign.id,
        "status": campaign.status,
        "approved_by": current_user.email,
        "approved_at": campaign.approved_at.isoformat() if campaign.approved_at else None
    }

@router.post("/{campaign_id}/pause")
def pause_campaign(
    campaign_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    new_status = "paused" if campaign.status == "approved" else ("approved" if campaign.status == "paused" else campaign.status)
    campaign.status = new_status
    db.commit()

    log_audit(
        db,
        actor_email=current_user.email,
        action="CAMPAIGN_PAUSE_TOGGLE",
        object_type="CAMPAIGN",
        object_id=str(campaign.id),
        details=f"Campaign '{campaign.name}' status set to {new_status}",
        ip_address=request.client.host if request.client else None
    )

    return {"success": True, "campaign_id": campaign.id, "status": campaign.status}

@router.get("/{campaign_id}/preview", response_model=CampaignPreviewResponse)
def preview_campaign_email(
    campaign_id: int,
    lead_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    # Pick specified lead or first eligible lead in target sector
    lead = None
    if lead_id:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        query = db.query(Lead)
        if campaign.sector and campaign.sector != "All":
            query = query.filter(Lead.sector == campaign.sector)
        lead = query.first()

    if not lead:
        # Fallback dummy representation for preview
        lead = Lead(
            company_name="Acme Global Corporation",
            contact_name="Jane Doe",
            email="jane.doe@acmeglobal.demo",
            sector=campaign.sector if campaign.sector != "All" else "Enterprise Software"
        )

    # First name extraction
    first_name = lead.contact_name.split()[0] if lead.contact_name else "there"
    company = lead.company_name or "your company"
    sector = lead.sector or "your industry"

    # Merge tags
    rendered_subject = campaign.subject.replace("{{first_name}}", first_name)
    rendered_subject = rendered_subject.replace("{{company}}", company)
    rendered_subject = rendered_subject.replace("{{sector}}", sector)

    rendered_body = campaign.body_template.replace("{{first_name}}", first_name)
    rendered_body = rendered_body.replace("{{company}}", company)
    rendered_body = rendered_body.replace("{{sector}}", sector)

    # Generate secure signed unsubscribe link
    unsub_token = create_unsubscribe_token(lead.email)
    frontend_base = settings.FRONTEND_URL.rstrip('/')
    unsubscribe_url = f"{frontend_base}/unsubscribe?token={unsub_token}"

    full_body = f"{rendered_body}\n\n---\nTo opt-out of future B2B correspondence, click here:\n{unsubscribe_url}"

    return CampaignPreviewResponse(
        campaign_id=campaign.id,
        subject=rendered_subject,
        rendered_body=full_body,
        recipient_email=lead.email,
        first_name=first_name,
        company=company,
        sector=sector,
        unsubscribe_url=unsubscribe_url
    )

@router.get("/{campaign_id}/eligibility", response_model=CampaignEligibilityResponse)
def check_campaign_eligibility(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    leads_query = db.query(Lead)
    if campaign.sector and campaign.sector != "All":
        leads_query = leads_query.filter(Lead.sector == campaign.sector)
    leads = leads_query.all()

    eligible_count = 0
    suppressed_count = 0
    unapproved_leads_count = 0
    unverified_leads_count = 0

    for lead in leads:
        supp, _ = is_suppressed(db, lead.email)
        if supp:
            suppressed_count += 1
            continue
        if lead.email_verification_status != "valid":
            unverified_leads_count += 1
            continue
        if lead.lead_status != "approved":
            unapproved_leads_count += 1
            continue

        eligible_count += 1

    return CampaignEligibilityResponse(
        campaign_id=campaign.id,
        eligible_count=eligible_count,
        suppressed_count=suppressed_count,
        unapproved_leads_count=unapproved_leads_count,
        unverified_leads_count=unverified_leads_count,
        is_campaign_approved=(campaign.status == "approved")
    )
