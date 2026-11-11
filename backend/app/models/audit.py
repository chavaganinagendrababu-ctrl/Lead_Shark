from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_email = Column(String(255), index=True, nullable=False)
    action = Column(String(100), index=True, nullable=False) # LOGIN, LEAD_CREATE, LEAD_UPDATE, LEAD_DELETE, CSV_IMPORT, CAMPAIGN_CREATE, CAMPAIGN_APPROVE, CAMPAIGN_UPDATE, SUPPRESSION_ADD, UNSUBSCRIBE
    object_type = Column(String(100), index=True, nullable=False) # USER, LEAD, CAMPAIGN, SUPPRESSION, DISCOVERY
    object_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)

