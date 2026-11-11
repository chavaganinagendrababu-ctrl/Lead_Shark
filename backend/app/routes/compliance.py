from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.compliance import SuppressionList
from app.models.user import User
from app.schemas.compliance import (
    SuppressionCreate, SuppressionResponse, UnsubscribeRequest, UnsubscribeResponse
)
from app.security.auth import (
    get_current_user, require_roles, verify_unsubscribe_token
)
from app.services.compliance import add_suppression_entry
from app.services.audit import log_audit

router = APIRouter(tags=["Compliance"])

@router.get("/api/suppression", response_model=List[SuppressionResponse])
def get_suppression_list(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(SuppressionList)
    if search:
        search_term = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                SuppressionList.email.ilike(search_term),
                SuppressionList.domain.ilike(search_term),
                SuppressionList.reason.ilike(search_term),
                SuppressionList.notes.ilike(search_term)
            )
        )
    return query.order_by(SuppressionList.id.desc()).all()

@router.post("/api/suppression", response_model=SuppressionResponse, status_code=status.HTTP_201_CREATED)
def add_suppression(
    supp_in: SuppressionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "reviewer"]))
):
    entry = add_suppression_entry(
        db=db,
        email=supp_in.email,
        reason=supp_in.reason,
        notes=supp_in.notes,
        added_by=current_user.email
    )

    log_audit(
        db,
        actor_email=current_user.email,
        action="SUPPRESSION_ADD",
        object_type="SUPPRESSION",
        object_id=str(entry.id),
        details=f"Suppressed {entry.email} (Reason: {entry.reason})",
        ip_address=request.client.host if request.client else None
    )

    return entry

@router.post("/unsubscribe/{token}", response_model=UnsubscribeResponse)
@router.post("/api/unsubscribe/{token}", response_model=UnsubscribeResponse)
@router.post("/api/compliance/unsubscribe/{token}", response_model=UnsubscribeResponse)
def process_unsubscribe(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Validates cryptographic signed, expiring unsubscribe token and immediately
    adds the email to the global suppression list.
    """
    email = verify_unsubscribe_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired unsubscribe token."
        )

    # Immediately add to suppression list
    entry = add_suppression_entry(
        db=db,
        email=email,
        reason="unsubscribed",
        notes="Recipient opted out via cryptographically signed one-click unsubscribe token.",
        added_by="public_unsubscribe_link"
    )

    log_audit(
        db,
        actor_email=email,
        action="UNSUBSCRIBE",
        object_type="SUPPRESSION",
        object_id=str(entry.id),
        details=f"Email '{email}' opted out via signed token. Added to global suppression list.",
        ip_address=request.client.host if request.client else None
    )

    return UnsubscribeResponse(
        success=True,
        message=f"Email address '{email}' has been successfully unsubscribed and placed on our global suppression list.",
        email=email
    )

