import io
import sys
import os
import json

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, Base, engine
from app.models import *
from app.security.auth import get_password_hash, create_unsubscribe_token
from app.utils.seeding import seed_database

# Ensure database tables and initial seed data are initialized
Base.metadata.create_all(bind=engine)
_seed_db = SessionLocal()
try:
    seed_database(_seed_db)
finally:
    _seed_db.close()

client = TestClient(app, raise_server_exceptions=True)

results = {}

def log_test(category, name, passed, details=""):
    results[f"{category}::{name}"] = {"passed": passed, "details": details}
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {category} - {name}: {details}")

print("==================================================")
print("     STARTING LIVE PHASE 4 EXECUTION SUITE        ")
print("==================================================")

# ----------------------------------------------------
# Health & Docs
# ----------------------------------------------------
res = client.get("/health")
log_test("System", "Health Check", res.status_code == 200 and res.json()["status"] == "healthy", f"Status: {res.status_code}")

res = client.get("/docs")
log_test("System", "Swagger Documentation", res.status_code == 200, f"Status: {res.status_code}")

# ----------------------------------------------------
# Test 8: Authentication and Security
# ----------------------------------------------------
# Valid login Admin
res_admin = client.post("/api/auth/login", json={"email": "admin@leadshark.io", "password": "AdminLeadShark2026!"})
admin_token = res_admin.json().get("access_token")
log_test("Auth", "Admin Login", res_admin.status_code == 200 and admin_token is not None, "Token issued")

# Valid login Reviewer
res_rev = client.post("/api/auth/login", json={"email": "reviewer@leadshark.io", "password": "ReviewerLeadShark2026!"})
reviewer_token = res_rev.json().get("access_token")
log_test("Auth", "Reviewer Login", res_rev.status_code == 200 and reviewer_token is not None, "Token issued")

# Valid login Sales
res_sales = client.post("/api/auth/login", json={"email": "sales@leadshark.io", "password": "SalesLeadShark2026!"})
sales_token = res_sales.json().get("access_token")
log_test("Auth", "Sales Login", res_sales.status_code == 200 and sales_token is not None, "Token issued")

# Invalid login
res_bad = client.post("/api/auth/login", json={"email": "admin@leadshark.io", "password": "WrongPassword"})
log_test("Auth", "Invalid Credentials Rejected", res_bad.status_code == 401, "Returned 401")

# Protected endpoint without token
res_prot = client.get("/api/dashboard/stats")
log_test("Auth", "Protected Endpoint Blocks Unauthenticated", res_prot.status_code == 401, "Returned 401")

# Invalid token
res_inv_tok = client.get("/api/dashboard/stats", headers={"Authorization": "Bearer bogus_token_123"})
log_test("Auth", "Invalid Token Rejected", res_inv_tok.status_code == 401, "Returned 401")

# Password hashing verification in DB
db = SessionLocal()
admin_u = db.query(User).filter(User.email == "admin@leadshark.io").first()
has_bcrypt = admin_u and admin_u.hashed_password.startswith("$2")
log_test("Security", "Password Hashing with Bcrypt", has_bcrypt, "Hashed with salted rounds in DB")

# Role permissions: Sales cannot delete or view audit logs
res_audit_sales = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {sales_token}"})
log_test("Security", "Role Permission: Sales Blocked From Audit Logs", res_audit_sales.status_code == 403, "Returned 403 Forbidden")

admin_headers = {"Authorization": f"Bearer {admin_token}"}
sales_headers = {"Authorization": f"Bearer {sales_token}"}
reviewer_headers = {"Authorization": f"Bearer {reviewer_token}"}

# ----------------------------------------------------
# Test 1: Dashboard
# ----------------------------------------------------
res_dash = client.get("/api/dashboard/stats", headers=admin_headers)
dash_data = res_dash.json()
db_lead_count = db.query(Lead).count()
log_test("Dashboard", "Stats Loaded", res_dash.status_code == 200, f"Total Leads in DB: {db_lead_count}")
log_test("Dashboard", "Data Accuracy", dash_data["total_leads"] == db_lead_count, f"Dashboard reports {dash_data['total_leads']}, DB has {db_lead_count}")

# ----------------------------------------------------
# Test 2: Lead Management (Required sample leads)
# ----------------------------------------------------
# Missing fields validation
res_missing = client.post("/api/leads", json={"company_name": "ABC Tech"}, headers=admin_headers)
log_test("Leads", "Validate Missing Required Fields", res_missing.status_code == 422, "Returned 422 Unprocessable Entity")

# Invalid email format validation
res_inv_email = client.post("/api/leads", json={
    "company_name": "ABC Tech",
    "contact_name": "Test User",
    "email": "not-an-email"
}, headers=admin_headers)
log_test("Leads", "Validate Invalid Email Format", res_inv_email.status_code == 422, "Pydantic EmailStr validation caught format")

# Clean up any previous test leads if they exist
existing_rahul = db.query(Lead).filter(Lead.email == "rahul@example.com").first()
if existing_rahul:
    db.delete(existing_rahul)
existing_priya = db.query(Lead).filter(Lead.email == "priya@example.org").first()
if existing_priya:
    db.delete(existing_priya)
db.commit()

# Create Lead 1: Rahul Kumar
lead1_data = {
    "company_name": "ABC Technologies",
    "contact_name": "Rahul Kumar",
    "email": "rahul@example.com",
    "sector": "Information Technology",
    "region": "India"
}
res_lead1 = client.post("/api/leads", json=lead1_data, headers=admin_headers)
lead1_id = res_lead1.json().get("id")
log_test("Leads", "Add Lead 1 (Rahul Kumar)", res_lead1.status_code == 201, f"Lead ID: {lead1_id}")

# Create Lead 2: Priya Sharma
lead2_data = {
    "company_name": "XYZ Solutions",
    "contact_name": "Priya Sharma",
    "email": "priya@example.org",
    "sector": "Information Technology",
    "region": "India"
}
res_lead2 = client.post("/api/leads", json=lead2_data, headers=admin_headers)
lead2_id = res_lead2.json().get("id")
log_test("Leads", "Add Lead 2 (Priya Sharma)", res_lead2.status_code == 201, f"Lead ID: {lead2_id}")

# Duplicate detection
res_dup = client.post("/api/leads", json=lead1_data, headers=admin_headers)
log_test("Leads", "Duplicate Lead Rejection", res_dup.status_code == 400 and "already exists" in res_dup.json()["detail"].lower(), "Duplicate rejected with 400")

# View and Search leads
res_search = client.get("/api/leads?search=Rahul", headers=admin_headers)
found_rahul = any(l["email"] == "rahul@example.com" for l in res_search.json()["items"])
log_test("Leads", "Search Leads", res_search.status_code == 200 and found_rahul, "Found Rahul Kumar by query")

# Edit lead
res_edit = client.put(f"/api/leads/{lead1_id}", json={"job_title": "Senior Solutions Architect", "lead_status": "approved"}, headers=admin_headers)
log_test("Leads", "Edit Lead", res_edit.status_code == 200 and res_edit.json()["job_title"] == "Senior Solutions Architect", "Updated job title and status to approved")

# ----------------------------------------------------
# Test 3: CSV Upload
# ----------------------------------------------------
csv_content = (
    "company_name,contact_name,job_title,email,sector,region\n"
    "Valid Ingestion Co,Vikram Singh,CTO,vikram.singh@validtech.demo,Information Technology,India\n"
    "Valid Ingestion Co,Vikram Duplicate,CTO,vikram.singh@validtech.demo,Information Technology,India\n" # Duplicate in file
    "Suppressed Lead Co,Opted Out Person,VP,optout@competitorcorp.com,Finance,North America\n" # Globally Suppressed
    "Malformed Email Co,Broken User,Dev,brokenemailformat,Retail,Asia\n" # Invalid email format
    ",Missing Company,Manager,missingco@example.com,Healthcare,Asia\n" # Missing required company
)
files = {"file": ("test_import.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
res_csv = client.post("/api/leads/import", files=files, headers=admin_headers)
csv_res_data = res_csv.json()
log_test("CSV Upload", "Batch Import Processing", res_csv.status_code == 200 and csv_res_data["success"] is True, f"Imported: {csv_res_data.get('imported')}, Duplicates: {csv_res_data.get('duplicates')}, Suppressed: {csv_res_data.get('suppressed')}, Invalid: {csv_res_data.get('invalid')}")

# ----------------------------------------------------
# Test 4: Email Validation
# ----------------------------------------------------
from app.services.verification import verify_email_address
val_valid = verify_email_address("test.engineer@google.com")
log_test("Email Validation", "Valid Syntax & Host", val_valid["status"] in ["valid", "unknown"], f"Status: {val_valid['status']}")

val_invalid_syntax = verify_email_address("invalid..syntax@")
log_test("Email Validation", "Invalid Syntax Format", val_invalid_syntax["status"] == "invalid", f"Status: {val_invalid_syntax['status']} - {val_invalid_syntax['details']}")

val_disposable = verify_email_address("disposable@mailinator.com")
log_test("Email Validation", "Disposable Domain Rejected", val_disposable["status"] == "invalid" and "disposable" in val_disposable["details"].lower(), f"Status: {val_disposable['status']}")

# ----------------------------------------------------
# Test 5: Lead Classification
# ----------------------------------------------------
from app.services.classification import classifier_service
clf_it = classifier_service.classify("CloudOps Software Solutions", "https://cloudops.tech", "DevOps Engineer")
log_test("Classification", "IT Services Classification", clf_it["sector"] == "Information Technology" and clf_it["confidence"] >= 0.70, f"Sector: {clf_it['sector']}, Confidence: {clf_it['confidence']}")

clf_health = classifier_service.classify("Apex Medical & Healthcare Clinic", "https://apexmedical.org", "Physician")
log_test("Classification", "Healthcare Classification", clf_health["sector"] == "Healthcare", f"Sector: {clf_health['sector']}, Confidence: {clf_health['confidence']}")

clf_finance = classifier_service.classify("Venture Capital Investment Partners", "https://venturecapital.org", "Managing Partner")
log_test("Classification", "Finance Classification", clf_finance["sector"] == "Finance", f"Sector: {clf_finance['sector']}, Confidence: {clf_finance['confidence']}")

clf_unknown = classifier_service.classify("XYZ Ambiguous Corp 999", "", "")
log_test("Classification", "Unknown Business (Review Required)", clf_unknown["sector"] == "Other" and clf_unknown["needs_review"] is True, "Marked as Other with needs_review=True")

# ----------------------------------------------------
# Test 6: Campaign Management
# ----------------------------------------------------
camp_payload = {
    "name": "Q4 Enterprise Infrastructure Outreach",
    "subject": "Modernizing systems for {{company}}",
    "body_template": "Hello {{first_name}},\n\nI noticed {{company}}'s leadership in {{sector}}.\n\nBest,\nLead Shark",
    "sector": "Information Technology",
    "daily_limit": 50
}
res_camp = client.post("/api/campaigns", json=camp_payload, headers=sales_headers)
camp_id = res_camp.json().get("id")
log_test("Campaigns", "Create Campaign Draft", res_camp.status_code == 201 and res_camp.json()["status"] == "draft", f"Campaign ID: {camp_id}")

# Preview campaign
res_prev = client.get(f"/api/campaigns/{camp_id}/preview", headers=sales_headers)
prev_data = res_prev.json()
log_test("Campaigns", "Preview Campaign with Merge Tags", res_prev.status_code == 200 and "unsubscribe" in prev_data["rendered_body"].lower(), "Rendered tags and signed unsubscribe link")

# Verify creator cannot self-approve (Four-Eyes governance)
res_self_app = client.post(f"/api/campaigns/{camp_id}/approve", json={"action": "approve"}, headers=sales_headers)
log_test("Campaigns", "Creator Cannot Self-Approve", res_self_app.status_code == 403, "Blocked by RBAC / Four-Eyes policy")

# Reviewer approves campaign
res_rev_app = client.post(f"/api/campaigns/{camp_id}/approve", json={"action": "approve", "notes": "Approved by reviewer"}, headers=reviewer_headers)
log_test("Campaigns", "Reviewer Approval Workflow", res_rev_app.status_code == 200 and res_rev_app.json()["status"] == "approved", "Approved by reviewer account")

# Editing approved campaign resets approval
res_camp_edit = client.put(f"/api/campaigns/{camp_id}", json={"subject": "Updated subject line for {{company}}"}, headers=sales_headers)
log_test("Campaigns", "Template Edit Revokes Approval", res_camp_edit.status_code == 200 and res_camp_edit.json()["status"] == "pending_approval", "Approval revoked to pending_approval")

# ----------------------------------------------------
# Test 7: Suppression List
# ----------------------------------------------------
test_supp_email = "optout-phase4-test@enterprise.org"
res_supp_add = client.post("/api/suppression", json={
    "email": test_supp_email,
    "reason": "manual_suppression",
    "notes": "Added during Phase 4 live testing"
}, headers=reviewer_headers)
log_test("Suppression", "Add Suppressed Email", res_supp_add.status_code == 201, f"Added {test_supp_email}")

# Attempt to add duplicate suppression entry
res_supp_dup = client.post("/api/suppression", json={
    "email": test_supp_email,
    "reason": "data_deletion",
    "notes": "Article 17 GDPR erasure"
}, headers=reviewer_headers)
log_test("Suppression", "Duplicate Suppression Graceful Update", res_supp_dup.status_code == 201 and res_supp_dup.json()["reason"] == "data_deletion", "Updated existing suppression without collision")

# Verify suppressed contact cannot be added as lead
res_blocked_lead = client.post("/api/leads", json={
    "company_name": "Blocked Company",
    "contact_name": "Blocked Person",
    "email": test_supp_email
}, headers=admin_headers)
log_test("Suppression", "Suppressed Email Blocked from Leads", res_blocked_lead.status_code == 400 and "suppression" in res_blocked_lead.json()["detail"].lower(), "Blocked with 400")

# Test signed token unsubscribe
unsub_tok = create_unsubscribe_token("user-optout@commercial.com")
res_unsub = client.post(f"/unsubscribe/{unsub_tok}")
log_test("Suppression", "Signed Token Unsubscribe Endpoint", res_unsub.status_code == 200 and res_unsub.json()["success"] is True, "Token verified and contact suppressed")

# ----------------------------------------------------
# Clean up temporary test records
# ----------------------------------------------------
del_lead1 = client.delete(f"/api/leads/{lead1_id}", headers=admin_headers)
del_lead2 = client.delete(f"/api/leads/{lead2_id}", headers=admin_headers)
log_test("Cleanup", "Delete Test Leads (Rahul & Priya)", del_lead1.status_code == 200 and del_lead2.status_code == 200, "Cleaned up test prospect records")

# Clean up vikram lead from CSV
vikram = db.query(Lead).filter(Lead.email == "vikram.singh@validtech.demo").first()
if vikram:
    db.delete(vikram)
# Clean up test campaign
camp_obj = db.query(Campaign).filter(Campaign.id == camp_id).first()
if camp_obj:
    db.delete(camp_obj)
db.commit()
db.close()

total_tests = len(results)
passed_tests = sum(1 for r in results.values() if r["passed"])
failed_tests = total_tests - passed_tests

print("==================================================")
print(f"   EXECUTION COMPLETE: {passed_tests}/{total_tests} PASSED ({failed_tests} FAILED)")
print("==================================================")

