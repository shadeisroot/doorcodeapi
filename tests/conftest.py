import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import Base, get_db
from main import app


engine = create_engine(settings.test_database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Override the app's get_db to use the test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


# 3. Fixture: fresh tables before each test, dropped after
@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)   # setup: create tables
    yield TestClient(app)                     # the test runs here
    Base.metadata.drop_all(bind=engine)       # teardown: wipe tables