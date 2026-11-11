from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.database import Base

class DiscoveryJob(Base):
    __tablename__ = "discovery_jobs"

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(100), nullable=False) # csv_import, manual, partner_api
    source_name = Column(String(255), nullable=True)
    status = Column(String(50), default="running", nullable=False) # running, completed, failed
    total_discovered = Column(Integer, default=0, nullable=False)
    total_imported = Column(Integer, default=0, nullable=False)
    total_rejected = Column(Integer, default=0, nullable=False)
    summary_note = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

