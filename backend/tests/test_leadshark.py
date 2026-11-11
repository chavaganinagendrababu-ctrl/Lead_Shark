import io
from fastapi.testclient import TestClient

def get_auth_token(client: TestClient, email: str = "admin@leadshark.io", password: str = "AdminLeadShark2026!") -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, f"Login failed for {email}: {response.text}"
    return response.json()["access_token"]

def test_15_health_check(client: TestClient):
    """Test 15: Backend health endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_01_login_success(client: TestClient):
    """Test 1: Login works with valid credentials."""
    response = client.post("/api/auth/login", json={
        "email": "admin@leadshark.io",
        "password": "AdminLeadShark2026!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_02_unauthorized_rejected(client: TestClient):
    """Test 2: Unauthorized requests are rejected."""
    # Without token
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 401

    # With invalid token
    response = client.get("/api/dashboard/stats", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401

def test_03_create_lead(client: TestClient):
    """Test 3: Leads can be created."""
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "company_name": "Quantum Cyber Labs",
        "contact_name": "Evelyn Reed",
        "job_title": "CISO",
        "email": "evelyn.reed@quantumcyber.demo",
        "phone": "+1-555-9012",
        "website": "https://quantumcyber.demo",
        "sector": "Information Technology",
        "region": "North America"
    }
    response = client.post("/api/leads", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "evelyn.reed@quantumcyber.demo"
    assert data["email_verification_status"] == "unknown"  # Never auto-verified
    assert data["lead_status"] == "pending_review"

def test_05_duplicate_email_rejected(client: TestClient):
    """Test 5: Duplicate emails are rejected."""
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "company_name": "Quantum Cyber Duplicate",
        "contact_name": "Evelyn Copy",
        "email": "evelyn.reed@quantumcyber.demo",
    }
    response = client.post("/api/leads", json=payload, headers=headers)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()

def test_04_csv_import_and_deduplication(client: TestClient):
    """Test 4: CSV imports work, skips duplicates and suppressed emails."""
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    csv_content = (
        "company_name,contact_name,job_title,email,sector,region\n"
        "Alpha Dynamics,Arthur Pendelton,CTO,arthur.p@alphadynamics.demo,Information Technology,North America\n"
        "Beta Biologics,Beatrice Webb,COO,beatrice@betabiologics.demo,Healthcare,Europe\n"
        "Duplicate Lead,Dup User,Dev,arthur.p@alphadynamics.demo,Information Technology,North America\n" # Duplicate in file
        "Suppressed Co,Suppressed User,VP,optout@competitorcorp.com,Finance,North America\n" # Suppressed
    )

    files = {"file": ("leads.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = client.post("/api/leads/import", files=files, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["imported"] == 2
    assert data["duplicates"] >= 1
    assert data["suppressed"] >= 1

def test_06_verification_and_invalid_email_not_valid(client: TestClient):
    """Test 6: Email validation flags invalid syntax/domains as non-valid."""
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Add a lead with invalid disposable domain
    payload = {
        "company_name": "Temp Spammer",
        "contact_name": "Fake Name",
        "email": "fake.user@mailinator.com",
    }
    response = client.post("/api/leads", json=payload, headers=headers)
    lead_id = response.json()["id"]

    # Trigger verify
    verify_res = client.post(f"/api/leads/{lead_id}/verify", headers=headers)
    assert verify_res.status_code == 200
    assert verify_res.json()["status"] == "invalid"
    assert "disposable" in verify_res.json()["details"].lower()

def test_07_lead_filtering(client: TestClient):
    """Test 7: Lead filtering works by sector and status."""
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    res_it = client.get("/api/leads?sector=Information Technology", headers=headers)
    assert res_it.status_code == 200
    it_leads = res_it.json()["items"]
    assert all(l["sector"] == "Information Technology" for l in it_leads)

def test_08_suppression_and_campaign_eligibility(client: TestClient):
    """Test 8: Suppressed emails cannot become campaign eligible."""
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Add a test email to suppression
    supp_res = client.post("/api/suppression", json={
        "email": "blocked.lead@example.com",
        "reason": "spam_complaint",
        "notes": "Direct spam complaint"
    }, headers=headers)
    assert supp_res.status_code == 201

    # Attempt to create a lead with suppressed email -> should be blocked
    lead_res = client.post("/api/leads", json={
        "company_name": "Blocked Inc",
        "contact_name": "Blocked User",
        "email": "blocked.lead@example.com"
    }, headers=headers)
    assert lead_res.status_code == 400
    assert "suppression" in lead_res.json()["detail"].lower()

def test_09_unsubscribe_endpoint(client: TestClient):
    """Test 9: Unsubscribe works via signed token."""
    from app.security.auth import create_unsubscribe_token
    token = create_unsubscribe_token("optout-test-recipient@business.com")

    response = client.post(f"/unsubscribe/{token}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "optout-test-recipient@business.com" in data["message"]

    # Verify it is now in suppression list
    admin_token = get_auth_token(client)
    supp_res = client.get(f"/api/suppression?search=optout-test-recipient@business.com", headers={"Authorization": f"Bearer {admin_token}"})
    assert len(supp_res.json()) >= 1

def test_10_and_11_campaign_creation_and_approval(client: TestClient):
    """Test 10 & 11: Campaign creation works & creator cannot approve own campaign."""
    sales_token = get_auth_token(client, email="sales@leadshark.io", password="SalesLeadShark2026!")
    sales_headers = {"Authorization": f"Bearer {sales_token}"}

    # Sales creates campaign
    camp_res = client.post("/api/campaigns", json={
        "name": "Q4 Cloud Modernization",
        "subject": "Modernizing infrastructure for {{company}}",
        "body_template": "Hello {{first_name}}, let's talk about {{sector}} solutions for {{company}}.",
        "sector": "Information Technology",
        "daily_limit": 100
    }, headers=sales_headers)
    assert camp_res.status_code == 201
    camp_id = camp_res.json()["id"]
    assert camp_res.json()["status"] == "draft"

    # Sales tries to approve their own campaign -> Forbidden (Four-eyes policy)
    self_approve = client.post(f"/api/campaigns/{camp_id}/approve", json={"action": "approve"}, headers=sales_headers)
    assert self_approve.status_code == 403

    # Reviewer approves campaign -> Allowed
    reviewer_token = get_auth_token(client, email="reviewer@leadshark.io", password="ReviewerLeadShark2026!")
    reviewer_headers = {"Authorization": f"Bearer {reviewer_token}"}
    approve_res = client.post(f"/api/campaigns/{camp_id}/approve", json={"action": "approve"}, headers=reviewer_headers)
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "approved"

def test_12_editing_campaign_resets_approval(client: TestClient):
    """Test 12: Editing an approved campaign resets its approval status."""
    reviewer_token = get_auth_token(client, email="reviewer@leadshark.io", password="ReviewerLeadShark2026!")
    reviewer_headers = {"Authorization": f"Bearer {reviewer_token}"}

    # Get the approved campaign
    campaigns = client.get("/api/campaigns", headers=reviewer_headers).json()
    approved_camp = next((c for c in campaigns if c["status"] == "approved"), None)
    assert approved_camp is not None

    # Update template body
    update_res = client.put(f"/api/campaigns/{approved_camp['id']}", json={
        "body_template": "Modified template: Hello {{first_name}} at {{company}}!"
    }, headers=reviewer_headers)
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "pending_approval"

def test_13_audit_logs_generated(client: TestClient):
    """Test 13: Audit logs are recorded for actions."""
    reviewer_token = get_auth_token(client, email="reviewer@leadshark.io", password="ReviewerLeadShark2026!")
    reviewer_headers = {"Authorization": f"Bearer {reviewer_token}"}

    audit_res = client.get("/api/audit-logs", headers=reviewer_headers)
    assert audit_res.status_code == 200
    items = audit_res.json()["items"]
    assert len(items) > 0
    actions = [a["action"] for a in items]
    assert any("LOGIN" in a or "LEAD" in a or "CAMPAIGN" in a for a in actions)

