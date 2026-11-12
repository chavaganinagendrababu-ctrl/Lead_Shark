from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, SessionLocal, get_db
from app.models import *  # ensure all models are registered
from app.utils.seeding import seed_database
from app.routes import auth, dashboard, leads, discovery, campaigns, compliance, audit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("leadshark")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed default accounts/data
    logger.info("Initializing Lead Shark database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
        logger.info("Database seeding verified.")
    finally:
        db.close()
    yield
    logger.info("Lead Shark backend shutting down.")

app = FastAPI(
    title="Lead Shark API",
    description="Compliant Lead Discovery & Outreach Management Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Production CORS: Uses origin regex to dynamically reflect the requesting origin,
# ensuring full compatibility with Vercel production domains, preview deployments, and localhost
# without triggering wildcard credential restriction errors in modern web browsers.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Secure Global Exception Handler: Protects against stack trace leakage
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled system exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please contact the compliance administrator."}
    )

# Root Index Endpoint
@app.get("/")
@app.get("/api")
def root():
    return {
        "service": "Lead Shark Backend API",
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/health"
    }

# Health Check Endpoint
@app.get("/health")
@app.get("/api/health")
def health_check():
    db_connected = True
    provisioned_users = 0
    try:
        from app.models.user import User
        db = SessionLocal()
        try:
            provisioned_users = db.query(User).count()
        finally:
            db.close()
    except Exception as e:
        db_connected = False
        logger.error(f"Database health check error: {str(e)}")

    return {
        "status": "healthy" if db_connected else "degraded",
        "service": "Lead Shark Backend",
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_connected else "disconnected",
        "users_provisioned": provisioned_users >= 3,
        "users_count": provisioned_users
    }

# API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(auth.router)  # Dual-mount auth routes for root level compatibility
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(leads.router, prefix=settings.API_V1_STR)
app.include_router(discovery.router, prefix=settings.API_V1_STR)
app.include_router(campaigns.router, prefix=settings.API_V1_STR)
app.include_router(compliance.router)
app.include_router(audit.router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)

