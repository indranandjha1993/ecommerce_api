import pytest
from fastapi.testclient import TestClient


class TestBrandBasics:
    """Tests for basic brand operations."""
    
    def test_get_brands(self, client):
        """
        GIVEN a database with brands
        WHEN a request is made to list all brands
        THEN a paginated list of brands should be returned
        """
        response = client.get("/api/v1/brands")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify data structure
        assert isinstance(data, dict)
        assert "items" in data
        assert isinstance(data["items"], list)
    
    def test_get_brand_by_id(self, client, superuser_token_headers):
        """
        GIVEN a brand in the database
        WHEN a request is made to get that brand by ID
        THEN the brand details should be returned
        """
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
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify brand data
        assert data["name"] == brand_data["name"]
        assert data["id"] == brand_id
    
    def test_get_brand_not_found(self, client):
        """
        GIVEN a non-existent brand ID
        WHEN a request is made to get that brand
        THEN a 404 Not Found response should be returned
        """
        # Use a valid UUID format that doesn't exist in the database
        response = client.get("/api/v1/brands/00000000-0000-0000-0000-000000000000")
        
        # Verify response
        assert response.status_code == 404
        assert "Brand not found" in response.json()["detail"]
        
        # Also test with an invalid UUID format
        response = client.get("/api/v1/brands/invalid-uuid")
        assert response.status_code == 422  # Validation error


class TestBrandAdministration:
    """Tests for brand administration operations."""
    
    def test_create_brand(self, client, superuser_token_headers):
        """
        GIVEN a superuser with valid brand data
        WHEN a request is made to create a new brand
        THEN the brand should be created successfully
        """
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
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        
        # Verify brand data
        assert data["name"] == brand_data["name"]
        assert data["description"] == brand_data["description"]
        assert data["website"] == brand_data["website"]
        assert "id" in data
    
    def test_create_brand_duplicate_name(self, client, superuser_token_headers):
        """
        GIVEN a superuser and an existing brand
        WHEN a request is made to create a brand with the same slug
        THEN a 400 Bad Request response should be returned
        """
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
        
        # Verify response
        assert response.status_code == 400
        assert "A brand with slug 'duplicate-brand' already exists" in response.json()["detail"]


    def test_update_brand(self, client, superuser_token_headers):
        """
        GIVEN a superuser and an existing brand
        WHEN a request is made to update the brand
        THEN the brand should be updated successfully
        """
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
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify updated data
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["website"] == update_data["website"]
        assert data["id"] == brand_id
    
    def test_update_brand_not_found(self, client, superuser_token_headers):
        """
        GIVEN a superuser and a non-existent brand ID
        WHEN a request is made to update the brand
        THEN a 404 Not Found response should be returned
        """
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
        
        # Verify response
        assert response.status_code == 404
        assert "Brand not found" in response.json()["detail"]
    
    def test_delete_brand(self, client, superuser_token_headers):
        """
        GIVEN a superuser and an existing brand
        WHEN a request is made to delete the brand
        THEN the brand should be deleted successfully
        """
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
        
        # Verify response
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/brands/{brand_id}")
        assert get_response.status_code == 404
    
    def test_delete_brand_not_found(self, client, superuser_token_headers):
        """
        GIVEN a superuser and a non-existent brand ID
        WHEN a request is made to delete the brand
        THEN a 404 Not Found response should be returned
        """
        response = client.delete(
            "/api/v1/brands/00000000-0000-0000-0000-000000000000",
            headers=superuser_token_headers
        )
        
        # Verify response
        assert response.status_code == 404
        assert "Brand not found" in response.json()["detail"]


class TestBrandPermissions:
    """Tests for brand permission functionality."""
    
    def test_normal_user_cannot_create_brand(self, client, normal_user_token_headers):
        """
        GIVEN a normal user
        WHEN the user tries to create a brand
        THEN access should be denied with a 403 Forbidden response
        """
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
        
        # Verify response
        assert response.status_code == 403
        assert "The user doesn't have enough privileges" in response.json()["detail"]