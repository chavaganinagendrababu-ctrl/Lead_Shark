from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class SuppressionCreate(BaseModel):
    email: EmailStr
    reason: str = "manual_suppression" # unsubscribed, hard_bounce, spam_complaint, manual_suppression, data_deletion
    notes: Optional[str] = None

class SuppressionResponse(BaseModel):
    id: int
    email: str
    domain: Optional[str] = None
    reason: str
    notes: Optional[str] = None
    added_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UnsubscribeRequest(BaseModel):
    token: str
    reason: Optional[str] = "unsubscribed"

class UnsubscribeResponse(BaseModel):
    success: bool
    message: str
    email: Optional[str] = None
