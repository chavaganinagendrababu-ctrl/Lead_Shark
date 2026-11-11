from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User, UserRole
from app.models.lead import Lead
from app.models.compliance import SuppressionList
from app.models.campaign import Campaign
from app.models.audit import AuditLog
from app.security.auth import get_password_hash

def seed_database(db: Session):
    """Initializes development users, demo leads, compliance list, and sample campaigns."""
    # 1. Seed Users
    admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            email=settings.ADMIN_EMAIL,
            full_name=settings.ADMIN_NAME,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            role=UserRole.ADMIN.value,
            is_active=True
        )
        db.add(admin)

    reviewer = db.query(User).filter(User.email == settings.REVIEWER_EMAIL).first()
    if not reviewer:
        reviewer = User(
            email=settings.REVIEWER_EMAIL,
            full_name=settings.REVIEWER_NAME,
            hashed_password=get_password_hash(settings.REVIEWER_PASSWORD),
            role=UserRole.REVIEWER.value,
            is_active=True
        )
        db.add(reviewer)

    sales = db.query(User).filter(User.email == settings.SALES_EMAIL).first()
    if not sales:
        sales = User(
            email=settings.SALES_EMAIL,
            full_name=settings.SALES_NAME,
            hashed_password=get_password_hash(settings.SALES_PASSWORD),
            role=UserRole.SALES.value,
            is_active=True
        )
        db.add(sales)
    
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

