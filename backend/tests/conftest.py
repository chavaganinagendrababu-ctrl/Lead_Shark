import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from fastapi.testclient import TestClient

import app.database as db_module
from app.main import app
from app.utils.seeding import seed_database

test_engine = create_engine("sqlite:///./test_leadshark.db", connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Monkey-patch database module for testing
db_module.engine = test_engine
db_module.SessionLocal = TestSessionLocal

@pytest.fixture(scope="session")
def client():
    # Setup test schema
    db_module.Base.metadata.drop_all(bind=test_engine)
    db_module.Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    seed_database(db)
    db.close()

    def override_get_db():
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[db_module.get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

    app.dependency_overrides.clear()
    db_module.Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_leadshark.db"):
        try:
            os.remove("./test_leadshark.db")
        except Exception:
            pass
