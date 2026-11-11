from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogPagination
from app.security.auth import get_current_user, require_roles

router = APIRouter(prefix="/audit-logs", tags=["Audit"])

@router.get("", response_model=AuditLogPagination)
def list_audit_logs(
    page: int = Query(1, ge=1),
    size: int = Query(25, ge=1, le=100),
    action: Optional[str] = None,
    object_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "reviewer"]))
):
    query = db.query(AuditLog)

    if action and action != "All":
        query = query.filter(AuditLog.action == action)

    if object_type and object_type != "All":
        query = query.filter(AuditLog.object_type == object_type)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                AuditLog.actor_email.ilike(search_term),
                AuditLog.details.ilike(search_term),
                AuditLog.action.ilike(search_term)
            )
        )

    total = query.count()
    items = query.order_by(AuditLog.timestamp.desc()).offset((page - 1) * size).limit(size).all()

    return AuditLogPagination(
        items=items,
        total=total,
        page=page,
        size=size
    )

