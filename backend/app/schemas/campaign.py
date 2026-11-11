from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class CampaignBase(BaseModel):
    name: str
    subject: str
    body_template: str
    sector: Optional[str] = "All"
    daily_limit: Optional[int] = 50

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    body_template: Optional[str] = None
    sector: Optional[str] = None
    daily_limit: Optional[int] = None
    status: Optional[str] = None

class CampaignApprovalRequest(BaseModel):
    action: str # approve, reject
    notes: Optional[str] = None

class CampaignPreviewResponse(BaseModel):
    campaign_id: int
    subject: str
    rendered_body: str
    recipient_email: str
    first_name: str
    company: str
    sector: str
    unsubscribe_url: str

class CampaignResponse(CampaignBase):
    id: int
    target_audience_count: int
    status: str
    created_by_id: int
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CampaignEligibilityResponse(BaseModel):
    campaign_id: int
    eligible_count: int
    suppressed_count: int
    unapproved_leads_count: int
    unverified_leads_count: int
    is_campaign_approved: bool

