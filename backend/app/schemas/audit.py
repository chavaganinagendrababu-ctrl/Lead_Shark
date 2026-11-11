from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class AuditLogResponse(BaseModel):
    id: int
    actor_email: str
    action: str
    object_type: str
    object_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class AuditLogPagination(BaseModel):
    items: List[AuditLogResponse]
    total: int
    page: int
    size: int
