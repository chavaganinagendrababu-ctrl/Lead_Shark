from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, Token, UserResponse
from app.security.auth import verify_password, create_access_token, get_current_user
from app.security.rate_limiter import auth_rate_limiter
from app.services.audit import log_audit

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(login_req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    auth_rate_limiter.check_rate_limit(request)
    
    user = db.query(User).filter(User.email == login_req.email.lower().strip()).first()
    if not user or not verify_password(login_req.password, user.hashed_password):
        # Log failed attempt
        log_audit(
            db,
            actor_email=login_req.email,
            action="LOGIN_FAILED",
            object_type="USER",
            details="Invalid email or password",
            ip_address=request.client.host if request.client else None
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is disabled")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id},
        expires_delta=access_token_expires
    )

    log_audit(
        db,
        actor_email=user.email,
        action="LOGIN_SUCCESS",
        object_type="USER",
        object_id=str(user.id),
        details=f"User logged in with role: {user.role}",
        ip_address=request.client.host if request.client else None
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
