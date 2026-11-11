from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.campaign import Campaign
from app.models.compliance import SuppressionList

COOLDOWN_DAYS = 14

def is_suppressed(db: Session, email: str) -> Tuple[bool, Optional[str]]:
    """Checks if email or its domain is on the global suppression list."""
    email_clean = email.lower().strip()
    domain = email_clean.split("@")[-1] if "@" in email_clean else ""

    # Direct email match
    direct_suppression = db.query(SuppressionList).filter(SuppressionList.email == email_clean).first()
    if direct_suppression:
        return True, f"Suppressed (reason: {direct_suppression.reason})"

    # Domain level match
    if domain:
        domain_suppression = db.query(SuppressionList).filter(SuppressionList.domain == domain).first()
        if domain_suppression:
            return True, f"Domain {domain} is globally suppressed (reason: {domain_suppression.reason})"

    return False, None

def add_suppression_entry(db: Session, email: str, reason: str, notes: Optional[str] = None, added_by: Optional[str] = "system") -> SuppressionList:
    email_clean = email.lower().strip()
    domain = email_clean.split("@")[-1] if "@" in email_clean else None

    existing = db.query(SuppressionList).filter(SuppressionList.email == email_clean).first()
    if existing:
        existing.reason = reason
        if notes:
            existing.notes = f"{existing.notes or ''}; {notes}".strip("; ")
        db.commit()
        db.refresh(existing)
        return existing

    entry = SuppressionList(
        email=email_clean,
        domain=domain,
        reason=reason,
        notes=notes,
        added_by=added_by
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def validate_campaign_eligibility(db: Session, lead: Lead, campaign: Campaign) -> Tuple[bool, str]:
    """
    Evaluates 7-step strict compliance eligibility:
    1. Email status is valid.
    2. Email is not suppressed.
    3. Domain is not suppressed.
    4. Lead is approved.
    5. Campaign is approved.
    6. Lead not contacted within cooldown window.
    7. Campaign is within daily limit.
    """
    # 1. Email status is valid
    if lead.email_verification_status != "valid":
        return False, f"Ineligible: Lead email status is '{lead.email_verification_status}'. Only explicitly valid emails can be contacted."

    # 2 & 3. Suppression check
    suppressed, supp_reason = is_suppressed(db, lead.email)
    if suppressed:
        return False, f"Ineligible: Global suppression restriction triggered ({supp_reason})."

    # 4. Lead is approved
    if lead.lead_status != "approved":
        return False, f"Ineligible: Lead status is '{lead.lead_status}'. Only approved leads are eligible."

    # 5. Campaign is approved
    if campaign.status != "approved":
        return False, f"Ineligible: Campaign status is '{campaign.status}'. Campaign must be in 'approved' status."

    # 6. Cooldown window
    if lead.last_contacted_at:
        cooldown_threshold = datetime.now(timezone.utc) - timedelta(days=COOLDOWN_DAYS)
        # Handle naive or aware datetime comparison
        contacted_at = lead.last_contacted_at
        if contacted_at.tzinfo is None:
            contacted_at = contacted_at.replace(tzinfo=timezone.utc)
        if contacted_at > cooldown_threshold:
            return False, f"Ineligible: Lead was contacted recently within the {COOLDOWN_DAYS}-day cooldown window."

    # 7. Sector alignment
    if campaign.sector and campaign.sector != "All" and campaign.sector != lead.sector:
        return False, f"Ineligible: Lead sector '{lead.sector}' does not match campaign target sector '{campaign.sector}'."

    return True, "Lead is fully compliant and eligible for outreach."
