import re
import dns.resolver
from email_validator import validate_email, EmailNotValidError

DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com",
    "yopmail.com", "trashmail.com", "throwawaymail.com"
}

ROLE_PREFIXES = {
    "admin@", "support@", "info@", "help@", "sales@", "billing@", "contact@", "marketing@"
}

def verify_email_address(email: str) -> dict:
    """
    Performs multi-step email validation:
    1. Syntax verification (RFC standards via email-validator)
    2. Disposable domain check
    3. Role-based prefix check (flagged as risky)
    4. MX record lookup via DNS
    
    Status values:
    - 'valid': Valid syntax, non-disposable, non-role, verified active MX records.
    - 'risky': Role account (info@, support@) or unusual configuration.
    - 'invalid': Invalid syntax, non-existent domain, or disposable temp email.
    - 'unknown': DNS lookup timed out or unresolvable.
    """
    email_clean = email.lower().strip()
    
    # 1. Syntax check
    try:
        valid = validate_email(email_clean, check_deliverability=False)
        normalized_email = valid.normalized
        domain = valid.domain
    except EmailNotValidError as e:
        return {
            "email": email_clean,
            "status": "invalid",
            "details": f"Syntax error: {str(e)}",
            "mx_records_found": False
        }
    except Exception as e:
        return {
            "email": email_clean,
            "status": "invalid",
            "details": "Malformed email format",
            "mx_records_found": False
        }

    # 2. Check disposable domains
    if domain in DISPOSABLE_DOMAINS:
        return {
            "email": normalized_email,
            "status": "invalid",
            "details": f"Rejected disposable temporary email domain: {domain}",
            "mx_records_found": False
        }

    # 3. Check role account
    is_role_account = any(normalized_email.startswith(prefix) for prefix in ROLE_PREFIXES)

    # 4. Check DNS MX records
    try:
        answers = dns.resolver.resolve(domain, 'MX', lifetime=4.0)
        mx_hosts = [str(r.exchange).rstrip('.') for r in answers]
        if not mx_hosts:
            return {
                "email": normalized_email,
                "status": "invalid",
                "details": f"No active MX mail exchanger records found for domain {domain}",
                "mx_records_found": False
            }
        
        if is_role_account:
            return {
                "email": normalized_email,
                "status": "risky",
                "details": f"Role-based mailbox with valid MX host ({mx_hosts[0]})",
                "mx_records_found": True
            }

        return {
            "email": normalized_email,
            "status": "valid",
            "details": f"Valid syntax and active MX record host ({mx_hosts[0]}). Note: full mailbox existence requires mailbox-level SMTP ping.",
            "mx_records_found": True
        }
    except dns.resolver.NXDOMAIN:
        return {
            "email": normalized_email,
            "status": "invalid",
            "details": f"Domain {domain} does not exist (NXDOMAIN)",
            "mx_records_found": False
        }
    except (dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return {
            "email": normalized_email,
            "status": "invalid",
            "details": f"No mail server (MX) configured for {domain}",
            "mx_records_found": False
        }
    except Exception as e:
        # DNS timeout or network restriction in sandbox
        return {
            "email": normalized_email,
            "status": "unknown",
            "details": f"DNS MX check inconclusive or unreachable: {str(e)}",
            "mx_records_found": False
        }

