from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base

class SuppressionList(Base):
    __tablename__ = "suppression_list"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    domain = Column(String(255), index=True, nullable=True)
    reason = Column(String(100), nullable=False) # unsubscribed, hard_bounce, spam_complaint, manual_suppression, data_deletion
    notes = Column(Text, nullable=True)
    added_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

