import pytest
from fastapi.testclient import TestClient


def test_create_category(client, superuser_token_headers):
    """Test creating a new category."""
    category_data = {
        "name": "Test Category",
        "slug": "test-category",
        "description": "This is a test category",
        "is_active": True
    }
    response = client.post(
        "/api/v1/categories",
        json=category_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == category_data["name"]
    assert data["description"] == category_data["description"]
    assert "id" in data


def test_create_category_duplicate_name(client, superuser_token_headers):
    """Test creating a category with a duplicate name."""
    # First create a category
    category_data = {
        "name": "Duplicate Category",
        "slug": "duplicate-category",
        "description": "This is a test category",
        "is_active": True
    }
    client.post(
        "/api/v1/categories",
        json=category_data,
        headers=superuser_token_headers
    )
    
    # Try to create another with the same name
    response = client.post(
        "/api/v1/categories",
        json=category_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 400
    assert "A category with slug 'duplicate-category' already exists" in response.json()["detail"]


def test_get_categories(client):
    """Test getting all categories."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "items" in data
    assert isinstance(data["items"], list)


def test_get_category_by_id(client, superuser_token_headers):
    """Test getting a category by ID."""
    # First create a category
    category_data = {
        "name": "Get Category Test",
        "slug": "get-category-test",
        "description": "This is a test category for getting by ID",
        "is_active": True
    }
    create_response = client.post(
        "/api/v1/categories",
        json=category_data,
        headers=superuser_token_headers
    )
    category_id = create_response.json()["id"]
    
    # Get the category by ID
    response = client.get(f"/api/v1/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == category_data["name"]
    assert data["id"] == category_id


def test_get_category_not_found(client):
    """Test getting a non-existent category."""
    response = client.get("/api/v1/categories/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert "Category not found" in response.json()["detail"]
    
    # Also test with an invalid UUID format
    response = client.get("/api/v1/categories/invalid-uuid")
    assert response.status_code == 422  # Validation error


def test_update_category(client, superuser_token_headers):
    """Test updating a category."""
    # First create a category
    category_data = {
        "name": "Update Category Test",
        "slug": "update-category-test",
        "description": "This is a test category for updating",
        "is_active": True
    }
    create_response = client.post(
        "/api/v1/categories",
        json=category_data,
        headers=superuser_token_headers
    )
    category_id = create_response.json()["id"]
    
    # Update the category
    update_data = {
        "name": "Updated Category Name",
        "slug": "updated-category-name",
        "description": "This is an updated description"
    }
    response = client.put(
        f"/api/v1/categories/{category_id}",
        json=update_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["id"] == category_id


def test_update_category_not_found(client, superuser_token_headers):
    """Test updating a non-existent category."""
    update_data = {
        "name": "Non-existent Category",
        "slug": "non-existent-category",
        "description": "This category doesn't exist"
    }
    response = client.put(
        "/api/v1/categories/00000000-0000-0000-0000-000000000000",
        json=update_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 404
    assert "Category not found" in response.json()["detail"]


def test_delete_category(client, superuser_token_headers):
    """Test deleting a category."""
    # First create a category
    category_data = {
        "name": "Delete Category Test",
        "slug": "delete-category-test",
        "description": "This is a test category for deleting",
        "is_active": True
    }
    create_response = client.post(
        "/api/v1/categories",
        json=category_data,
        headers=superuser_token_headers
    )
    category_id = create_response.json()["id"]
    
    # Delete the category
    response = client.delete(
        f"/api/v1/categories/{category_id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/v1/categories/{category_id}")
    assert get_response.status_code == 404


def test_delete_category_not_found(client, superuser_token_headers):
    """Test deleting a non-existent category."""
    response = client.delete(
        "/api/v1/categories/00000000-0000-0000-0000-000000000000",
        headers=superuser_token_headers
    )
    assert response.status_code == 404
    assert "Category not found" in response.json()["detail"]


def test_normal_user_cannot_create_category(client, normal_user_token_headers):
    """Test that a normal user cannot create a category."""
    category_data = {
        "name": "Unauthorized Category",
        "slug": "unauthorized-category",
        "description": "This should fail",
        "is_active": True
    }
    response = client.post(
        "/api/v1/categories",
        json=category_data,
        headers=normal_user_token_headers
    )
    assert response.status_code == 403
    assert "The user doesn't have enough privileges" in response.json()["detail"]


def test_category_cache_headers(client):
    """Test that category endpoints return appropriate cache headers."""
    # Test main categories endpoint
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    assert "Cache-Control" in response.headers
    assert "public" in response.headers["Cache-Control"]
    
    # Test category tree endpoint
    response = client.get("/api/v1/categories/tree")
    assert response.status_code == 200
    assert "Cache-Control" in response.headers
    assert "public" in response.headers["Cache-Control"]
    
    # Test root categories endpoint
    response = client.get("/api/v1/categories/root")
    assert response.status_code == 200
    assert "Cache-Control" in response.headers
    assert "public" in response.headers["Cache-Control"]
    
    # Test category by ID endpoint (using a UUID that likely doesn't exist)
    # Even though it returns 404, it should still have cache headers
    response = client.get("/api/v1/categories/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert "Cache-Control" in response.headers
    assert "public" in response.headers["Cache-Control"]
    
    # Test category by slug endpoint (using a slug that likely doesn't exist)
    response = client.get("/api/v1/categories/slug/nonexistent-category")
    assert response.status_code == 404
    assert "Cache-Control" in response.headers
    assert "public" in response.headers["Cache-Control"]