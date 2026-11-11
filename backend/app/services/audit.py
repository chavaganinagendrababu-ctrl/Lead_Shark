from typing import Optional
from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def log_audit(
    db: Session,
    actor_email: str,
    action: str,
    object_type: str,
    object_id: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """Records security and operational audit trail entry."""
    # Ensure sensitive patterns are not exposed
    safe_details = details
    if safe_details and ("password" in safe_details.lower() or "secret" in safe_details.lower()):
        safe_details = "[REDACTED_SECURITY_DATA]"

    audit_entry = AuditLog(
        actor_email=actor_email,
        action=action,
        object_type=object_type,
        object_id=str(object_id) if object_id is not None else None,
        details=safe_details,
        ip_address=ip_address
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry

