from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.lead import Lead
from app.models.campaign import Campaign
from app.models.compliance import SuppressionList
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.analytics import DashboardStats, SectorStat, RegionStat, RecentLeadStat
from app.security.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_leads = db.query(Lead).count()
    verified_leads = db.query(Lead).filter(Lead.email_verification_status == "valid").count()
    pending_review = db.query(Lead).filter(Lead.lead_status.in_(["new", "pending_review"])).count()
    approved_leads = db.query(Lead).filter(Lead.lead_status == "approved").count()
    invalid_emails = db.query(Lead).filter(Lead.email_verification_status == "invalid").count()

    total_campaigns = db.query(Campaign).count()
    active_campaigns = db.query(Campaign).filter(Campaign.status.in_(["approved", "pending_approval"])).count()
    suppressed_leads = db.query(SuppressionList).count()

    # Sector distribution
    sector_counts = db.query(Lead.sector, func.count(Lead.id)).group_by(Lead.sector).all()
    sector_distribution = [
        SectorStat(sector=s or "Unclassified", count=c) for s, c in sector_counts
    ]

    # Region distribution
    region_counts = db.query(Lead.region, func.count(Lead.id)).group_by(Lead.region).all()
    region_distribution = [
        RegionStat(region=r or "Unknown", count=c) for r, c in region_counts if r
    ]

    # Recent leads
    recent_leads_query = db.query(Lead).order_by(Lead.created_at.desc()).limit(6).all()
    recent_leads = [
        RecentLeadStat(
            id=l.id,
            company_name=l.company_name,
            contact_name=l.contact_name,
            email=l.email,
            sector=l.sector,
            lead_status=l.lead_status,
            email_verification_status=l.email_verification_status
        ) for l in recent_leads_query
    ]

    # Recent activities from Audit Log
    recent_audit = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(8).all()
    recent_activities = [
        {
            "id": a.id,
            "actor": a.actor_email,
            "action": a.action,
            "object_type": a.object_type,
            "details": a.details,
            "timestamp": a.timestamp.isoformat()
        } for a in recent_audit
    ]

    return DashboardStats(
        total_leads=total_leads,
        verified_leads=verified_leads,
        pending_review=pending_review,
        approved_leads=approved_leads,
        total_campaigns=total_campaigns,
        active_campaigns=active_campaigns,
        suppressed_leads=suppressed_leads,
        invalid_emails=invalid_emails,
        sector_distribution=sector_distribution,
        region_distribution=region_distribution,
        recent_leads=recent_leads,
        recent_activities=recent_activities
    )

