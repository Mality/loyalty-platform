import pytest
import json
from fastapi.testclient import TestClient
from src.main import app
from uuid import uuid4
from datetime import datetime, timedelta

client = TestClient(app)

@pytest.fixture
def test_data():
    test_user = {
        "login": "test_user",
        "password": "Password123!",
        "email": "test@example.com"
    }
    test_user_response = {
        "id": str(uuid4()),
        "login": "test_user",
        "email": "test@example.com",
        "createdAt": datetime.now().isoformat()
    }
    test_auth_response = {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "expiresAt": (datetime.now() + timedelta(hours=2)).isoformat(),
        "user": test_user_response
    }
    return {
        "test_user": test_user,
        "test_user_response": test_user_response,
        "test_auth_response": test_auth_response
    }

@pytest.mark.parametrize("test_id", ["register_user_success"])
def test_register_user_success(test_data, test_id):
    response = client.post("/api/v1/auth/register", json=test_data["test_user"])
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["login"] == test_data["test_user"]["login"]
    assert response.json()["email"] == test_data["test_user"]["email"]
    assert "createdAt" in response.json()

@pytest.mark.parametrize("test_id", ["register_user_already_exists"])
def test_register_user_already_exists(test_data, test_id):
    client.post("/api/v1/auth/register", json=test_data["test_user"])
    
    response = client.post("/api/v1/auth/register", json=test_data["test_user"])
    assert response.status_code == 409
    assert "already exists" in response.json()["message"].lower()

@pytest.mark.parametrize("test_id", ["login_user_success"])
def test_login_user_success(test_data, test_id):
    client.post("/api/v1/auth/register", json=test_data["test_user"])
    
    response = client.post("/api/v1/auth/login", json={
        "login": test_data["test_user"]["login"],
        "password": test_data["test_user"]["password"]
    })
    assert response.status_code == 200
    assert "token" in response.json()
    assert "expiresAt" in response.json()
    assert "user" in response.json()
    assert response.json()["user"]["login"] == test_data["test_user"]["login"]

@pytest.mark.parametrize("test_id", ["login_user_invalid_credentials"])
def test_login_user_invalid_credentials(test_data, test_id):
    client.post("/api/v1/auth/register", json=test_data["test_user"])
    
    response = client.post("/api/v1/auth/login", json={
        "login": test_data["test_user"]["login"],
        "password": "wrong_password"
    })
    assert response.status_code == 401
    assert "invalid" in response.json()["message"].lower()

@pytest.mark.parametrize("test_id", ["get_user_by_id"])
def test_get_user_by_id(test_data, test_id):
    register_response = client.post("/api/v1/auth/register", json=test_data["test_user"])
    user_id = register_response.json()["id"]
    
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["login"] == test_data["test_user"]["login"]
    assert response.json()["email"] == test_data["test_user"]["email"]

@pytest.mark.parametrize("test_id", ["get_user_not_found"])
def test_get_user_not_found(test_data, test_id):
    user_id = str(uuid4())
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["message"].lower()
