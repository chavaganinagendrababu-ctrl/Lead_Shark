import io
import re
from datetime import datetime, timezone
from typing import Dict, Any, List
import pandas as pd
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.compliance import SuppressionList
from app.services.verification import verify_email_address
from app.services.classification import classifier_service

REQUIRED_COLUMNS = ["company_name", "contact_name", "email"]
DANGEROUS_FORMULA_PREFIXES = ('=', '+', '-', '@', '\t', '\r')

def sanitize_csv_value(val: Any) -> str:
    """Protects against CSV Formula Injection (DDE injection)."""
    if val is None:
        return ""
    str_val = str(val).strip()
    if str_val.startswith(DANGEROUS_FORMULA_PREFIXES):
        # Prefix with a single quote to neutralize formula evaluation in Excel/Sheets
        return "'" + str_val
    return str_val

def parse_and_import_leads_csv(
    file_bytes: bytes,
    db: Session,
    source_name: str = "CSV Upload",
    lawful_basis: str = "Legitimate interest for B2B commercial outreach"
) -> Dict[str, Any]:
    try:
        # Read CSV with pandas
        df = pd.read_csv(io.BytesIO(file_bytes), dtype=str)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse CSV file: {str(e)}",
            "imported": 0,
            "skipped": 0,
            "invalid": 0,
            "duplicates": 0,
            "suppressed": 0
        }

    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        return {
            "success": False,
            "error": f"CSV missing required columns: {', '.join(missing_cols)}. Required: company_name, contact_name, email",
            "imported": 0,
            "skipped": 0,
            "invalid": 0,
            "duplicates": 0,
            "suppressed": 0
        }

    total_rows = len(df)
    imported = 0
    skipped = 0
    invalid_count = 0
    duplicate_count = 0
    suppressed_count = 0
    seen_in_batch = set()

    for idx, row in df.iterrows():
        raw_email = str(row.get("email", "")).strip().lower()
        company_name = str(row.get("company_name", "")).strip()
        contact_name = str(row.get("contact_name", "")).strip()

        if not raw_email or not company_name or not contact_name:
            invalid_count += 1
            continue

        # Basic email syntax check
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", raw_email):
            invalid_count += 1
            continue

        # Check duplicate in this file batch
        if raw_email in seen_in_batch:
            duplicate_count += 1
            continue
        seen_in_batch.add(raw_email)

        # Check duplicate against existing database leads
        existing_lead = db.query(Lead).filter(Lead.email == raw_email).first()
        if existing_lead:
            duplicate_count += 1
            continue

        # Check global suppression list
        domain = raw_email.split("@")[-1]
        is_suppressed = db.query(SuppressionList).filter(
            (SuppressionList.email == raw_email) | (SuppressionList.domain == domain)
        ).first()

        if is_suppressed:
            suppressed_count += 1
            skipped += 1
            continue

        # Extract optional fields
        job_title = str(row.get("job_title", "")).strip() or None
        phone = str(row.get("phone", "")).strip() or None
        website = str(row.get("website", "")).strip() or None
        region = str(row.get("region", "")).strip() or None
        
        # Sector classification
        raw_sector = str(row.get("sector", "")).strip()
        if raw_sector and raw_sector.lower() not in ["", "nan", "none", "other"]:
            sector = raw_sector
            confidence = 0.85
            reason = "Specified directly in CSV dataset"
        else:
            classified = classifier_service.classify(company_name, website or "", job_title or "")
            sector = classified["sector"]
            confidence = classified["confidence"]
            reason = classified["reason"]

        new_lead = Lead(
            company_name=company_name,
            contact_name=contact_name,
            job_title=job_title,
            email=raw_email,
            phone=phone,
            website=website,
            sector=sector,
            region=region,
            source_type="csv_import",
            source_url=source_name,
            collection_date=datetime.now(timezone.utc),
            lawful_basis_note=lawful_basis,
            # Mandatory requirement: Never mark imported addresses as verified automatically
            email_verification_status="unknown",
            verification_details="Imported via CSV. Verification pending.",
            lead_status="pending_review",
            classification_confidence=confidence,
            classification_reason=reason
        )
        db.add(new_lead)
        imported += 1

    db.commit()

    return {
        "success": True,
        "total_rows": total_rows,
        "imported": imported,
        "skipped": skipped,
        "invalid": invalid_count,
        "duplicates": duplicate_count,
        "suppressed": suppressed_count
    }

