import sys
import os
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = str(Path(__file__).resolve().parent.parent.parent)
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from sqlalchemy import func
from app.config import settings
from app.database import SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.security.auth import get_password_hash, verify_password

def recover_admin(email: str = None, password: str = None, name: str = None):
    """
    Secure Admin Account Recovery Script.
    Ensures that the platform administrator account exists, is active,
    and has a valid bcrypt-hashed password.
    """
    admin_email = (email or settings.ADMIN_EMAIL).lower().strip()
    admin_pass = password or settings.ADMIN_PASSWORD
    admin_name = name or settings.ADMIN_NAME

    print("=" * 60)
    print("      LEAD SHARK - SECURE ADMIN RECOVERY UTILITY")
    print("=" * 60)
    print(f"Target Admin Email: {admin_email}")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(func.lower(func.trim(User.email)) == admin_email).first()
        hashed = get_password_hash(admin_pass)

        if not user:
            print("[INFO] Admin account does not exist. Creating new Admin record...")
            user = User(
                email=admin_email,
                full_name=admin_name,
                hashed_password=hashed,
                role=UserRole.ADMIN.value,
                is_active=True
            )
            db.add(user)
        else:
            print(f"[INFO] Existing Admin record found (ID: {user.id}). Updating credentials and active status...")
            user.email = admin_email
            user.full_name = admin_name
            user.hashed_password = hashed
            user.role = UserRole.ADMIN.value
            user.is_active = True

        db.commit()
        db.refresh(user)

        # Verification test
        is_valid = verify_password(admin_pass, user.hashed_password)
        print("=" * 60)
        if is_valid:
            print(f"[SUCCESS] Admin account '{user.email}' is ACTIVE and verified.")
            print(f"[STATUS] Role: {user.role} | Active: {user.is_active} | User ID: {user.id}")
            print("[INFO] Authentication credentials are ready for use.")
        else:
            print("[ERROR] Password verification check failed unexpectedly.")
            sys.exit(1)
        print("=" * 60)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Database operation failed: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    recover_admin()
