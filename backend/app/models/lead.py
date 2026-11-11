from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    contact_name = Column(String(255), nullable=False, index=True)
    job_title = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(100), nullable=True)
    website = Column(String(500), nullable=True)
    sector = Column(String(100), index=True, default="Other")
    region = Column(String(100), index=True, nullable=True)
    
    # Provenance and Compliance
    source_type = Column(String(100), default="manual", nullable=False) # manual, csv_import, permitted_api
    source_url = Column(String(500), nullable=True)
    collection_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    lawful_basis_note = Column(Text, default="Legitimate interest for B2B commercial outreach", nullable=True)
    
    # Verification & Approval
    email_verification_status = Column(String(50), default="unknown", nullable=False) # valid, invalid, risky, unknown
    verification_details = Column(Text, nullable=True)
    lead_status = Column(String(50), default="new", nullable=False) # new, pending_review, approved, rejected
    
    # Classification Metadata
    classification_confidence = Column(Float, default=0.0)
    classification_reason = Column(String(500), nullable=True)
    
    # Activity Tracking
    last_contacted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

