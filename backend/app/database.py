import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("leadshark.database")

Base = declarative_base()

def create_app_engine():
    db_url = settings.get_database_url()
    
    if db_url.startswith("sqlite"):
        logger.info("Initializing SQLite database engine (development/local mode).")
        return create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True
        )
    else:
        logger.info("Initializing PostgreSQL database engine with connection pooling.")
        return create_engine(
            db_url,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 10}
        )

engine = create_app_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

