import pytest
from fastapi.testclient import TestClient


class TestCategoryBasics:
    """Tests for basic category operations."""
    
    def test_get_categories(self, client):
        """
        GIVEN a database with categories
        WHEN a request is made to list all categories
        THEN a paginated list of categories should be returned
        """
        response = client.get("/api/v1/categories")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify data structure
        assert isinstance(data, dict)
        assert "items" in data
        assert isinstance(data["items"], list)
    
    def test_get_category_by_id(self, client, superuser_token_headers):
        """
        GIVEN a category in the database
        WHEN a request is made to get that category by ID
        THEN the category details should be returned
        """
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
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify category data
        assert data["name"] == category_data["name"]
        assert data["id"] == category_id
    
    def test_get_category_not_found(self, client):
        """
        GIVEN a non-existent category ID
        WHEN a request is made to get that category
        THEN a 404 Not Found response should be returned
        """
        response = client.get("/api/v1/categories/00000000-0000-0000-0000-000000000000")
        
        # Verify response
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]
        
        # Also test with an invalid UUID format
        response = client.get("/api/v1/categories/invalid-uuid")
        assert response.status_code == 422  # Validation error


class TestCategoryAdministration:
    """Tests for category administration operations."""
    
    def test_create_category(self, client, superuser_token_headers):
        """
        GIVEN a superuser with valid category data
        WHEN a request is made to create a new category
        THEN the category should be created successfully
        """
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
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        
        # Verify category data
        assert data["name"] == category_data["name"]
        assert data["description"] == category_data["description"]
        assert "id" in data
    
    def test_create_category_duplicate_name(self, client, superuser_token_headers):
        """
        GIVEN a superuser and an existing category
        WHEN a request is made to create a category with the same slug
        THEN a 400 Bad Request response should be returned
        """
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
        
        # Verify response
        assert response.status_code == 400
        assert "A category with slug 'duplicate-category' already exists" in response.json()["detail"]


    def test_update_category(self, client, superuser_token_headers):
        """
        GIVEN a superuser and an existing category
        WHEN a request is made to update the category
        THEN the category should be updated successfully
        """
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
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify updated data
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["id"] == category_id
    
    def test_update_category_not_found(self, client, superuser_token_headers):
        """
        GIVEN a superuser and a non-existent category ID
        WHEN a request is made to update the category
        THEN a 404 Not Found response should be returned
        """
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
        
        # Verify response
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]
    
    def test_delete_category(self, client, superuser_token_headers):
        """
        GIVEN a superuser and an existing category
        WHEN a request is made to delete the category
        THEN the category should be deleted successfully
        """
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
        
        # Verify response
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/categories/{category_id}")
        assert get_response.status_code == 404
    
    def test_delete_category_not_found(self, client, superuser_token_headers):
        """
        GIVEN a superuser and a non-existent category ID
        WHEN a request is made to delete the category
        THEN a 404 Not Found response should be returned
        """
        response = client.delete(
            "/api/v1/categories/00000000-0000-0000-0000-000000000000",
            headers=superuser_token_headers
        )
        
        # Verify response
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]


class TestCategoryPermissions:
    """Tests for category permission functionality."""
    
    def test_normal_user_cannot_create_category(self, client, normal_user_token_headers):
        """
        GIVEN a normal user
        WHEN the user tries to create a category
        THEN access should be denied with a 403 Forbidden response
        """
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
        
        # Verify response
        assert response.status_code == 403
        assert "The user doesn't have enough privileges" in response.json()["detail"]