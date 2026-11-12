import os
import re
import logging
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("leadshark.config")

# Common placeholder hostnames that should never be used in a real database connection
PLACEHOLDER_HOSTNAMES = {
    "hostname",
    "your-db-host",
    "your_host",
    "example.com",
    "placeholder",
    "db_host"
}

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    PROJECT_NAME: str = "Lead Shark"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "leadshark-super-secure-production-ready-jwt-secret-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower().strip()
    PORT: int = int(os.getenv("PORT", 8000))

    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://leadshark.vercel.app",
        os.getenv("FRONTEND_URL", "http://localhost:5173")
    ]
    
    # Initial Admin / Seed accounts
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@leadshark.io")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "AdminLeadShark2026!")
    ADMIN_NAME: str = "LeadShark Admin"

    REVIEWER_EMAIL: str = os.getenv("REVIEWER_EMAIL", "reviewer@leadshark.io")
    REVIEWER_PASSWORD: str = os.getenv("REVIEWER_PASSWORD", "ReviewerLeadShark2026!")
    REVIEWER_NAME: str = "Compliance Reviewer"

    SALES_EMAIL: str = os.getenv("SALES_EMAIL", "sales@leadshark.io")
    SALES_PASSWORD: str = os.getenv("SALES_PASSWORD", "SalesLeadShark2026!")
    SALES_NAME: str = "Sales Representative"

    def get_database_url(self) -> str:
        """
        Validates, normalizes, and returns the active database connection URL.
        - In production, enforces a valid PostgreSQL connection string and rejects placeholders.
        - In development, defaults to SQLite if DATABASE_URL is not set.
        - Automatically normalizes postgres:// or postgresql:// to postgresql+psycopg2://.
        """
        raw_url = (self.DATABASE_URL or "").strip()
        is_prod = self.ENVIRONMENT == "production"

        if not raw_url:
            if is_prod:
                raise ValueError(
                    "DATABASE_URL environment variable is missing in production! "
                    "Render requires a valid PostgreSQL connection string. "
                    "Please navigate to Render Dashboard > Web Service > Environment, "
                    "add 'DATABASE_URL', and paste your Render or Supabase PostgreSQL connection URL."
                )
            return "sqlite:///./leadshark.db"

        # Check for placeholder hosts
        for ph in PLACEHOLDER_HOSTNAMES:
            if f"@{ph}" in raw_url or f"://{ph}" in raw_url:
                raise ValueError(
                    f"DATABASE_URL contains placeholder host '{ph}' ('{raw_url}')! "
                    "This is an example placeholder copied from .env.example. "
                    "In your Render Dashboard > Web Service > Environment, update DATABASE_URL "
                    "with your real PostgreSQL connection URL (e.g. from Render PostgreSQL or Supabase)."
                )

        # Normalize driver for PostgreSQL
        normalized_url = raw_url
        if normalized_url.startswith("postgres://"):
            normalized_url = normalized_url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif normalized_url.startswith("postgresql://") and not normalized_url.startswith("postgresql+"):
            normalized_url = normalized_url.replace("postgresql://", "postgresql+psycopg2://", 1)

        # In production, disallow sqlite
        if is_prod and normalized_url.startswith("sqlite"):
            raise ValueError(
                "SQLite is not permitted in production environment! "
                "Please configure a valid PostgreSQL connection string in the DATABASE_URL environment variable."
            )

        return normalized_url

settings = Settings()
