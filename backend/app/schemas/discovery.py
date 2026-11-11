from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class DiscoveryJobCreate(BaseModel):
    source_type: str = "mock_partner_api" # mock_partner_api, csv_import, manual
    source_name: Optional[str] = "Permitted Public B2B Registry (Demo)"
    sector_filter: Optional[str] = "All"
    records_to_discover: Optional[int] = 5

class DiscoveryJobResponse(BaseModel):
    id: int
    source_type: str
    source_name: Optional[str] = None
    status: str
    total_discovered: int
    total_imported: int
    total_rejected: int
    summary_note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

