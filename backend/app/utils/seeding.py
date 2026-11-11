from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.config import settings
from app.models.user import User, UserRole
from app.models.lead import Lead
from app.models.compliance import SuppressionList
from app.models.campaign import Campaign
from app.models.audit import AuditLog
from app.security.auth import get_password_hash, verify_password

def seed_database(db: Session):
    """Initializes development users, demo leads, compliance list, and sample campaigns."""
    # 1. Seed & Sync Users (ensures Admin, Reviewer, and Sales accounts are active and password-synced)
    def sync_user(email: str, name: str, password: str, role: str) -> User:
        clean_email = email.lower().strip()
        user = db.query(User).filter(func.lower(func.trim(User.email)) == clean_email).first()
        if not user:
            user = User(
                email=clean_email,
                full_name=name,
                hashed_password=get_password_hash(password),
                role=role,
                is_active=True
            )
            db.add(user)
            db.flush()
        else:
            # Sync existing user record: ensure active status, role, and email formatting
            user.email = clean_email
            user.full_name = name
            user.role = role
            user.is_active = True
            # Secure Account Recovery: If the stored password hash does not verify against
            # the current configured password, safely rehash and update it.
            if not verify_password(password, user.hashed_password):
                user.hashed_password = get_password_hash(password)
            db.flush()
        return user

    admin = sync_user(settings.ADMIN_EMAIL, settings.ADMIN_NAME, settings.ADMIN_PASSWORD, UserRole.ADMIN.value)
    reviewer = sync_user(settings.REVIEWER_EMAIL, settings.REVIEWER_NAME, settings.REVIEWER_PASSWORD, UserRole.REVIEWER.value)
    sales = sync_user(settings.SALES_EMAIL, settings.SALES_NAME, settings.SALES_PASSWORD, UserRole.SALES.value)
    
    db.commit()
    db.refresh(admin)
    db.refresh(reviewer)
    db.refresh(sales)

    # 2. Seed Suppression List
    suppressions = [
        {"email": "optout@competitorcorp.com", "domain": "competitorcorp.com", "reason": "unsubscribed", "notes": "Recipient opted out via web link"},
        {"email": "bounce@deadserver-demo.net", "domain": "deadserver-demo.net", "reason": "hard_bounce", "notes": "550 User not found hard bounce"},
        {"email": "privacy@gdpr-request-example.org", "domain": "gdpr-request-example.org", "reason": "data_deletion", "notes": "Article 17 GDPR erasure request"}
    ]
    for s in suppressions:
        if not db.query(SuppressionList).filter(SuppressionList.email == s["email"]).first():
            entry = SuppressionList(
                email=s["email"],
                domain=s["domain"],
                reason=s["reason"],
                notes=s["notes"],
                added_by="system_seeder"
            )
            db.add(entry)

    # 3. Seed Demo Leads (Clearly labeled as demo/sample in source_type)
    demo_leads = [
        {
            "company_name": "Apex Cloud Systems",
            "contact_name": "Sarah Jenkins",
            "job_title": "VP of Engineering",
            "email": "sarah.jenkins@apexcloudsystems.demo",
            "phone": "+1-555-0192",
            "website": "https://apexcloudsystems.demo",
            "sector": "Information Technology",
            "region": "North America",
            "source_type": "sample_demo_record",
            "source_url": "Demo Seeder",
            "email_verification_status": "valid",
            "verification_details": "Simulated MX host verified. Syntax valid.",
            "lead_status": "approved",
            "classification_confidence": 0.95,
            "classification_reason": "Matched tech, cloud, systems keywords."
        },
        {
            "company_name": "BioHealth Therapeutics",
            "contact_name": "Dr. Marcus Chen",
            "job_title": "Chief Medical Officer",
            "email": "mchen@biohealththerapeutics.demo",
            "phone": "+1-555-0144",
            "website": "https://biohealththerapeutics.demo",
            "sector": "Healthcare",
            "region": "North America",
            "source_type": "sample_demo_record",
            "source_url": "Demo Seeder",
            "email_verification_status": "valid",
            "verification_details": "Simulated MX host verified. Syntax valid.",
            "lead_status": "approved",
            "classification_confidence": 0.90,
            "classification_reason": "Matched bio, health, medical keywords."
        },
        {
            "company_name": "Vanguard Capital Partners",
            "contact_name": "Elena Rostova",
            "job_title": "Managing Director",
            "email": "elena.r@vanguardcp.demo",
            "phone": "+44-20-7946-0912",
            "website": "https://vanguardcp.demo",
            "sector": "Finance",
            "region": "Europe",
            "source_type": "sample_demo_record",
            "source_url": "Demo Seeder",
            "email_verification_status": "unknown",
            "verification_details": "Verification pending.",
            "lead_status": "pending_review",
            "classification_confidence": 0.85,
            "classification_reason": "Matched capital, finance keywords."
        },
        {
            "company_name": "Precision Automation Dynamics",
            "contact_name": "Klaus Weber",
            "job_title": "Head of Operations",
            "email": "klaus.weber@precisionautomation.demo",
            "phone": "+49-89-6372-881",
            "website": "https://precisionautomation.demo",
            "sector": "Manufacturing",
            "region": "Europe",
            "source_type": "sample_demo_record",
            "source_url": "Demo Seeder",
            "email_verification_status": "valid",
            "verification_details": "Simulated MX host verified. Syntax valid.",
            "lead_status": "approved",
            "classification_confidence": 0.88,
            "classification_reason": "Matched automation, industrial keywords."
        },
        {
            "company_name": "OmniRetail Global",
            "contact_name": "Chloe Vance",
            "job_title": "E-Commerce Director",
            "email": "chloe.vance@omniretail.demo",
            "phone": "+1-555-0188",
            "website": "https://omniretail.demo",
            "sector": "Retail",
            "region": "North America",
            "source_type": "sample_demo_record",
            "source_url": "Demo Seeder",
            "email_verification_status": "risky",
            "verification_details": "Role-adjacent mailbox detected.",
            "lead_status": "new",
            "classification_confidence": 0.80,
            "classification_reason": "Matched retail, ecommerce keywords."
        }
    ]

    for lead_data in demo_leads:
        if not db.query(Lead).filter(Lead.email == lead_data["email"]).first():
            new_lead = Lead(**lead_data, collection_date=datetime.now(timezone.utc))
            db.add(new_lead)

    # 4. Seed Sample Campaign
    if not db.query(Campaign).first():
        campaign = Campaign(
            name="Q4 Enterprise Cloud Infrastructure Intro",
            subject="Streamlining infrastructure for {{company}}",
            body_template="Hi {{first_name}},\n\nI noticed the impressive work {{company}} is delivering in the {{sector}} space.\n\nWe help technical leaders modernize their workflows with zero compliance friction.\n\nBest regards,\nAlex Vance\nLead Shark Outreach",
            sector="Information Technology",
            target_audience_count=1,
            status="draft",
            daily_limit=50,
            created_by_id=sales.id
        )
        db.add(campaign)

    # 5. Seed Audit Log Entry
    if not db.query(AuditLog).first():
        log = AuditLog(
            actor_email=settings.ADMIN_EMAIL,
            action="SYSTEM_INITIALIZED",
            object_type="SYSTEM",
            object_id="0",
            details="Lead Shark security parameters, default roles, and compliance filters seeded successfully.",
            ip_address="127.0.0.1"
        )
        db.add(log)

    db.commit()

