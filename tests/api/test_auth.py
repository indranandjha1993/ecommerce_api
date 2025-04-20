import pytest
from fastapi.testclient import TestClient


class TestUserRegistration:
    """Tests for user registration functionality."""
    
    def test_register_user_success(self, client):
        """
        GIVEN valid user registration data
        WHEN a user registers with valid information
        THEN the user should be created successfully
        """
        user_data = {
            "email": "register-test@example.com",
            "password": "StrongPass123!",
            "confirm_password": "StrongPass123!",
            "first_name": "Register",
            "last_name": "Test"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        
        # Verify user data
        assert data["email"] == user_data["email"]
        assert data["first_name"] == user_data["first_name"]
        assert data["last_name"] == user_data["last_name"]
        assert "id" in data
        assert "password_hash" not in data  # Ensure password is not returned

    def test_register_user_email_exists(self, client, db):
        """
        GIVEN an email that is already registered
        WHEN a user tries to register with that email
        THEN an error should be returned
        """
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
        
        # Verify response
        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data
        assert "Email already registered" in error_data["detail"]

    def test_register_user_password_mismatch(self, client):
        """
        GIVEN registration data with mismatched passwords
        WHEN a user tries to register with those passwords
        THEN an error should be returned
        """
        user_data = {
            "email": "mismatch@example.com",
            "password": "StrongPass123!",
            "confirm_password": "DifferentPass456!",
            "first_name": "Password",
            "last_name": "Mismatch"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Verify response
        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data
        assert "Passwords do not match" in error_data["detail"]

    def test_register_user_weak_password(self, client):
        """
        GIVEN registration data with a weak password
        WHEN a user tries to register with that password
        THEN an error should be returned
        """
        user_data = {
            "email": "weakpass@example.com",
            "password": "123456",  # Too simple
            "confirm_password": "123456",
            "first_name": "Weak",
            "last_name": "Password"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Verify response - accept either 400 (custom validation) or 422 (Pydantic validation)
        assert response.status_code in [400, 422]
        
        # Check for error message - could be from Pydantic or custom validation
        response_data = response.json()
        
        if response.status_code == 400:
            # Custom validation
            assert "Password is too weak" in response_data["detail"]
        else:
            # Pydantic validation
            assert "detail" in response_data
            # The error could be in different formats depending on Pydantic version
            detail = response_data["detail"]
            if isinstance(detail, list):
                # It's a list of validation errors
                error_messages = [str(err).lower() for err in detail]
                assert any("password" in msg and ("short" in msg or "length" in msg) for msg in error_messages)
            else:
                # It's a string
                assert "password" in str(detail).lower() and ("short" in str(detail).lower() or "length" in str(detail).lower())


class TestUserAuthentication:
    """Tests for user authentication functionality."""
    
    def test_login_success(self, client, db):
        """
        GIVEN a registered user with valid credentials
        WHEN the user logs in with those credentials
        THEN the user should receive valid authentication tokens
        """
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
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify token data
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, db):
        """
        GIVEN a registered user
        WHEN the user logs in with incorrect password
        THEN an authentication error should be returned
        """
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
        
        # Verify response
        assert response.status_code == 401
        error_data = response.json()
        assert "detail" in error_data
        assert "Incorrect email or password" in error_data["detail"]

    def test_login_nonexistent_user(self, client):
        """
        GIVEN a non-existent user
        WHEN someone tries to log in with that user's email
        THEN an authentication error should be returned
        """
        login_data = {
            "username": "nonexistent@example.com",
            "password": "AnyPassword123!"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        # Verify response
        assert response.status_code == 401
        error_data = response.json()
        assert "detail" in error_data
        assert "Incorrect email or password" in error_data["detail"]


class TestTokenManagement:
    """Tests for token management functionality."""
    
    def test_refresh_token_success(self, client):
        """
        GIVEN a valid refresh token
        WHEN the user requests a new access token
        THEN a new access token should be issued
        """
        # First register a user
        user_data = {
            "email": "refresh-test@example.com",
            "password": "StrongPass123!",
            "confirm_password": "StrongPass123!",
            "first_name": "Refresh",
            "last_name": "Test"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Login to get a refresh token
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
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify token data
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client):
        """
        GIVEN an invalid refresh token
        WHEN the user tries to get a new access token
        THEN an error should be returned
        """
        refresh_data = {
            "refresh_token": "invalid_token_here"
        }
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        # Verify response - accept either 401 (auth error) or 422 (validation error)
        assert response.status_code in [401, 422]
        
        # Check error message
        error_detail = response.json().get("detail", "")
        if isinstance(error_detail, str):
            assert "Invalid token" in error_detail or "token" in error_detail.lower()
        else:
            # Handle case where detail might be a list of validation errors
            assert any("token" in str(err).lower() for err in error_detail)