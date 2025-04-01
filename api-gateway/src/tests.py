import pytest
import json
from unittest.mock import patch, MagicMock
from main import app
from fastapi.testclient import TestClient
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
def test_register_user_success(test_data, test_id, monkeypatch):
    with patch('main.http_client.request') as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.content = json.dumps(test_data["test_user_response"]).encode()
        mock_response.headers = {"content-type": "application/json"}
        mock_request.return_value = mock_response

        response = client.post("/api/v1/auth/register", json=test_data["test_user"])
        
        assert response.status_code == 201
        assert response.json() == test_data["test_user_response"]
        
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        assert call_args["method"] == "POST"
        assert call_args["url"] == "/api/v1/auth/register"

@pytest.mark.parametrize("test_id", ["login_user_success"])
def test_login_user_success(test_data, test_id, monkeypatch):
    with patch('main.http_client.request') as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = json.dumps(test_data["test_auth_response"]).encode()
        mock_response.headers = {"content-type": "application/json"}
        mock_request.return_value = mock_response

        response = client.post("/api/v1/auth/login", json={
            "login": test_data["test_user"]["login"],
            "password": test_data["test_user"]["password"]
        })
        
        assert response.status_code == 200
        assert response.json() == test_data["test_auth_response"]
        
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        assert call_args["method"] == "POST"
        assert call_args["url"] == "/api/v1/auth/login"

@pytest.mark.parametrize("test_id", ["proxy_request_error"])
def test_proxy_request_error(test_data, test_id, monkeypatch):
    with patch('main.http_client.request') as mock_request:
        mock_request.side_effect = Exception("Connection error")

        response = client.post("/api/v1/auth/register", json=test_data["test_user"])
        
        assert response.status_code == 503
        assert "Error communicating with user service" in response.json()["detail"]
