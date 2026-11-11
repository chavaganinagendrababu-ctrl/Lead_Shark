from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class LeadBase(BaseModel):
    company_name: str
    contact_name: str
    job_title: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    website: Optional[str] = None
    sector: Optional[str] = "Other"
    region: Optional[str] = None
    source_type: Optional[str] = "manual"
    source_url: Optional[str] = None
    lawful_basis_note: Optional[str] = "Legitimate interest for B2B commercial outreach"

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    job_title: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    sector: Optional[str] = None
    region: Optional[str] = None
    lead_status: Optional[str] = None
    lawful_basis_note: Optional[str] = None

class LeadResponse(LeadBase):
    id: int
    collection_date: datetime
    email_verification_status: str
    verification_details: Optional[str] = None
    lead_status: str
    classification_confidence: float
    classification_reason: Optional[str] = None
    last_contacted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LeadPagination(BaseModel):
    items: List[LeadResponse]
    total: int
    page: int
    size: int
    pages: int

class LeadVerifyResult(BaseModel):
    lead_id: int
    email: str
    status: str # valid, invalid, risky, unknown
    details: str
    mx_records_found: bool
