import pytest
from fastapi.testclient import TestClient


def test_register_user_success(client):
    """Test successful user registration."""
    user_data = {
        "email": "register-test@example.com",
        "password": "StrongPass123!",
        "confirm_password": "StrongPass123!",
        "first_name": "Register",
        "last_name": "Test"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data


def test_register_user_email_exists(client, db):
    """Test registration with an email that already exists."""
    # First register a user
    user_data = {
        "email": "duplicate@example.com",
        "password": "StrongPass123!",
        "confirm_password": "StrongPass123!",
        "first_name": "Duplicate",
        "last_name": "User"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Try to register with the same email
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_register_user_password_mismatch(client):
    """Test registration with mismatched passwords."""
    user_data = {
        "email": "mismatch@example.com",
        "password": "StrongPass123!",
        "confirm_password": "DifferentPass456!",
        "first_name": "Password",
        "last_name": "Mismatch"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Passwords do not match" in response.json()["detail"]


def test_register_user_weak_password(client):
    """Test registration with a weak password."""
    user_data = {
        "email": "weakpass@example.com",
        "password": "123456",  # Too simple
        "confirm_password": "123456",
        "first_name": "Weak",
        "last_name": "Password"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Password is too weak" in response.json()["detail"]


def test_login_success(client, db):
    """Test successful login."""
    # First register a user
    user_data = {
        "email": "login-success@example.com",
        "password": "StrongPass123!",
        "confirm_password": "StrongPass123!",
        "first_name": "Login",
        "last_name": "Success"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Login with correct credentials
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, db):
    """Test login with invalid credentials."""
    # First register a user
    user_data = {
        "email": "login-fail@example.com",
        "password": "StrongPass123!",
        "confirm_password": "StrongPass123!",
        "first_name": "Login",
        "last_name": "Fail"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Login with wrong password
    login_data = {
        "username": user_data["email"],
        "password": "WrongPassword123!"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_nonexistent_user(client):
    """Test login with a non-existent user."""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "AnyPassword123!"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_refresh_token(client, normal_user_token_headers):
    """Test refreshing an access token."""
    # First login to get a refresh token
    user_data = {
        "email": "refresh-test@example.com",
        "password": "StrongPass123!",
        "confirm_password": "StrongPass123!",
        "first_name": "Refresh",
        "last_name": "Test"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    refresh_token = login_response.json()["refresh_token"]
    
    # Use the refresh token to get a new access token
    refresh_data = {
        "refresh_token": refresh_token
    }
    response = client.post("/api/v1/auth/refresh", json=refresh_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_token_invalid(client):
    """Test refreshing with an invalid token."""
    refresh_data = {
        "refresh_token": "invalid_token_here"
    }
    response = client.post("/api/v1/auth/refresh", json=refresh_data)
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]