import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.database import get_db
from app.main import app  # tu entrypoint principal

# BD temporal (SQLite en memoria)
SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear todas las tablas en cada test
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    print("🔍 Tablas registradas:", Base.metadata.tables.keys())
    yield
    Base.metadata.drop_all(bind=engine)

# Override dependency de get_db
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    return TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    return TestingSessionLocal()
