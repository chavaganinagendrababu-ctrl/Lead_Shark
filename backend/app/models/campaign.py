from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body_template = Column(Text, nullable=False)
    sector = Column(String(100), nullable=True) # Target sector or All
    target_audience_count = Column(Integer, default=0)
    status = Column(String(50), default="draft", nullable=False) # draft, pending_approval, approved, paused, completed
    daily_limit = Column(Integer, default=50, nullable=False)
    
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    creator = relationship("User", foreign_keys=[created_by_id])
    approver = relationship("User", foreign_keys=[approved_by_id])
    steps = relationship("CampaignStep", back_populates="campaign", cascade="all, delete-orphan")
    approvals = relationship("CampaignApproval", back_populates="campaign", cascade="all, delete-orphan")

class CampaignStep(Base):
    __tablename__ = "campaign_steps"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    step_order = Column(Integer, default=1, nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    delay_days = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    campaign = relationship("Campaign", back_populates="steps")

class CampaignApproval(Base):
    __tablename__ = "campaign_approvals"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False) # submitted, approved, rejected, reset
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    campaign = relationship("Campaign", back_populates="approvals")
    reviewer = relationship("User")

