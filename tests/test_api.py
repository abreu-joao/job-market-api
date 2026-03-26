import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_list_jobs_with_filter():
    response = client.get("/jobs?tech=Python")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) >= 1
    assert "Python" in data[0]["technology"]

def test_statistics_endpoint():
    response = client.get("/jobs/stats")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "overview" in data["data"]
    assert "technologies" in data["data"]