# LEAD SHARK
### B2B Lead Discovery & Compliant Outreach Platform

**Lead Shark** is an enterprise-grade B2B lead discovery, verification, and compliant outreach platform engineered to eliminate spam risks, enforce strict data privacy standards (GDPR, CAN-SPAM), and streamline sales engagement.

---

## Architecture Overview

```
lead-shark/
├── backend/                  # FastAPI RESTful Microservice
│   ├── app/
│   │   ├── main.py           # FastAPI lifecycle, CORS, exception handlers
│   │   ├── config.py         # Pydantic Settings & environment config
│   │   ├── database.py       # SQLAlchemy engine & session manager
│   │   ├── models/           # PostgreSQL ORM entities
│   │   │   ├── user.py       # Users & RBAC roles
│   │   │   ├── lead.py       # Staged leads & provenance
│   │   │   ├── company.py    # Company metadata
│   │   │   ├── discovery.py  # Ingestion batch records
│   │   │   ├── campaign.py   # Campaigns & approval ledger
│   │   │   ├── compliance.py # Global suppression list
│   │   │   └── audit.py      # Immutable security audit log
│   │   ├── schemas/          # Pydantic v2 request/response models
│   │   ├── routes/           # REST endpoints
│   │   │   ├── auth.py       # JWT authentication & profile
│   │   │   ├── dashboard.py  # Real-time analytics & KPIs
│   │   │   ├── leads.py      # CRUD, CSV import/export, verify, classify
│   │   │   ├── discovery.py  # Ingestion pipelines & job history
│   │   │   ├── campaigns.py  # Campaign workflows & 4-eyes approval
│   │   │   ├── compliance.py # Suppression & signed token unsubscribe
│   │   │   └── audit.py      # Security audit log queries
│   │   ├── services/         # Business logic & compliance engines
│   │   │   ├── verification.py # RFC syntax & DNS MX validation
│   │   │   ├── classification.py # Sector rule engine / RAG connector
│   │   │   ├── compliance.py # 7-step audience eligibility filter
│   │   │   └── audit.py      # Audit trail logger
│   │   ├── security/         # Cryptography & auth guards
│   │   │   ├── auth.py       # Bcrypt & JWT tokens
│   │   │   └── rate_limiter.py # Token bucket rate limiter
│   │   └── utils/
│   │       ├── csv_handler.py # CSV parser & DDE formula protection
│   │       └── seeding.py    # Initial roles & demo data
│   ├── tests/                # Pytest test suite (100% pass)
│   ├── Dockerfile            # Production container definition
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Backend environment template
│
├── frontend/                 # React.js (Vite) Enterprise Dashboard
│   ├── src/
│   │   ├── components/       # Enterprise UI components & Sidebar
│   │   ├── pages/            # View modules (Dashboard, Leads, etc.)
│   │   ├── context/          # Auth state & role permissions
│   │   ├── layouts/          # Responsive dashboard workspace
│   │   └── services/         # Axios API client
│   ├── package.json          # Dependencies
│   ├── vite.config.js        # Vite build & reverse proxy
│   └── tailwind.config.js    # Custom navy SaaS theme
│
├── vercel.json               # Vercel SPA routing configuration
├── render.yaml               # Render Blueprint (Web Service + Postgres)
└── README.md                 # Complete documentation
```

---

## Key Features & Compliance Controls

1. **Global Suppression Engine:**
   - Permanent email and domain-level exclusion.
   - Screened during manual entry, CSV import, and campaign audience assembly.
   - Erasure requests (GDPR Article 17) maintain suppression protection even if contact profile is deleted.
2. **7-Step Campaign Outreach Eligibility Check:**
   Every outreach candidate must pass all 7 criteria before campaign eligibility:
   1. Email syntax is valid.
   2. Email is not on the suppression list.
   3. Email domain is not on the suppression list.
   4. Lead status is `approved` by reviewer.
   5. Campaign status is `approved`.
   6. Cooldown window: lead has not been contacted within the last 14 days.
   7. Campaign is within daily sending limit.
3. **Four-Eyes Governance Workflow:**
   - A campaign creator can **never** approve their own outreach campaign.
   - Approvals require independent Reviewer or Admin sign-off.
   - Any template or sector modification automatically revokes approval and returns status to `pending_approval`.
4. **CSV DDE Formula Injection Protection:**
   - When exporting CSV data, dangerous spreadsheet characters (`=`, `+`, `-`, `@`, `\t`, `\r`) are automatically neutralized to protect recipient spreadsheet software against remote code execution.
5. **Cryptographic One-Click Unsubscribe:**
   - Signed, expiring JWT tokens embedded in campaign previews and test links.
   - Recipient opt-out immediately records into the suppression list with zero friction.
6. **Email Verification Pipeline:**
   - Multi-tier check: RFC 5322 syntax validation, temporary/disposable domain rejection, role account detection (`info@`, `support@` flagged as risky), and DNS MX mail exchange host verification.
   - Explicit rule: Imported emails are never marked verified automatically.
7. **Empirical Reporting:**
   - Real database counts only. Zero fabricated open or click rates. In Version 1 Safe Mode, delivery metrics are explicitly documented as safe-mode locked.

---

## Role-Based Access Control (RBAC)

| Capability | Admin | Reviewer | Sales User |
| :--- | :---: | :---: | :---: |
| View Dashboard & Analytics | Yes | Yes | Yes |
| Create / Import Leads | Yes | Yes | Yes |
| Verify Email / Classify Sector | Yes | Yes | Yes |
| Delete Lead Records | Yes | Yes | No |
| Author Outreach Campaign | Yes | Yes | Yes |
| Approve Outreach Campaign | Yes | Yes (Non-own) | No |
| Pause / Resume Campaigns | Yes | Yes | Yes |
| Manage Global Suppression List | Yes | Yes | No |
| Access Security Audit Logs | Yes | Yes | No |

---

## Seed Accounts (Quick Access)

For local evaluation, the database automatically seeds three role accounts:

| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@leadshark.io` | `AdminLeadShark2026!` |
| **Reviewer** | `reviewer@leadshark.io` | `ReviewerLeadShark2026!` |
| **Sales** | `sales@leadshark.io` | `SalesLeadShark2026!` |

---

## Local Development Setup

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Node.js 18+ (Tested on Node v24)
- Git

### 2. Backend Setup
```bash
# From workspace root
cd backend

# Install dependencies (virtual environment recommended)
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at: `http://127.0.0.1:8000/docs`  
Health check endpoint: `http://127.0.0.1:8000/health`

### 3. Frontend Setup
```bash
# In a separate terminal
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Running the Automated Test Suite

Run the full backend test suite covering authentication, duplicate detection, suppression enforcement, four-eyes campaign approval, and CSV sanitization:

```bash
# From workspace root
pytest backend/tests -v
```

All 13 integration and unit tests pass with 100% success.

---

## Production Deployment Guide

### A. Deploy Backend to Render

1. **Create PostgreSQL Database on Render:**
   - Log into [Render Dashboard](https://dashboard.render.com).
   - Click **New +** -> **PostgreSQL**.
   - Name: `leadshark-postgres`
   - Copy the **Internal Database URL** (or External Database URL).
2. **Create Web Service on Render:**
   - Click **New +** -> **Web Service**.
   - Connect your GitHub repository.
   - Root Directory: `backend`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add Environment Variables:
     - `ENVIRONMENT` = `production`
     - `DATABASE_URL` = `<your-render-postgresql-connection-string>`
     - `SECRET_KEY` = `<strong-random-hex-key>`
     - `FRONTEND_URL` = `https://<your-vercel-app>.vercel.app`
3. **Verify:** Check `https://<your-render-app>.onrender.com/health` returns status `healthy`.

*Alternatively, use Render Blueprints by deploying with the included `render.yaml` file.*

---

### B. Deploy Frontend to Vercel

1. **Import Project into Vercel:**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard) -> **Add New...** -> **Project**.
   - Select your repository.
2. **Configure Build Settings:**
   - Framework Preset: **Vite**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
3. **Set Environment Variables:**
   - `VITE_API_BASE_URL` = `https://<your-render-backend-subdomain>.onrender.com/api`
4. **Deploy:** Click **Deploy**. Vercel will build the frontend SPA and apply the rewrites defined in `vercel.json`.

---

## API Endpoints Reference

### Authentication
- `POST /api/auth/login` - Authenticate user & issue JWT bearer token.
- `GET /api/auth/me` - Retrieve current active user profile and role.

### Dashboard & Analytics
- `GET /api/dashboard/stats` - Empirical aggregates, sector distribution, regional readiness, recent leads, and activity ledger.

### Discovery Engine
- `GET /api/discovery/jobs` - List batch discovery ingestion executions.
- `POST /api/discovery/jobs` - Trigger compliant discovery from permitted directory connector.

### Lead Management
- `GET /api/leads` - Paginated query with search, sector, region, verification status, and approval filters.
- `POST /api/leads` - Manually stage new prospect (screened against duplicates and suppression).
- `GET /api/leads/{id}` - Fetch single lead details.
- `PUT /api/leads/{id}` - Update lead fields (resets verification if email modified).
- `DELETE /api/leads/{id}` - Remove lead (suppression records remain intact).
- `POST /api/leads/import` - Bulk upload CSV with duplicate & suppression filtering.
- `GET /api/leads/export` - Export leads with CSV formula injection protection.
- `POST /api/leads/{id}/verify` - Execute DNS MX & RFC email validation.
- `POST /api/leads/{id}/classify` - Rule-based / RAG sector classification.

### Outreach Campaigns
- `GET /api/campaigns` - List all authored campaigns.
- `POST /api/campaigns` - Create new campaign in `draft` status.
- `GET /api/campaigns/{id}` - Retrieve campaign details.
- `PUT /api/campaigns/{id}` - Modify campaign (automatically revokes previous approval).
- `POST /api/campaigns/{id}/approve` - Reviewer/Admin approval (creator cannot self-approve).
- `POST /api/campaigns/{id}/pause` - Toggle pause / resume status.
- `GET /api/campaigns/{id}/preview` - Render template with merge tags & signed unsubscribe link.
- `GET /api/campaigns/{id}/eligibility` - 7-step audience compliance audit breakdown.

### Compliance & Suppression
- `GET /api/suppression` - Search and list global suppression records.
- `POST /api/suppression` - Add manual suppression record.
- `POST /unsubscribe/{token}` - Public cryptographic one-click unsubscribe endpoint.

### Audit Logs
- `GET /api/audit-logs` - Search and filter immutable security and operational audit trail.

---

## Version 2 Recommendations

1. **Integration with External RAG Agent:** Wire the `BaseSectorClassifier` interface to an external LLM / vector retrieval service for nuanced company categorization.
2. **Mailbox-Level SMTP Handshake:** Integrate specialized deliverability APIs (e.g. ZeroBounce, NeverBounce) for mailbox-level ping beyond DNS MX checks.
3. **Official Provider Adapters:** Implement SendGrid / Amazon SES / Postmark adapters with webhooks for automated bounce, open, and spam complaint synchronization once domain reputation and warmup are complete.
