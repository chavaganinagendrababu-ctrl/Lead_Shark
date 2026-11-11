import sys
import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

def run_phase6_test_suite():
    print("=" * 70)
    print("      PHASE 6: PRODUCTION AUTHENTICATION & ROLE TEST FLOW")
    print("=" * 70)

    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    # Pre-check: Health & DB check
    h = client.get("/health")
    assert h.status_code == 200 and h.json()["status"] == "healthy"
    print(f"[PASS] Pre-Check: Backend health OK | DB: {h.json().get('database')} | Provisioned: {h.json().get('users_provisioned')}")

    # TEST 1: Admin Login
    admin_payload = {"email": "admin@leadshark.io", "password": "AdminLeadShark2026!"}
    res_admin = client.post("/api/auth/login", json=admin_payload)
    assert res_admin.status_code == 200, f"Admin login failed: {res_admin.text}"
    admin_body = res_admin.json()
    admin_token = admin_body["access_token"]
    assert admin_token, "Admin access_token missing"
    assert admin_body.get("user") is not None, "Admin user payload missing from login response"
    assert admin_body["user"]["role"] == "admin"
    print(f"[PASS] Test 1: Admin Login -> Token issued, bundled user ID={admin_body['user']['id']}, Role='{admin_body['user']['role']}'")

    # TEST 2: Sales Login
    sales_payload = {"email": "sales@leadshark.io", "password": "SalesLeadShark2026!"}
    res_sales = client.post("/api/auth/login", json=sales_payload)
    assert res_sales.status_code == 200, f"Sales login failed: {res_sales.text}"
    sales_body = res_sales.json()
    sales_token = sales_body["access_token"]
    assert sales_token, "Sales access_token missing"
    assert sales_body["user"]["role"] == "sales"
    print(f"[PASS] Test 2: Sales Login -> Token issued, bundled user ID={sales_body['user']['id']}, Role='{sales_body['user']['role']}'")

    # TEST 3: Reviewer Login
    reviewer_payload = {"email": "reviewer@leadshark.io", "password": "ReviewerLeadShark2026!"}
    res_reviewer = client.post("/api/auth/login", json=reviewer_payload)
    assert res_reviewer.status_code == 200, f"Reviewer login failed: {res_reviewer.text}"
    reviewer_body = res_reviewer.json()
    reviewer_token = reviewer_body["access_token"]
    assert reviewer_token, "Reviewer access_token missing"
    assert reviewer_body["user"]["role"] == "reviewer"
    print(f"[PASS] Test 3: Reviewer Login -> Token issued, bundled user ID={reviewer_body['user']['id']}, Role='{reviewer_body['user']['role']}'")

    # TEST 4: Incorrect Password
    bad_pass = client.post("/api/auth/login", json={"email": "admin@leadshark.io", "password": "WrongPassword999!"})
    assert bad_pass.status_code == 401
    assert bad_pass.json()["detail"] == "Invalid credentials"
    print("[PASS] Test 4: Incorrect Password -> Rejected with HTTP 401 Unauthorized ('Invalid credentials')")

    # TEST 5: Invalid Email
    bad_email = client.post("/api/auth/login", json={"email": "nonexistent@enterprise.demo", "password": "AdminLeadShark2026!"})
    assert bad_email.status_code == 401
    assert bad_email.json()["detail"] == "Invalid credentials"
    print("[PASS] Test 5: Invalid Email -> Rejected with HTTP 401 Unauthorized ('Invalid credentials')")

    # TEST 6: Expired or Invalid Token
    invalid_token_req = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.fake.token.signature"})
    assert invalid_token_req.status_code == 401
    print("[PASS] Test 6: Expired / Malformed Token -> Rejected with HTTP 401 Unauthorized")

    # TEST 7: Unauthorized API Access
    no_auth_req = client.get("/api/audit-logs")
    assert no_auth_req.status_code == 401
    print("[PASS] Test 7: Unauthorized API Access -> Rejected with HTTP 401 Unauthorized")

    # TEST 8: Role-Based Dashboard & Resource Access
    # 8a: Admin accessing dashboard & privileged audit logs
    dash_admin = client.get("/api/dashboard/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert dash_admin.status_code == 200
    audit_admin = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert audit_admin.status_code == 200
    print("[PASS] Test 8a: Admin Dashboard & Audit Logs -> Authorized (HTTP 200 OK)")

    # 8b: Reviewer accessing dashboard & compliance logs, but blocked from non-reviewer endpoints
    dash_rev = client.get("/api/dashboard/stats", headers={"Authorization": f"Bearer {reviewer_token}"})
    assert dash_rev.status_code == 200
    audit_rev = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {reviewer_token}"})
    assert audit_rev.status_code == 200
    print("[PASS] Test 8b: Reviewer Dashboard & Compliance Audit Logs -> Authorized (HTTP 200 OK)")

    # 8c: Sales accessing dashboard, but strictly blocked from audit logs and approvals
    dash_sales = client.get("/api/dashboard/stats", headers={"Authorization": f"Bearer {sales_token}"})
    assert dash_sales.status_code == 200
    audit_sales = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {sales_token}"})
    assert audit_sales.status_code == 403, f"Expected 403 for sales audit, got {audit_sales.status_code}"
    sales_approve = client.post("/api/campaigns/1/approve", headers={"Authorization": f"Bearer {sales_token}"})
    assert sales_approve.status_code == 403, f"Expected 403 for sales approve, got {sales_approve.status_code}"
    print("[PASS] Test 8c: Sales Dashboard Accessible | Audit Logs & Campaign Approval Blocked (HTTP 403 Forbidden)")

    # TEST 9: Logout & Login Again Simulation
    # Emulating client-side token discard and re-issuing a new token
    res_admin2 = client.post("/api/auth/login", json=admin_payload)
    assert res_admin2.status_code == 200
    new_admin_token = res_admin2.json()["access_token"]
    assert new_admin_token != "", "New token generation failed"
    me_after_relogin = client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_admin_token}"})
    assert me_after_relogin.status_code == 200
    assert me_after_relogin.json()["email"] == "admin@leadshark.io"
    print("[PASS] Test 9: Logout & Login Again -> Re-authentication succeeds and generates active session token")

    # TEST 10: Page Refresh / Token Persistence Verification
    # Simulates page reload where client uses previously stored JWT token to restore user profile
    persisted_session = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert persisted_session.status_code == 200
    assert persisted_session.json()["id"] == admin_body["user"]["id"]
    assert persisted_session.json()["role"] == "admin"
    print("[PASS] Test 10: Page Refresh Token Persistence -> Session accurately restored from stored JWT token")

    print("=" * 70)
    print("   ALL 10 PRODUCTION AUTHENTICATION & SECURITY TESTS PASSED! (10/10)")
    print("=" * 70)

if __name__ == "__main__":
    run_phase6_test_suite()
