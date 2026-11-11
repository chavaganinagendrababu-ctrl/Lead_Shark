import sys
import enum
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum

# Ensure backend root is on sys.path if run directly as a script
backend_root = str(Path(__file__).resolve().parent.parent.parent)
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    REVIEWER = "reviewer"
    SALES = "sales"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.SALES.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

if __name__ == "__main__":
    print("=" * 55)
    print("         LEAD SHARK - User SQLAlchemy Model        ")
    print("=" * 55)
    print(f"Table Name:  {User.__tablename__}")
    print("Columns:")
    for col in User.__table__.columns:
        print(f"  - {col.name:<18} ({col.type})")
    print("\nSupported Roles:")
    for role in UserRole:
        print(f"  - {role.value}")
    print("=" * 55)
    print("Model loaded and validated successfully.")
