import pytest
from fastapi.testclient import TestClient


def test_create_cart(client, normal_user_token_headers):
    """Test getting or creating a new cart."""
    response = client.get(
        "/api/v1/carts",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["is_active"] is True
    assert len(data["items"]) == 0


def test_get_active_cart(client, normal_user_token_headers):
    """Test getting the active cart for a user."""
    # Get the active cart (will create one if it doesn't exist)
    response = client.get(
        "/api/v1/carts",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["is_active"] is True


def test_cart_authentication_and_validation(client, normal_user_token_headers):
    """Test cart authentication and validation scenarios."""
    # Scenario 1: Try to get a cart without authentication or session ID
    response = client.get("/api/v1/carts")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]
    
    # Scenario 2: Create a cart with authentication
    response = client.get("/api/v1/carts", headers=normal_user_token_headers)
    assert response.status_code == 200
    cart_data = response.json()
    assert "id" in cart_data
    
    # Scenario 3: Test validation error with invalid UUID format
    response = client.put(
        "/api/v1/carts/items/invalid-uuid", 
        json={"quantity": 1},
        headers=normal_user_token_headers
    )
    assert response.status_code == 422  # Validation error for UUID format


def test_add_item_to_cart(client, normal_user_token_headers, db):
    """Test adding an item to a cart."""
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
    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == str(product.id)
    assert data["quantity"] == 2
    assert "id" in data


def test_add_item_to_cart_invalid_product(client, normal_user_token_headers):
    """Test adding an invalid product to a cart."""
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
    assert response.status_code == 404
    assert "Product not found" in response.json()["detail"]


def test_update_cart_item(client, normal_user_token_headers, db):
    """Test updating a cart item quantity."""
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
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 5
    assert data["id"] == item_id


def test_remove_cart_item(client, normal_user_token_headers, db):
    """Test removing an item from a cart."""
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
    assert response.status_code == 204
    
    # Verify it's removed
    cart_response = client.get(
        "/api/v1/carts",
        headers=normal_user_token_headers
    )
    cart_data = cart_response.json()
    assert len(cart_data["items"]) == 0


def test_clear_cart(client, normal_user_token_headers, db):
    """Test clearing all items from a cart."""
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
    assert response.status_code == 204
    
    # Verify it's cleared
    cart_response = client.get(
        "/api/v1/carts",
        headers=normal_user_token_headers
    )
    cart_data = cart_response.json()
    assert len(cart_data["items"]) == 0


def test_cart_cache_headers(client, normal_user_token_headers, db):
    """Test that cart endpoints return appropriate cache headers."""
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
    
    # Test main cart endpoint
    response = client.post(
        "/api/v1/carts",
        headers=normal_user_token_headers
    )
    assert response.status_code == 201
    assert "Cache-Control" in response.headers
    assert "no-cache" in response.headers["Cache-Control"]
    assert "no-store" in response.headers["Cache-Control"]
    assert "must-revalidate" in response.headers["Cache-Control"]
    assert "Pragma" in response.headers
    assert "no-cache" in response.headers["Pragma"]
    assert "Expires" in response.headers
    assert "0" in response.headers["Expires"]
    
    # Test cart summary endpoint
    response = client.get(
        "/api/v1/carts/summary",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    assert "Cache-Control" in response.headers
    assert "no-cache" in response.headers["Cache-Control"]
    
    # Test add item to cart endpoint with a valid product
    item_data = {
        "product_id": str(product.id),
        "quantity": 1
    }
    response = client.post(
        "/api/v1/carts/items",
        json=item_data,
        headers=normal_user_token_headers
    )
    assert response.status_code == 201
    assert "Cache-Control" in response.headers
    assert "no-cache" in response.headers["Cache-Control"]