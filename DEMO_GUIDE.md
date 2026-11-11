# Lead Shark — Live Demo & Presentation Walkthrough

Use this guide to demonstrate **Lead Shark** during your technical assignment review.

---

## 1. Quick Access Credentials

The platform is pre-seeded with 3 role accounts. On the login page, you can click the quick-fill buttons at the bottom:

| Account | Email | Password | Role |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@leadshark.io` | `AdminLeadShark2026!` | Full administrator |
| **Reviewer** | `reviewer@leadshark.io` | `ReviewerLeadShark2026!` | Lead & Campaign Approver |
| **Sales User** | `sales@leadshark.io` | `SalesLeadShark2026!` | Lead Ingestion & Campaign Author |

---

## 2. Recommended 5-Minute Demo Flow

### Step 1: Authentication & Role Enforcement (1 min)
1. Navigate to `http://localhost:5173`.
2. Click the **Sales** button on the login screen and click **Sign In**.
3. Point out:
   - Notice the role badge in the bottom-left sidebar: `SALES`.
   - The **Audit Logs** module is automatically hidden from the navigation because Sales users lack audit access.
4. If a sales user tries to navigate directly to `http://localhost:5173/audit-logs`, the protected route blocks access.

### Step 2: Leads Management & CSV Ingestion (1.5 min)
1. Click **Leads Management** in the sidebar.
2. Click **Import CSV** and point out the downloadable template:
   - Click the **Template.csv** button to show required and optional columns.
3. Demonstrate lead verification:
   - Click **Verify MX** on any lead in the table.
   - Show the prompt showing real DNS MX resolution host and deliverability disclaimer.
4. Demonstrate sector classification:
   - Click **Classify** on any lead to see the rule-based confidence score and keyword matching rationale.
5. Demonstrate export protection:
   - Click **Export CSV** to show that exported files have formula injection (DDE) protection applied.

### Step 3: Four-Eyes Campaign Governance (1.5 min)
1. Click **Campaigns** in the sidebar.
2. Click **Create Campaign**:
   - Name: `Q4 Healthcare Outreach`
   - Subject: `Innovating clinical systems at {{company}}`
   - Target Sector: `Healthcare`
   - Body: `Hello {{first_name}},\n\nI love what {{company}} is building in the {{sector}} space.\n\nBest,\nSales Team`
   - Click **Submit for Review**.
3. Campaign is created in `draft` status.
4. Click the eye icon (**Preview**):
   - Notice that `{{first_name}}`, `{{company}}`, and `{{sector}}` are dynamically interpolated.
   - Point out the cryptographic, signed one-click unsubscribe URL.
5. Attempt self-approval:
   - As the creator (Sales user), the **Approve** button is disabled with a tooltip explaining that campaign creators cannot approve their own outreach.
6. Switch to **Reviewer**:
   - Log out and log in as `reviewer@leadshark.io`.
   - Go to **Campaigns** and click **Approve** on the sales campaign.
   - Enter approval notes. The status changes to `APPROVED`.
7. Demonstrate approval revocation:
   - Click the pencil icon (**Edit**) on the approved campaign and modify the subject line.
   - Save the change. Point out that the status **immediately resets** to `PENDING_APPROVAL`.

### Step 4: Universal Compliance & Global Suppression (1 min)
1. Click **Compliance & Suppression** in the sidebar.
2. In the **Interactive Unsubscribe Simulator**:
   - Enter an email (e.g. `optout-demo@company.com`) and click **Simulate Opt-Out**.
   - The address is immediately added to the Global Suppression List.
3. Try to bypass suppression:
   - Go to **Leads Management** and click **Add Lead**.
   - Attempt to add `optout-demo@company.com`.
   - The system displays a validation error: the email is on the Global Suppression List and cannot be imported.

### Step 5: Security Audit Ledger (30 sec)
1. Click **Audit Logs** in the sidebar (visible to Reviewer and Admin).
2. Show the real-time audit ledger:
   - Log entries for login, lead verification, campaign approval, and suppression opt-out with actor email, action code, and timestamp.

---

## 3. Key Talking Points for Evaluators

1. **Compliance First:** Universal suppression list blocks forbidden contacts across manual entry, CSV import, and campaign audience generation.
2. **Four-Eyes Governance:** Creators cannot self-approve production campaigns. Template edits revoke approvals automatically.
3. **Transparent Reporting:** The application does not fabricate delivery, open, or click rates while in Version 1 Safe Mode.
4. **Security Hardening:** Salted bcrypt hashing, JWT tokens, DDE formula injection protection on CSV exports, and token-bucket rate limiting on authentication.
