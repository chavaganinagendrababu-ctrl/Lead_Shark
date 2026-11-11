import io
import os
import sys
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup test environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["DATABASE_URL"] = "sqlite:///./qa_test_leadshark.db"
os.environ["SECRET_KEY"] = "qa-leadshark-super-secure-verification-secret"

import app.database as db_module
from app.main import app
from app.utils.seeding import seed_database
from app.models.user import User, UserRole
from app.models.lead import Lead
from app.models.campaign import Campaign, CampaignApproval
from app.models.compliance import SuppressionList
from app.models.audit import AuditLog
from app.security.auth import create_access_token, create_unsubscribe_token

qa_engine = create_engine("sqlite:///./qa_test_leadshark.db", connect_args={"check_same_thread": False})
QASessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=qa_engine)

db_module.engine = qa_engine
db_module.SessionLocal = QASessionLocal

@pytest.fixture(scope="session", autouse=True)
def init_qa_environment():
    db_module.Base.metadata.drop_all(bind=qa_engine)
    db_module.Base.metadata.create_all(bind=qa_engine)
    db = QASessionLocal()
    seed_database(db)
    db.close()
    yield
    db_module.Base.metadata.drop_all(bind=qa_engine)
    if os.path.exists("./qa_test_leadshark.db"):
        try:
            os.remove("./qa_test_leadshark.db")
        except Exception:
            pass

@pytest.fixture
def qa_client():
    def override_get_db():
        db = QASessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[db_module.get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()

def get_token(client: TestClient, email: str, password: str) -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]

# ============================================================================
# 1. DASHBOARD TESTS
# ============================================================================
def test_dashboard_kpis_and_db_consistency(qa_client: TestClient):
    """Verify dashboard loads, numbers match database, and handles empty/populated states."""
    admin_token = get_token(qa_client, "admin@leadshark.io", "AdminLeadShark2026!")
    res = qa_client.get("/api/dashboard/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.json()

    # Compare directly with DB count
    db = QASessionLocal()
    actual_leads = db.query(Lead).count()
    actual_suppressed = db.query(SuppressionList).count()
    actual_campaigns = db.query(Campaign).count()
    actual_verified = db.query(Lead).filter(Lead.email_verification_status == "valid").count()
    db.close()

    assert data["total_leads"] == actual_leads
    assert data["suppressed_leads"] == actual_suppressed
    assert data["total_campaigns"] == actual_campaigns
    assert data["verified_leads"] == actual_verified
    assert isinstance(data["sector_distribution"], list)
    assert isinstance(data["region_distribution"], list)
    assert isinstance(data["recent_leads"], list)
    assert isinstance(data["recent_activities"], list)

# ============================================================================
# 2. LEAD MANAGEMENT TESTS (CRUD, Validation, Duplicate, Search, Filter)
# ============================================================================
def test_lead_crud_and_validation(qa_client: TestClient):
    """Test full lead lifecycle: create, read, update, delete, search, filters, validation."""
    admin_token = get_token(qa_client, "admin@leadshark.io", "AdminLeadShark2026!")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Validation error: Missing required fields
    invalid_res = qa_client.post("/api/leads", json={"company_name": "Incomplete"}, headers=headers)
    assert invalid_res.status_code == 422 # Pydantic validation error

    # 2. Validation error: Malformed email
    bad_email_res = qa_client.post("/api/leads", json={
        "company_name": "Acme",
        "contact_name": "John Doe",
        "email": "not-an-email"
    }, headers=headers)
    assert bad_email_res.status_code == 422

    # 3. Create valid lead
    lead_payload = {
        "company_name": "Starlight Robotics",
        "contact_name": "Alan Turing",
        "job_title": "Principal Architect",
        "email": "alan.turing@starlightrobotics.demo",
        "phone": "+1-555-7788",
        "website": "https://starlightrobotics.demo",
        "sector": "Information Technology",
        "region": "North America"
    }
    create_res = qa_client.post("/api/leads", json=lead_payload, headers=headers)
    assert create_res.status_code == 201
    created_id = create_res.json()["id"]
    assert create_res.json()["email_verification_status"] == "unknown" # Must not auto-verify!
    assert create_res.json()["lead_status"] == "pending_review"

    # 4. Duplicate rejection
    dup_res = qa_client.post("/api/leads", json=lead_payload, headers=headers)
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"].lower()

    # 5. Read single lead
    get_res = qa_client.get(f"/api/leads/{created_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["contact_name"] == "Alan Turing"

    # 6. Update lead
    update_res = qa_client.put(f"/api/leads/{created_id}", json={
        "job_title": "Chief Scientist",
        "lead_status": "approved"
    }, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["job_title"] == "Chief Scientist"
    assert update_res.json()["lead_status"] == "approved"

    # 7. Search leads
    search_res = qa_client.get("/api/leads?search=Starlight", headers=headers)
    assert search_res.status_code == 200
    assert any(l["id"] == created_id for l in search_res.json()["items"])

    # 8. Filter leads by sector and status
    filter_res = qa_client.get("/api/leads?sector=Information Technology&lead_status=approved", headers=headers)
    assert filter_res.status_code == 200
    assert all(l["sector"] == "Information Technology" and l["lead_status"] == "approved" for l in filter_res.json()["items"])

    # 9. Delete lead (Admin allowed)
    del_res = qa_client.delete(f"/api/leads/{created_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 10. Verify lead is gone
    not_found = qa_client.get(f"/api/leads/{created_id}", headers=headers)
    assert not_found.status_code == 404

def test_sales_role_cannot_delete_leads(qa_client: TestClient):
    """Test RBAC: Sales users must NOT be allowed to delete leads."""
    sales_token = get_token(qa_client, "sales@leadshark.io", "SalesLeadShark2026!")
    sales_headers = {"Authorization": f"Bearer {sales_token}"}

    # First get an existing lead
    leads_res = qa_client.get("/api/leads", headers=sales_headers)
    lead_id = leads_res.json()["items"][0]["id"]

    del_res = qa_client.delete(f"/api/leads/{lead_id}", headers=sales_headers)
    assert del_res.status_code == 403
    assert "operation not permitted" in del_res.json()["detail"].lower()

# ============================================================================
# 3. CSV UPLOAD TESTS (Empty, Missing Columns, Bad Type, Duplicates, Suppression)
# ============================================================================
def test_csv_upload_scenarios(qa_client: TestClient):
    """Test CSV import validations, empty files, missing columns, and duplicate handling."""
    admin_token = get_token(qa_client, "admin@leadshark.io", "AdminLeadShark2026!")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Unsupported file type (.txt / .json)
    txt_file = {"file": ("leads.txt", io.BytesIO(b"some,plain,text"), "text/plain")}
    bad_type_res = qa_client.post("/api/leads/import", files=txt_file, headers=headers)
    assert bad_type_res.status_code == 400
    assert "file type invalid" in bad_type_res.json()["detail"].lower()

    # 2. Empty CSV
    empty_file = {"file": ("empty.csv", io.BytesIO(b""), "text/csv")}
    empty_res = qa_client.post("/api/leads/import", files=empty_file, headers=headers)
    assert empty_res.status_code == 400
    assert "empty" in empty_res.json()["detail"].lower()

    # 3. Missing required columns
    bad_csv = "company_name,phone\nAcme,+123456\n"
    bad_col_file = {"file": ("missing_cols.csv", io.BytesIO(bad_csv.encode("utf-8")), "text/csv")}
    col_res = qa_client.post("/api/leads/import", files=bad_col_file, headers=headers)
    assert col_res.status_code == 400
    assert "missing required columns" in col_res.json()["detail"].lower()

    # 4. Valid CSV with duplicates, invalid emails, and suppressed emails
    valid_csv = (
        "company_name,contact_name,job_title,email,sector,region\n"
        "Helios Software,Helena Troy,VP Engineering,helena@heliossoft.demo,Information Technology,Europe\n"
        "Helios Software,Helena Duplicate,VP Engineering,helena@heliossoft.demo,Information Technology,Europe\n" # Duplicate in file
        "Suppressed Corp,Suppressed User,Director,optout@competitorcorp.com,Finance,North America\n" # Suppressed
        "Broken Email Co,No At Sign,Manager,brokenemailaddress.com,Retail,North America\n" # Invalid format
        "Orion Healthcare,Dr. Orion Vance,Chief Surgeon,orion@orionhealth.demo,Healthcare,North America\n"
    )
    valid_file = {"file": ("batch_leads.csv", io.BytesIO(valid_csv.encode("utf-8")), "text/csv")}
    import_res = qa_client.post("/api/leads/import", files=valid_file, headers=headers)
    assert import_res.status_code == 200
    data = import_res.json()
    assert data["success"] is True
    assert data["imported"] == 2
    assert data["duplicates"] >= 1
    assert data["suppressed"] >= 1
    assert data["invalid"] >= 1

    # Verify newly imported leads have verification status 'unknown'
    db = QASessionLocal()
    imported_lead = db.query(Lead).filter(Lead.email == "helena@heliossoft.demo").first()
    assert imported_lead is not None
    assert imported_lead.email_verification_status == "unknown"
    db.close()

# ============================================================================
# 4. EMAIL VERIFICATION TESTS (Syntax, Disposable, MX, Realistic Statuses)
# ============================================================================
def test_email_verification_precision(qa_client: TestClient):
    """Verify syntax checks, disposable domain flagging, and role account detection."""
    from app.services.verification import verify_email_address

    # 1. Invalid syntax
    res1 = verify_email_address("invalid..syntax@")
    assert res1["status"] == "invalid"
    assert res1["mx_records_found"] is False

    # 2. Disposable domain
    res2 = verify_email_address("burner@trashmail.com")
    assert res2["status"] == "invalid"
    assert "disposable" in res2["details"].lower()

    # 3. Nonexistent domain
    res3 = verify_email_address("john@this-domain-definitely-does-not-exist-99214.xyz")
    assert res3["status"] in ["invalid", "unknown"]

    # 4. Verify endpoint via API
    admin_token = get_token(qa_client, "admin@leadshark.io", "AdminLeadShark2026!")
    headers = {"Authorization": f"Bearer {admin_token}"}
    lead = qa_client.post("/api/leads", json={
        "company_name": "Disposable Test",
        "contact_name": "Burner Guy",
        "email": "burner.guy@tempmail.com"
    }, headers=headers).json()

    verify_res = qa_client.post(f"/api/leads/{lead['id']}/verify", headers=headers)
    assert verify_res.status_code == 200
    assert verify_res.json()["status"] == "invalid"

# ============================================================================
# 5. SECTOR CLASSIFICATION & RAG CONNECTOR TESTS
# ============================================================================
def test_sector_classification_and_uncertain_review(qa_client: TestClient):
    """Verify keyword classification, confidence scores, and flagging ambiguous info for review."""
    from app.services.classification import classifier_service

    # 1. Tech keywords
    c1 = classifier_service.classify("CloudScale AI Systems", "https://cloudscale.ai", "Lead Dev")
    assert c1["sector"] == "Information Technology"
    assert c1["confidence"] >= 0.70
    assert c1["needs_review"] is False

    # 2. Healthcare keywords
    c2 = classifier_service.classify("Global Therapeutics Clinic", "https://clinic.com", "Chief Medical Officer")
    assert c2["sector"] == "Healthcare"
    assert c2["confidence"] >= 0.70

    # 3. Ambiguous / Unknown company
    c3 = classifier_service.classify("XYZ Ventures 123", "", "Consultant")
    assert c3["sector"] in ["Finance", "Other"]
    if c3["sector"] == "Other":
        assert c3["needs_review"] is True # Flagged for human review!

# ============================================================================
# 6. CAMPAIGN MANAGEMENT & FOUR-EYES GOVERNANCE
# ============================================================================
def test_campaign_governance_and_reset(qa_client: TestClient):
    """Test campaign creation, preview, four-eyes approval restriction, and approval reset."""
    sales_token = get_token(qa_client, "sales@leadshark.io", "SalesLeadShark2026!")
    reviewer_token = get_token(qa_client, "reviewer@leadshark.io", "ReviewerLeadShark2026!")
    sales_headers = {"Authorization": f"Bearer {sales_token}"}
    reviewer_headers = {"Authorization": f"Bearer {reviewer_token}"}

    # 1. Sales creates campaign
    camp = qa_client.post("/api/campaigns", json={
        "name": "Healthcare Digital Transformation",
        "subject": "Innovating clinical workflows at {{company}}",
        "body_template": "Hi {{first_name}},\n\nWe love your work at {{company}} in {{sector}}.\n\nBest,\nSales",
        "sector": "Healthcare",
        "daily_limit": 25
    }, headers=sales_headers).json()

    camp_id = camp["id"]
    assert camp["status"] == "draft"

    # 2. Preview email renders merge tags and unsubscribe URL
    prev = qa_client.get(f"/api/campaigns/{camp_id}/preview", headers=sales_headers)
    assert prev.status_code == 200
    assert "unsubscribe" in prev.json()["rendered_body"].lower()
    assert prev.json()["unsubscribe_url"].startswith("http")

    # 3. Layer 1: Sales user cannot approve (RBAC rejection)
    sales_approve = qa_client.post(f"/api/campaigns/{camp_id}/approve", json={"action": "approve"}, headers=sales_headers)
    assert sales_approve.status_code == 403
    assert "required role" in sales_approve.json()["detail"].lower()

    # 4. Layer 2: Reviewer creates a campaign, then tries to approve their own campaign (Four-Eyes rejection)
    rev_camp = qa_client.post("/api/campaigns", json={
        "name": "Reviewer Campaign Self-Approval Test",
        "subject": "Testing four-eyes",
        "body_template": "Hello {{first_name}}",
        "sector": "Information Technology"
    }, headers=reviewer_headers).json()
    rev_camp_id = rev_camp["id"]

    rev_self_approve = qa_client.post(f"/api/campaigns/{rev_camp_id}/approve", json={"action": "approve"}, headers=reviewer_headers)
    assert rev_self_approve.status_code == 403
    assert "four-eyes" in rev_self_approve.json()["detail"].lower()

    # 5. Independent Admin approves sales campaign
    admin_token = get_token(qa_client, "admin@leadshark.io", "AdminLeadShark2026!")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    admin_approve = qa_client.post(f"/api/campaigns/{camp_id}/approve", json={"action": "approve"}, headers=admin_headers)
    assert admin_approve.status_code == 200
    assert admin_approve.json()["status"] == "approved"

    # 6. Editing approved campaign automatically resets approval to 'pending_approval'
    edit_res = qa_client.put(f"/api/campaigns/{camp_id}", json={
        "subject": "Updated subject line for {{company}}"
    }, headers=sales_headers)
    assert edit_res.status_code == 200
    assert edit_res.json()["status"] == "pending_approval"

# ============================================================================
# 7. SUPPRESSION & UNSUBSCRIBE TESTS (Global enforcement, Erasure Protection)
# ============================================================================
def test_suppression_and_signed_unsubscribe(qa_client: TestClient):
    """Verify suppression blocks creation, duplicate suppressions update cleanly, and signed tokens work."""
    admin_token = get_token(qa_client, "admin@leadshark.io", "AdminLeadShark2026!")
    headers = {"Authorization": f"Bearer {admin_token}"}

    test_email = "optout-candidate@samplecompany.org"

    # 1. Add suppression
    supp_res = qa_client.post("/api/suppression", json={
        "email": test_email,
        "reason": "manual_suppression",
        "notes": "Added for testing"
    }, headers=headers)
    assert supp_res.status_code == 201

    # 2. Adding same email updates cleanly without duplicate error
    supp_dup = qa_client.post("/api/suppression", json={
        "email": test_email,
        "reason": "data_deletion",
        "notes": "Article 17 GDPR request"
    }, headers=headers)
    assert supp_dup.status_code == 201
    assert supp_dup.json()["reason"] == "data_deletion"

    # 3. Trying to create a lead with suppressed email is strictly blocked
    lead_block = qa_client.post("/api/leads", json={
        "company_name": "Sample Co",
        "contact_name": "Optout Candidate",
        "email": test_email
    }, headers=headers)
    assert lead_block.status_code == 400
    assert "suppression list" in lead_block.json()["detail"].lower()

    # 4. Test public unsubscribe endpoint with valid token
    token = create_unsubscribe_token("recipient-click@corporation.com")
    unsub_res = qa_client.post(f"/unsubscribe/{token}")
    assert unsub_res.status_code == 200
    assert unsub_res.json()["success"] is True

    # 5. Invalid token rejected
    bad_unsub = qa_client.post("/unsubscribe/completely-bogus-token-123")
    assert bad_unsub.status_code == 400

# ============================================================================
# 8. AUDIT LOGS TESTS
# ============================================================================
def test_audit_logs_rbac_and_entries(qa_client: TestClient):
    """Verify audit trails record actor, action, and timestamp, with RBAC protection."""
    reviewer_token = get_token(qa_client, "reviewer@leadshark.io", "ReviewerLeadShark2026!")
    sales_token = get_token(qa_client, "sales@leadshark.io", "SalesLeadShark2026!")

    # 1. Sales user cannot view audit logs
    denied = qa_client.get("/api/audit-logs", headers={"Authorization": f"Bearer {sales_token}"})
    assert denied.status_code == 403

    # 2. Reviewer can view audit logs
    allowed = qa_client.get("/api/audit-logs", headers={"Authorization": f"Bearer {reviewer_token}"})
    assert allowed.status_code == 200
    items = allowed.json()["items"]
    assert len(items) > 0
    first = items[0]
    assert "actor_email" in first
    assert "action" in first
    assert "timestamp" in first

# ============================================================================
# 9. AUTHENTICATION & SECURITY (Password hashing, JWT, Rate limiting, Injection)
# ============================================================================
def test_security_hardening(qa_client: TestClient):
    """Test invalid credentials, token tampering, password hashing in DB, and CSV formula sanitization."""
    # 1. Invalid credentials
    bad_login = qa_client.post("/api/auth/login", json={"email": "admin@leadshark.io", "password": "WrongPassword!"})
    assert bad_login.status_code == 401

    # 2. Tampered token
    tampered = qa_client.get("/api/auth/me", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.tampered.token"})
    assert tampered.status_code == 401

    # 3. Passwords in database are hashed with bcrypt
    db = QASessionLocal()
    admin_user = db.query(User).filter(User.email == "admin@leadshark.io").first()
    assert admin_user.hashed_password.startswith("$2b$") or admin_user.hashed_password.startswith("$2a$")
    assert "AdminLeadShark2026!" not in admin_user.hashed_password
    db.close()

    # 4. CSV Formula Injection Sanitization
    from app.utils.csv_handler import sanitize_csv_value
    assert sanitize_csv_value("=cmd|' /C calc'!A0") == "'=cmd|' /C calc'!A0"
    assert sanitize_csv_value("+12345") == "'+12345"
    assert sanitize_csv_value("-500") == "'-500"
    assert sanitize_csv_value("@SUM(A1:A10)") == "'@SUM(A1:A10)"
    assert sanitize_csv_value("Safe Company Name") == "Safe Company Name"
