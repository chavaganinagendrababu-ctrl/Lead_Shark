import sys
import os

# Ensure backend root is on sys.path
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.security.auth import verify_password
from app.utils.seeding import seed_database

def run_tests():
    print("=" * 60)
    print("      RUNNING AUTHENTICATION & ROLE PERMISSION TESTS")
    print("=" * 60)

    # 1. Ensure seeding is executed
    db = SessionLocal()
    seed_database(db)
    db.close()

    client = TestClient(app, raise_server_exceptions=True)

    # TEST 1: Admin Login
    admin_payload = {"email": "admin@leadshark.io", "password": "AdminLeadShark2026!"}
    res_admin = client.post("/api/auth/login", json=admin_payload)
    assert res_admin.status_code == 200, f"Admin login failed: {res_admin.text}"
    admin_token = res_admin.json()["access_token"]
    assert admin_token, "Admin access token is missing"

    me_admin = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert me_admin.status_code == 200
    assert me_admin.json()["role"] == "admin"
    assert me_admin.json()["is_active"] is True
    print("[PASS] Test 1: Admin Login succeeded with valid token and role 'admin'")

    # TEST 2: Reviewer Login
    reviewer_payload = {"email": "reviewer@leadshark.io", "password": "ReviewerLeadShark2026!"}
    res_reviewer = client.post("/api/auth/login", json=reviewer_payload)
    assert res_reviewer.status_code == 200, f"Reviewer login failed: {res_reviewer.text}"
    reviewer_token = res_reviewer.json()["access_token"]
    assert reviewer_token, "Reviewer access token is missing"

    me_reviewer = client.get("/api/auth/me", headers={"Authorization": f"Bearer {reviewer_token}"})
    assert me_reviewer.status_code == 200
    assert me_reviewer.json()["role"] == "reviewer"
    assert me_reviewer.json()["is_active"] is True
    print("[PASS] Test 2: Reviewer Login succeeded with valid token and role 'reviewer'")

    # TEST 3: Sales Login
    sales_payload = {"email": "sales@leadshark.io", "password": "SalesLeadShark2026!"}
    res_sales = client.post("/api/auth/login", json=sales_payload)
    assert res_sales.status_code == 200, f"Sales login failed: {res_sales.text}"
    sales_token = res_sales.json()["access_token"]
    assert sales_token, "Sales access token is missing"

    me_sales = client.get("/api/auth/me", headers={"Authorization": f"Bearer {sales_token}"})
    assert me_sales.status_code == 200
    assert me_sales.json()["role"] == "sales"
    assert me_sales.json()["is_active"] is True
    print("[PASS] Test 3: Sales Login succeeded with valid token and role 'sales'")

    # TEST 4: Role-Based Permissions (RBAC Verification)
    # 4a. Admin can view audit logs
    admin_audit = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_audit.status_code == 200, f"Admin could not access audit logs: {admin_audit.text}"
    print("[PASS] Test 4a: Admin successfully authorized to access audit logs")

    # 4b. Sales blocked from audit logs
    sales_audit = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {sales_token}"})
    assert sales_audit.status_code == 403, f"Sales should be 403 on audit logs, got {sales_audit.status_code}"
    print("[PASS] Test 4b: Sales role strictly blocked from audit logs (HTTP 403 Forbidden)")

    # 4c. Reviewer authorized to view audit logs (Compliance oversight)
    rev_audit = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {reviewer_token}"})
    assert rev_audit.status_code == 200, f"Reviewer should be allowed on audit logs, got {rev_audit.status_code}"
    print("[PASS] Test 4c: Reviewer role successfully authorized for audit log compliance review")

    # 4d. Sales blocked from campaign approval (Four-Eyes governance)
    sales_approve = client.post("/api/campaigns/1/approve", headers={"Authorization": f"Bearer {sales_token}"})
    assert sales_approve.status_code == 403, f"Sales should be 403 on campaign approval, got {sales_approve.status_code}"
    print("[PASS] Test 4d: Sales role strictly blocked from campaign approval (HTTP 403 Forbidden)")

    # TEST 5: Dual Route Endpoint Verification (/auth/login vs /api/auth/login)
    dual_res = client.post("/auth/login", json=admin_payload)
    assert dual_res.status_code == 200, f"Root /auth/login failed: {dual_res.text}"
    print("[PASS] Test 5: Root level /auth/login endpoint works interchangeably with /api/auth/login")

    # TEST 6: Case-Insensitivity & Whitespace Resiliency
    mixed_case_res = client.post("/api/auth/login", json={"email": "  ADMIN@LeadShark.IO  ", "password": "AdminLeadShark2026!"})
    assert mixed_case_res.status_code == 200, f"Mixed case login failed: {mixed_case_res.text}"
    print("[PASS] Test 6: Mixed-case and whitespace-padded email successfully normalized and authenticated")

    # TEST 7: Invalid Credentials Security Check
    bad_pass_res = client.post("/api/auth/login", json={"email": "admin@leadshark.io", "password": "WrongPassword123!"})
    assert bad_pass_res.status_code == 401, f"Bad password should return 401, got {bad_pass_res.status_code}"
    print("[PASS] Test 7: Invalid password correctly rejected with HTTP 401 Unauthorized")

    print("=" * 60)
    print("   ALL AUTHENTICATION & ROLE TESTS PASSED SUCCESSFULLY! (7/7)")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
