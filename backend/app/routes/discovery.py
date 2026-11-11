from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.discovery import DiscoveryJob
from app.models.lead import Lead
from app.models.compliance import SuppressionList
from app.models.user import User
from app.schemas.discovery import DiscoveryJobCreate, DiscoveryJobResponse
from app.security.auth import get_current_user
from app.services.audit import log_audit
from app.services.classification import classifier_service

router = APIRouter(prefix="/discovery", tags=["Discovery"])

@router.get("/jobs", response_model=List[DiscoveryJobResponse])
def get_discovery_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    jobs = db.query(DiscoveryJob).order_by(DiscoveryJob.id.desc()).limit(50).all()
    return jobs

@router.post("/jobs", response_model=DiscoveryJobResponse, status_code=status.HTTP_201_CREATED)
def trigger_discovery_job(
    job_in: DiscoveryJobCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Simulates discovery via permitted open directory mock connectors.
    Clearly tags discovered records as 'permitted_api_sample' with full provenance.
    """
    source_name = job_in.source_name or "Permitted Public B2B Registry (Demo)"
    
    # Create the job record
    job = DiscoveryJob(
        source_type=job_in.source_type,
        source_name=source_name,
        status="completed",
        total_discovered=0,
        total_imported=0,
        total_rejected=0,
        created_by_id=current_user.id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Sample compliant registry records for demonstration
    mock_registry = [
        {
            "company_name": "Nexus Neural Dynamics",
            "contact_name": "Dr. Aris Thorne",
            "job_title": "Director of Research",
            "email": "aris.thorne@nexusneural.demo",
            "phone": "+1-555-4819",
            "website": "https://nexusneural.demo",
            "sector": "Information Technology",
            "region": "North America",
        },
        {
            "company_name": "Solaris Energy Innovations",
            "contact_name": "Lila Henderson",
            "job_title": "VP Strategic Partnerships",
            "email": "lila.h@solarisenergy.demo",
            "phone": "+44-20-8910-1122",
            "website": "https://solarisenergy.demo",
            "sector": "Manufacturing",
            "region": "Europe",
        },
        {
            "company_name": "Aether Health Biometrics",
            "contact_name": "Devin O'Connor",
            "job_title": "Head of Clinical Systems",
            "email": "devin.oc@aetherhealth.demo",
            "phone": "+1-555-7721",
            "website": "https://aetherhealth.demo",
            "sector": "Healthcare",
            "region": "North America",
        },
        {
            "company_name": "Beacon Retail Ventures",
            "contact_name": "Maya Lin",
            "job_title": "Merchandising Lead",
            "email": "maya.lin@beaconretail.demo",
            "phone": "+65-6712-4450",
            "website": "https://beaconretail.demo",
            "sector": "Retail",
            "region": "Asia-Pacific",
        }
    ]

    discovered = len(mock_registry)
    imported = 0
    rejected = 0

    for item in mock_registry:
        email = item["email"].lower().strip()

        # Check suppression
        suppressed = db.query(SuppressionList).filter(
            (SuppressionList.email == email) | (SuppressionList.domain == email.split("@")[-1])
        ).first()
        if suppressed:
            rejected += 1
            continue

        # Check duplicate
        existing = db.query(Lead).filter(Lead.email == email).first()
        if existing:
            rejected += 1
            continue

        # Classify
        clf = classifier_service.classify(item["company_name"], item["website"], item["job_title"])

        lead = Lead(
            company_name=item["company_name"],
            contact_name=item["contact_name"],
            job_title=item["job_title"],
            email=email,
            phone=item["phone"],
            website=item["website"],
            sector=clf["sector"],
            region=item["region"],
            source_type="permitted_registry_demo",
            source_url=f"Demo Registry API ({source_name})",
            collection_date=datetime.now(timezone.utc),
            lawful_basis_note="B2B legitimate commercial outreach; public business directory profile",
            email_verification_status="unknown",
            verification_details="Discovered via registry connector. Verification pending.",
            lead_status="pending_review",
            classification_confidence=clf["confidence"],
            classification_reason=clf["reason"]
        )
        db.add(lead)
        imported += 1

    job.total_discovered = discovered
    job.total_imported = imported
    job.total_rejected = rejected
    job.summary_note = f"Discovery run finished. {imported} compliant leads staged for review; {rejected} rejected due to duplicates or suppression."
    db.commit()
    db.refresh(job)

    log_audit(
        db,
        actor_email=current_user.email,
        action="DISCOVERY_JOB_COMPLETED",
        object_type="DISCOVERY",
        object_id=str(job.id),
        details=job.summary_note,
        ip_address=request.client.host if request.client else None
    )

    return job
