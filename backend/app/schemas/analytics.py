from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class SectorStat(BaseModel):
    sector: str
    count: int

class RegionStat(BaseModel):
    region: str
    count: int

class RecentLeadStat(BaseModel):
    id: int
    company_name: str
    contact_name: str
    email: str
    sector: str
    lead_status: str
    email_verification_status: str

class DashboardStats(BaseModel):
    total_leads: int
    verified_leads: int
    pending_review: int
    approved_leads: int
    total_campaigns: int
    active_campaigns: int
    suppressed_leads: int
    invalid_emails: int
    sector_distribution: List[SectorStat]
    region_distribution: List[RegionStat]
    recent_leads: List[RecentLeadStat]
    recent_activities: List[Dict[str, Any]]
