import pytest


class TestUserManagement:
    """Tests for user management functionality."""
    
    def test_create_user(self, client):
        """
        GIVEN valid user registration data
        WHEN a new user is created
        THEN the user should be created successfully
        """
        user_data = {
            "email": "test-create@example.com",
            "password": "Password123",
            "confirm_password": "Password123",
            "first_name": "Test",
            "last_name": "User"
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

    def test_login_user(self, client, db):
        """
        GIVEN a registered user
        WHEN the user logs in with valid credentials
        THEN authentication tokens should be returned
        """
        # First create a user
        user_data = {
            "email": "test-login@example.com",
            "password": "Password123",
            "confirm_password": "Password123",
            "first_name": "Login",
            "last_name": "Test"
        }
        client.post("/api/v1/auth/register", json=user_data)

        # Then login
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

    def test_get_current_user(self, client, normal_user_token_headers):
        """
        GIVEN an authenticated user
        WHEN the user requests their profile information
        THEN the user's profile should be returned
        """
        response = client.get("/api/v1/users/me", headers=normal_user_token_headers)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify user data
        assert data["email"] == "test@example.com"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert "id" in data
        assert "password_hash" not in data

    def test_update_current_user(self, client, normal_user_token_headers):
        """
        GIVEN an authenticated user
        WHEN the user updates their profile information
        THEN the user's profile should be updated successfully
        """
        update_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        response = client.put(
            "/api/v1/users/me", 
            json=update_data, 
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify updated data
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]
        assert "email" in data
        assert "id" in data


class TestUserAddresses:
    """Tests for user address management functionality."""
    
    def test_create_address(self, client, normal_user_token_headers):
        """
        GIVEN an authenticated user
        WHEN the user creates a new address
        THEN the address should be created successfully
        """
        address_data = {
            "first_name": "John",
            "last_name": "Doe",
            "street_address_1": "123 Main St",
            "city": "New York",
            "postal_code": "10001",
            "country": "USA",
            "address_type": "shipping",
            "is_default": True
        }
        response = client.post(
            "/api/v1/users/me/addresses",
            json=address_data,
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        
        # Verify address data
        assert data["first_name"] == address_data["first_name"]
        assert data["last_name"] == address_data["last_name"]
        assert data["street_address_1"] == address_data["street_address_1"]
        assert data["city"] == address_data["city"]
        assert data["postal_code"] == address_data["postal_code"]
        assert data["country"] == address_data["country"]
        assert data["address_type"] == address_data["address_type"]
        assert data["is_default"] == address_data["is_default"]
        assert "id" in data

    def test_get_addresses(self, client, normal_user_token_headers):
        """
        GIVEN an authenticated user with addresses
        WHEN the user requests their addresses
        THEN the user's addresses should be returned
        """
        # First create an address
        address_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "street_address_1": "456 Broadway",
            "city": "Chicago",
            "postal_code": "60601",
            "country": "USA",
            "address_type": "billing",
            "is_default": True
        }
        client.post(
            "/api/v1/users/me/addresses",
            json=address_data,
            headers=normal_user_token_headers
        )

        # Get all addresses
        response = client.get(
            "/api/v1/users/me/addresses", 
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify addresses data
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Find the address we just created
        created_address = next(
            (addr for addr in data if addr["street_address_1"] == address_data["street_address_1"]), 
            None
        )
        assert created_address is not None
        assert created_address["city"] == address_data["city"]
        assert created_address["address_type"] == address_data["address_type"]

    def test_update_address(self, client, normal_user_token_headers):
        """
        GIVEN an authenticated user with an address
        WHEN the user updates the address
        THEN the address should be updated successfully
        """
        # First create an address
        address_data = {
            "first_name": "Update",
            "last_name": "Test",
            "street_address_1": "789 Oak St",
            "city": "Seattle",
            "postal_code": "98101",
            "country": "USA",
            "address_type": "shipping",
            "is_default": True
        }
        create_response = client.post(
            "/api/v1/users/me/addresses",
            json=address_data,
            headers=normal_user_token_headers
        )
        address_id = create_response.json()["id"]

        # Update the address
        update_data = {
            "city": "Portland",
            "postal_code": "97201"
        }
        response = client.put(
            f"/api/v1/users/me/addresses/{address_id}",
            json=update_data,
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify updated data
        assert data["city"] == update_data["city"]
        assert data["postal_code"] == update_data["postal_code"]
        assert data["street_address_1"] == address_data["street_address_1"]
        assert data["first_name"] == address_data["first_name"]
        assert data["last_name"] == address_data["last_name"]
        assert "id" in data

    def test_delete_address(self, client, normal_user_token_headers):
        """
        GIVEN an authenticated user with an address
        WHEN the user deletes the address
        THEN the address should be deleted successfully
        """
        # First create an address
        address_data = {
            "first_name": "Delete",
            "last_name": "Test",
            "street_address_1": "321 Pine St",
            "city": "Miami",
            "postal_code": "33101",
            "country": "USA",
            "address_type": "billing",
            "is_default": True
        }
        create_response = client.post(
            "/api/v1/users/me/addresses",
            json=address_data,
            headers=normal_user_token_headers
        )
        address_id = create_response.json()["id"]

        # Delete the address
        response = client.delete(
            f"/api/v1/users/me/addresses/{address_id}",
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(
            f"/api/v1/users/me/addresses/{address_id}",
            headers=normal_user_token_headers
        )
        assert get_response.status_code == 404


class TestUserPermissions:
    """Tests for user permission functionality."""
    
    def test_superuser_access(self, client, superuser_token_headers):
        """
        GIVEN a superuser
        WHEN the superuser accesses admin endpoints
        THEN the superuser should have access
        """
        response = client.get("/api/v1/users", headers=superuser_token_headers)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify users data
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all("email" in user for user in data)
        assert all("id" in user for user in data)

    def test_normal_user_cannot_access_admin(self, client, normal_user_token_headers):
        """
        GIVEN a normal user
        WHEN the user tries to access admin endpoints
        THEN access should be denied
        """
        response = client.get("/api/v1/users", headers=normal_user_token_headers)
        
        # Verify response
        assert response.status_code == 403
        error_data = response.json()
        
        # Verify error message
        assert "detail" in error_data
        assert isinstance(error_data["detail"], str)
