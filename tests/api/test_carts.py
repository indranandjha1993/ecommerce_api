import pytest
from fastapi.testclient import TestClient


class TestCartBasics:
    """Tests for basic cart functionality."""
    
    def test_create_cart(self, client, normal_user_token_headers):
        """
        GIVEN an authenticated user
        WHEN the user requests a cart
        THEN a new cart should be created if one doesn't exist
        """
        response = client.get(
            "/api/v1/carts",
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify cart data
        assert "id" in data
        assert data["is_active"] is True
        assert len(data["items"]) == 0
    
    def test_get_active_cart(self, client, normal_user_token_headers):
        """
        GIVEN an authenticated user with an existing cart
        WHEN the user requests their cart
        THEN the active cart should be returned
        """
        # Get the active cart (will create one if it doesn't exist)
        response = client.get(
            "/api/v1/carts",
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify cart data
        assert "id" in data
        assert data["is_active"] is True
    
    def test_cart_authentication_and_validation(self, client, normal_user_token_headers):
        """
        GIVEN various cart request scenarios
        WHEN requests are made with different authentication states
        THEN appropriate responses should be returned
        """
        # Scenario 1: Try to get a cart without authentication or session ID
        response = client.get("/api/v1/carts")
        
        # Verify response
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
        
        # Scenario 2: Create a cart with authentication
        response = client.get("/api/v1/carts", headers=normal_user_token_headers)
        
        # Verify response
        assert response.status_code == 200
        cart_data = response.json()
        assert "id" in cart_data
        
        # Scenario 3: Test validation error with invalid UUID format
        response = client.put(
            "/api/v1/carts/items/invalid-uuid", 
            json={"quantity": 1},
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 422  # Validation error for UUID format


class TestCartItems:
    """Tests for cart item operations."""
    
    def test_add_item_to_cart(self, client, normal_user_token_headers, db):
        """
        GIVEN an authenticated user with a cart and a valid product
        WHEN the user adds the product to their cart
        THEN the product should be added successfully
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        import uuid
        
        # Create test category
        category = Category(
            id=uuid.uuid4(),
            name="Test Category",
            slug="test-category",
            description="Test category for cart tests",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=uuid.uuid4(),
            name="Test Brand",
            slug="test-brand",
            description="Test brand for cart tests",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=uuid.uuid4(),
            name="Test Product",
            slug="test-product",
            description="Test product for cart tests",
            price=99.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True
        )
        db.add(product)
        db.commit()
        
        # Get or create a cart
        cart_response = client.get(
            "/api/v1/carts",
            headers=normal_user_token_headers
        )
        cart_id = cart_response.json()["id"]
        
        # Add item to cart
        item_data = {
            "product_id": str(product.id),
            "quantity": 2
        }
        response = client.post(
            "/api/v1/carts/items",
            json=item_data,
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        
        # Verify item data
        assert data["product_id"] == str(product.id)
        assert data["quantity"] == 2
        assert "id" in data
    
    def test_add_item_to_cart_invalid_product(self, client, normal_user_token_headers):
        """
        GIVEN an authenticated user with a cart
        WHEN the user tries to add a non-existent product to their cart
        THEN an error should be returned
        """
        # Get or create a cart
        client.get(
            "/api/v1/carts",
            headers=normal_user_token_headers
        )
        
        # Add non-existent product to cart
        item_data = {
            "product_id": "00000000-0000-0000-0000-000000000000",
            "quantity": 1
        }
        response = client.post(
            "/api/v1/carts/items",
            json=item_data,
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]


    def test_update_cart_item(self, client, normal_user_token_headers, db):
        """
        GIVEN an authenticated user with a cart containing an item
        WHEN the user updates the quantity of the item
        THEN the item quantity should be updated successfully
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        import uuid
        
        # Create test category
        category = Category(
            id=uuid.uuid4(),
            name="Update Category",
            slug="update-category",
            description="Test category for update cart tests",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=uuid.uuid4(),
            name="Update Brand",
            slug="update-brand",
            description="Test brand for update cart tests",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=uuid.uuid4(),
            name="Update Product",
            slug="update-product",
            description="Test product for update cart tests",
            price=49.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True
        )
        db.add(product)
        db.commit()
        
        # Get or create a cart
        cart_response = client.get(
            "/api/v1/carts",
            headers=normal_user_token_headers
        )
        
        # Add item to cart
        item_data = {
            "product_id": str(product.id),
            "quantity": 1
        }
        add_response = client.post(
            "/api/v1/carts/items",
            json=item_data,
            headers=normal_user_token_headers
        )
        item_id = add_response.json()["id"]
        
        # Update the item quantity
        update_data = {
            "quantity": 5
        }
        response = client.put(
            f"/api/v1/carts/items/{item_id}",
            json=update_data,
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify updated data
        assert data["quantity"] == 5
        assert data["id"] == item_id


    def test_remove_cart_item(self, client, normal_user_token_headers, db):
        """
        GIVEN an authenticated user with a cart containing an item
        WHEN the user removes the item from the cart
        THEN the item should be removed successfully
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        import uuid
        
        # Create test category
        category = Category(
            id=uuid.uuid4(),
            name="Remove Category",
            slug="remove-category",
            description="Test category for remove cart tests",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=uuid.uuid4(),
            name="Remove Brand",
            slug="remove-brand",
            description="Test brand for remove cart tests",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=uuid.uuid4(),
            name="Remove Product",
            slug="remove-product",
            description="Test product for remove cart tests",
            price=29.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True
        )
        db.add(product)
        db.commit()
        
        # Get or create a cart
        cart_response = client.get(
            "/api/v1/carts",
            headers=normal_user_token_headers
        )
        cart_id = cart_response.json()["id"]
        
        # Add item to cart
        item_data = {
            "product_id": str(product.id),
            "quantity": 3
        }
        add_response = client.post(
            "/api/v1/carts/items",
            json=item_data,
            headers=normal_user_token_headers
        )
        item_id = add_response.json()["id"]
        
        # Remove the item
        response = client.delete(
            f"/api/v1/carts/items/{item_id}",
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 204
        
        # Verify it's removed
        cart_response = client.get(
            "/api/v1/carts",
            headers=normal_user_token_headers
        )
        cart_data = cart_response.json()
        assert len(cart_data["items"]) == 0


class TestCartManagement:
    """Tests for cart management operations."""
    
    def test_clear_cart(self, client, normal_user_token_headers, db):
        """
        GIVEN an authenticated user with a cart containing items
        WHEN the user clears their cart
        THEN all items should be removed from the cart
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        import uuid
        
        # Create test category
        category = Category(
            id=uuid.uuid4(),
            name="Clear Category",
            slug="clear-category",
            description="Test category for clear cart tests",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=uuid.uuid4(),
            name="Clear Brand",
            slug="clear-brand",
            description="Test brand for clear cart tests",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=uuid.uuid4(),
            name="Clear Product",
            slug="clear-product",
            description="Test product for clear cart tests",
            price=19.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True
        )
        db.add(product)
        db.commit()
        
        # Get or create a cart
        cart_response = client.get(
            "/api/v1/carts",
            headers=normal_user_token_headers
        )
        
        # Add item to cart
        item_data = {
            "product_id": str(product.id),
            "quantity": 2
        }
        client.post(
            "/api/v1/carts/items",
            json=item_data,
            headers=normal_user_token_headers
        )
        
        # Clear the cart
        response = client.delete(
            "/api/v1/carts",
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 204
        
        # Verify it's cleared
        cart_response = client.get(
            "/api/v1/carts",
            headers=normal_user_token_headers
        )
        cart_data = cart_response.json()
        assert len(cart_data["items"]) == 0


class TestCartCaching:
    """Tests for cart caching behavior."""
    
    def test_cart_cache_headers(self, client, normal_user_token_headers, db):
        """
        GIVEN an authenticated user making cart-related requests
        WHEN the requests are processed
        THEN appropriate cache control headers should be returned
        """
        # First create a product for testing
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        import uuid
        
        # Create test category
        category = Category(
            id=uuid.uuid4(),
            name="Cache Test Category",
            slug="cache-test-category",
            description="Test category for cache headers",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=uuid.uuid4(),
            name="Cache Test Brand",
            slug="cache-test-brand",
            description="Test brand for cache headers",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=uuid.uuid4(),
            name="Cache Test Product",
            slug="cache-test-product",
            description="Test product for cache headers",
            price=24.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True
        )
        db.add(product)
        db.commit()
        
        # Test case 1: Main cart endpoint
        response = client.post(
            "/api/v1/carts",
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 201
        
        # Verify cache headers
        assert "Cache-Control" in response.headers
        assert "no-cache" in response.headers["Cache-Control"]
        assert "no-store" in response.headers["Cache-Control"]
        assert "must-revalidate" in response.headers["Cache-Control"]
        assert "Pragma" in response.headers
        assert "no-cache" in response.headers["Pragma"]
        assert "Expires" in response.headers
        assert "0" in response.headers["Expires"]
        
        # Test case 2: Cart summary endpoint
        response = client.get(
            "/api/v1/carts/summary",
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 200
        
        # Verify cache headers
        assert "Cache-Control" in response.headers
        assert "no-cache" in response.headers["Cache-Control"]
        
        # Test case 3: Add item to cart endpoint
        item_data = {
            "product_id": str(product.id),
            "quantity": 1
        }
        response = client.post(
            "/api/v1/carts/items",
            json=item_data,
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 201
        
        # Verify cache headers
        assert "Cache-Control" in response.headers
        assert "no-cache" in response.headers["Cache-Control"]