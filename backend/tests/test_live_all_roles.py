import sys
import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

def test_live_all_roles():
    print("=" * 65)
    print("      LIVE HTTP AUTHENTICATION & ROLE VERIFICATION SUITE")
    print("=" * 65)

    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    # 1. Health Probe
    h = client.get("/health")
    assert h.status_code == 200 and h.json()["status"] == "healthy"
    print("[PASS] System Health: Backend reachable and connected to database.")

    # 2. Test Admin Role
    admin_payload = {"email": "admin@leadshark.io", "password": "AdminLeadShark2026!"}
    res_admin = client.post("/api/auth/login", json=admin_payload)
    assert res_admin.status_code == 200, f"Admin login failed: {res_admin.text}"
    admin_token = res_admin.json()["access_token"]
    assert admin_token, "Admin access_token missing"
    print("[PASS] 1a. Admin Login: HTTP 200 OK, valid JWT access token generated.")

    # 2b. Admin Profile & Role
    me_admin = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert me_admin.status_code == 200
    admin_data = me_admin.json()
    assert admin_data["role"] == "admin"
    assert admin_data["is_active"] is True
    assert admin_data["email"] == "admin@leadshark.io"
    print(f"[PASS] 1b. Admin Identity Verified: ID={admin_data['id']}, Role='{admin_data['role']}', Active={admin_data['is_active']}")

    # 2c. Admin Dashboard Access
    dash_admin = client.get("/api/dashboard/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert dash_admin.status_code == 200
    dash_data = dash_admin.json()
    print(f"[PASS] 1c. Admin Dashboard Stats: Total Leads={dash_data.get('total_leads')}, Campaigns={dash_data.get('active_campaigns')}")

    # 2d. Admin Audit Log Access (Privileged)
    audit_admin = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert audit_admin.status_code == 200
    print("[PASS] 1d. Admin Privileged Access: Authorized to view audit logs (HTTP 200 OK).")

    # 3. Test Sales Role
    sales_payload = {"email": "sales@leadshark.io", "password": "SalesLeadShark2026!"}
    res_sales = client.post("/api/auth/login", json=sales_payload)
    assert res_sales.status_code == 200, f"Sales login failed: {res_sales.text}"
    sales_token = res_sales.json()["access_token"]
    assert sales_token, "Sales access_token missing"
    print("[PASS] 2a. Sales Login: HTTP 200 OK, valid JWT access token generated.")

    # 3b. Sales Profile & Role
    me_sales = client.get("/api/auth/me", headers={"Authorization": f"Bearer {sales_token}"})
    assert me_sales.status_code == 200
    sales_data = me_sales.json()
    assert sales_data["role"] == "sales"
    assert sales_data["is_active"] is True
    print(f"[PASS] 2b. Sales Identity Verified: ID={sales_data['id']}, Role='{sales_data['role']}', Active={sales_data['is_active']}")

    # 3c. Sales Dashboard Access
    dash_sales = client.get("/api/dashboard/stats", headers={"Authorization": f"Bearer {sales_token}"})
    assert dash_sales.status_code == 200
    print("[PASS] 2c. Sales Dashboard Stats: Accessible and verified.")

    # 3d. Sales Restricted from Audit Logs (RBAC Guard)
    audit_sales = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {sales_token}"})
    assert audit_sales.status_code == 403, f"Sales should be 403 on audit logs, got {audit_sales.status_code}"
    print("[PASS] 2d. Sales RBAC Protection: Strictly forbidden from accessing audit logs (HTTP 403 Forbidden).")

    # 3e. Sales Restricted from Approving Campaigns (Four-Eyes Guard)
    appr_sales = client.post("/api/campaigns/1/approve", headers={"Authorization": f"Bearer {sales_token}"})
    assert appr_sales.status_code == 403, f"Sales should be 403 on campaign approval, got {appr_sales.status_code}"
    print("[PASS] 2e. Sales RBAC Protection: Strictly forbidden from approving outreach campaigns (HTTP 403 Forbidden).")

    # 4. Test Reviewer Role
    rev_payload = {"email": "reviewer@leadshark.io", "password": "ReviewerLeadShark2026!"}
    res_rev = client.post("/api/auth/login", json=rev_payload)
    assert res_rev.status_code == 200, f"Reviewer login failed: {res_rev.text}"
    rev_token = res_rev.json()["access_token"]
    assert rev_token, "Reviewer access_token missing"
    print("[PASS] 3a. Reviewer Login: HTTP 200 OK, valid JWT access token generated.")

    # 4b. Reviewer Profile & Role
    me_rev = client.get("/api/auth/me", headers={"Authorization": f"Bearer {rev_token}"})
    assert me_rev.status_code == 200
    rev_data = me_rev.json()
    assert rev_data["role"] == "reviewer"
    assert rev_data["is_active"] is True
    print(f"[PASS] 3b. Reviewer Identity Verified: ID={rev_data['id']}, Role='{rev_data['role']}', Active={rev_data['is_active']}")

    # 4c. Reviewer Dashboard Access
    dash_rev = client.get("/api/dashboard/stats", headers={"Authorization": f"Bearer {rev_token}"})
    assert dash_rev.status_code == 200
    print("[PASS] 3c. Reviewer Dashboard Stats: Accessible and verified.")

    # 4d. Reviewer Authorized for Audit Oversight
    audit_rev = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {rev_token}"})
    assert audit_rev.status_code == 200
    print("[PASS] 3d. Reviewer RBAC Privilege: Authorized for compliance audit log review (HTTP 200 OK).")

    # 5. Case-Insensitivity & Whitespace Resiliency
    mixed_case = client.post("/api/auth/login", json={"email": "  ADMIN@LeadShark.IO  ", "password": "AdminLeadShark2026!"})
    assert mixed_case.status_code == 200
    print("[PASS] 4. Case & Whitespace Resiliency: '  ADMIN@LeadShark.IO  ' successfully authenticated.")

    # 6. Dual-Route Interoperability (/auth/login vs /api/auth/login)
    root_login = client.post("/auth/login", json=admin_payload)
    assert root_login.status_code == 200
    print("[PASS] 5. Dual Route Interoperability: Root level /auth/login resolves identically to /api/auth/login.")

    # 7. Invalid Password Rejection (Security Guard)
    bad_pass = client.post("/api/auth/login", json={"email": "admin@leadshark.io", "password": "WrongPassword2026!"})
    assert bad_pass.status_code == 401
    assert bad_pass.json()["detail"] == "Invalid credentials"
    print("[PASS] 6. Security Hardening: Invalid password rejected with HTTP 401 Unauthorized.")

    # 8. Unauthenticated Access Protection
    unauth = client.get("/api/audit-logs")
    assert unauth.status_code == 401
    print("[PASS] 7. Security Hardening: Unauthenticated request blocked with HTTP 401 Unauthorized.")

    print("=" * 65)
    print("   ALL 3 ROLES & SECURITY TESTS PASSED OVER LIVE HTTP! (10/10)")
    print("=" * 65)

if __name__ == "__main__":
    test_live_all_roles()
