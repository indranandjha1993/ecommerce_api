import pytest
from fastapi.testclient import TestClient


def test_create_brand(client, superuser_token_headers):
    """Test creating a new brand."""
    brand_data = {
        "name": "Test Brand",
        "slug": "test-brand",
        "description": "This is a test brand",
        "website": "https://testbrand.com",
        "is_active": True
    }
    response = client.post(
        "/api/v1/brands",
        json=brand_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == brand_data["name"]
    assert data["description"] == brand_data["description"]
    assert data["website"] == brand_data["website"]
    assert "id" in data


def test_create_brand_duplicate_name(client, superuser_token_headers):
    """Test creating a brand with a duplicate name."""
    # First create a brand
    brand_data = {
        "name": "Duplicate Brand",
        "slug": "duplicate-brand",
        "description": "This is a test brand",
        "website": "https://duplicatebrand.com",
        "is_active": True
    }
    client.post(
        "/api/v1/brands",
        json=brand_data,
        headers=superuser_token_headers
    )
    
    # Try to create another with the same name
    response = client.post(
        "/api/v1/brands",
        json=brand_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 400
    assert "A brand with slug 'duplicate-brand' already exists" in response.json()["detail"]


def test_get_brands(client):
    """Test getting all brands."""
    response = client.get("/api/v1/brands")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "items" in data
    assert isinstance(data["items"], list)


def test_get_brand_by_id(client, superuser_token_headers):
    """Test getting a brand by ID."""
    # First create a brand
    brand_data = {
        "name": "Get Brand Test",
        "slug": "get-brand-test",
        "description": "This is a test brand for getting by ID",
        "website": "https://getbrandtest.com",
        "is_active": True
    }
    create_response = client.post(
        "/api/v1/brands",
        json=brand_data,
        headers=superuser_token_headers
    )
    brand_id = create_response.json()["id"]
    
    # Get the brand by ID
    response = client.get(f"/api/v1/brands/{brand_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == brand_data["name"]
    assert data["id"] == brand_id


def test_get_brand_not_found(client):
    """Test getting a non-existent brand."""
    # Use a valid UUID format that doesn't exist in the database
    response = client.get("/api/v1/brands/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert "Brand not found" in response.json()["detail"]


def test_update_brand(client, superuser_token_headers):
    """Test updating a brand."""
    # First create a brand
    brand_data = {
        "name": "Update Brand Test",
        "slug": "update-brand-test",
        "description": "This is a test brand for updating",
        "website": "https://updatebrandtest.com",
        "is_active": True
    }
    create_response = client.post(
        "/api/v1/brands",
        json=brand_data,
        headers=superuser_token_headers
    )
    brand_id = create_response.json()["id"]
    
    # Update the brand
    update_data = {
        "name": "Updated Brand Name",
        "slug": "updated-brand-name",
        "description": "This is an updated description",
        "website": "https://updatedbrand.com"
    }
    response = client.put(
        f"/api/v1/brands/{brand_id}",
        json=update_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["website"] == update_data["website"]
    assert data["id"] == brand_id


def test_update_brand_not_found(client, superuser_token_headers):
    """Test updating a non-existent brand."""
    update_data = {
        "name": "Non-existent Brand",
        "slug": "non-existent-brand",
        "description": "This brand doesn't exist",
        "website": "https://nonexistent.com"
    }
    response = client.put(
        "/api/v1/brands/00000000-0000-0000-0000-000000000000",
        json=update_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 404
    assert "Brand not found" in response.json()["detail"]


def test_delete_brand(client, superuser_token_headers):
    """Test deleting a brand."""
    # First create a brand
    brand_data = {
        "name": "Delete Brand Test",
        "slug": "delete-brand-test",
        "description": "This is a test brand for deleting",
        "website": "https://deletebrandtest.com",
        "is_active": True
    }
    create_response = client.post(
        "/api/v1/brands",
        json=brand_data,
        headers=superuser_token_headers
    )
    brand_id = create_response.json()["id"]
    
    # Delete the brand
    response = client.delete(
        f"/api/v1/brands/{brand_id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/v1/brands/{brand_id}")
    assert get_response.status_code == 404


def test_delete_brand_not_found(client, superuser_token_headers):
    """Test deleting a non-existent brand."""
    response = client.delete(
        "/api/v1/brands/00000000-0000-0000-0000-000000000000",
        headers=superuser_token_headers
    )
    assert response.status_code == 404
    assert "Brand not found" in response.json()["detail"]


def test_normal_user_cannot_create_brand(client, normal_user_token_headers):
    """Test that a normal user cannot create a brand."""
    brand_data = {
        "name": "Unauthorized Brand",
        "slug": "unauthorized-brand",
        "description": "This should fail",
        "website": "https://unauthorized.com",
        "is_active": True
    }
    response = client.post(
        "/api/v1/brands",
        json=brand_data,
        headers=normal_user_token_headers
    )
    assert response.status_code == 403
    assert "The user doesn't have enough privileges" in response.json()["detail"]