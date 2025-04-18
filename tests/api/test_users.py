def test_create_user(client):
    """
    Test creating a new user.
    """
    user_data = {
        "email": "test-create@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert "id" in data
    assert "password_hash" not in data


def test_login_user(client, db):
    """
    Test logging in a user.
    """
    # First create a user
    user_data = {
        "email": "test-login@example.com",
        "password": "password123",
        "confirm_password": "password123",
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
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user(client, normal_user_token_headers):
    """
    Test getting the current user.
    """
    response = client.get("/api/v1/users/me", headers=normal_user_token_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"
    assert "id" in data


def test_update_current_user(client, normal_user_token_headers):
    """
    Test updating the current user.
    """
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }
    response = client.put("/api/v1/users/me", json=update_data, headers=normal_user_token_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["first_name"] == update_data["first_name"]
    assert data["last_name"] == update_data["last_name"]


def test_create_address(client, normal_user_token_headers):
    """
    Test creating an address for the current user.
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
    assert response.status_code == 201

    data = response.json()
    assert data["street_address_1"] == address_data["street_address_1"]
    assert data["city"] == address_data["city"]
    assert data["is_default"] == address_data["is_default"]
    assert "id" in data


def test_get_addresses(client, normal_user_token_headers):
    """
    Test getting addresses for the current user.
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
    response = client.get("/api/v1/users/me/addresses", headers=normal_user_token_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["street_address_1"] == address_data["street_address_1"]


def test_update_address(client, normal_user_token_headers):
    """
    Test updating an address for the current user.
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
    assert response.status_code == 200

    data = response.json()
    assert data["city"] == update_data["city"]
    assert data["postal_code"] == update_data["postal_code"]
    assert data["street_address_1"] == address_data["street_address_1"]


def test_delete_address(client, normal_user_token_headers):
    """
    Test deleting an address for the current user.
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
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(
        f"/api/v1/users/me/addresses/{address_id}",
        headers=normal_user_token_headers
    )
    assert get_response.status_code == 404


def test_superuser_access(client, superuser_token_headers):
    """
    Test that a superuser can access admin endpoints.
    """
    response = client.get("/api/v1/users", headers=superuser_token_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_normal_user_cannot_access_admin(client, normal_user_token_headers):
    """
    Test that a normal user cannot access admin endpoints.
    """
    response = client.get("/api/v1/users", headers=normal_user_token_headers)
    assert response.status_code == 403
