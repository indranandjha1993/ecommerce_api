import pytest
from fastapi.testclient import TestClient


def test_create_order_from_cart(client, normal_user_token_headers, db):
    """Test creating an order from a cart."""
    # First create necessary test data
    from app.models.product import Product
    from app.models.category import Category
    from app.models.brand import Brand
    from app.models.address import Address
    from app.models.user import User
    import uuid
    
    # Get the current user
    user_response = client.get("/api/v1/users/me", headers=normal_user_token_headers)
    user_id = user_response.json()["id"]
    
    # Create test category
    category = Category(
        id=str(uuid.uuid4()),
        name="Order Category",
        slug="order-category",
        description="Test category for order tests",
        is_active=True
    )
    db.add(category)
    
    # Create test brand
    brand = Brand(
        id=str(uuid.uuid4()),
        name="Order Brand",
        slug="order-brand",
        description="Test brand for order tests",
        is_active=True
    )
    db.add(brand)
    
    # Create test product
    product = Product(
        id=str(uuid.uuid4()),
        name="Order Product",
        slug="order-product",
        description="Test product for order tests",
        price=99.99,
        category_id=category.id,
        brand_id=brand.id,
        is_active=True,
        sku="ORD-TEST-001"
    )
    db.add(product)
    
    # Create test address
    address = Address(
        id=str(uuid.uuid4()),
        user_id=user_id,
        first_name="Order",
        last_name="Test",
        street_address_1="123 Order St",
        city="Order City",
        postal_code="12345",
        country="Order Country",
        address_type="shipping",
        is_default=True
    )
    db.add(address)
    db.commit()
    
    # Create a cart
    cart_response = client.post(
        "/api/v1/carts",
        headers=normal_user_token_headers
    )
    cart_id = cart_response.json()["id"]
    
    # Add item to cart
    item_data = {
        "product_id": product.id,
        "quantity": 2
    }
    client.post(
        f"/api/v1/carts/{cart_id}/items",
        json=item_data,
        headers=normal_user_token_headers
    )
    
    # Create an order from the cart
    order_data = {
        "cart_id": cart_id,
        "shipping_address_id": address.id,
        "billing_address_id": address.id,
        "payment_method": "credit_card"
    }
    response = client.post(
        "/api/v1/orders",
        json=order_data,
        headers=normal_user_token_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product.id
    assert data["items"][0]["quantity"] == 2
    assert data["total_amount"] == 199.98  # 99.99 * 2


def test_create_order_empty_cart(client, normal_user_token_headers, db):
    """Test creating an order from an empty cart."""
    # Create a cart
    cart_response = client.post(
        "/api/v1/carts",
        headers=normal_user_token_headers
    )
    cart_id = cart_response.json()["id"]
    
    # Create an address
    address_data = {
        "first_name": "Empty",
        "last_name": "Cart",
        "street_address_1": "456 Empty St",
        "city": "Empty City",
        "postal_code": "54321",
        "country": "Empty Country",
        "address_type": "shipping",
        "is_default": True
    }
    address_response = client.post(
        "/api/v1/users/me/addresses",
        json=address_data,
        headers=normal_user_token_headers
    )
    address_id = address_response.json()["id"]
    
    # Try to create an order from the empty cart
    order_data = {
        "cart_id": cart_id,
        "shipping_address_id": address_id,
        "billing_address_id": address_id,
        "payment_method": "credit_card"
    }
    response = client.post(
        "/api/v1/orders",
        json=order_data,
        headers=normal_user_token_headers
    )
    assert response.status_code == 400
    assert "Cart is empty" in response.json()["detail"]


def test_get_user_orders(client, normal_user_token_headers, db):
    """Test getting all orders for a user."""
    # First create an order (reusing the setup from test_create_order_from_cart)
    from app.models.product import Product
    from app.models.category import Category
    from app.models.brand import Brand
    from app.models.address import Address
    from app.models.user import User
    import uuid
    
    # Get the current user
    user_response = client.get("/api/v1/users/me", headers=normal_user_token_headers)
    user_id = user_response.json()["id"]
    
    # Create test category
    category = Category(
        id=str(uuid.uuid4()),
        name="List Order Category",
        slug="list-order-category",
        description="Test category for listing orders",
        is_active=True
    )
    db.add(category)
    
    # Create test brand
    brand = Brand(
        id=str(uuid.uuid4()),
        name="List Order Brand",
        slug="list-order-brand",
        description="Test brand for listing orders",
        is_active=True
    )
    db.add(brand)
    
    # Create test product
    product = Product(
        id=str(uuid.uuid4()),
        name="List Order Product",
        slug="list-order-product",
        description="Test product for listing orders",
        price=49.99,
        category_id=category.id,
        brand_id=brand.id,
        is_active=True,
        sku="LIST-ORD-001"
    )
    db.add(product)
    
    # Create test address
    address = Address(
        id=str(uuid.uuid4()),
        user_id=user_id,
        first_name="List",
        last_name="Orders",
        street_address_1="789 List St",
        city="List City",
        postal_code="67890",
        country="List Country",
        address_type="shipping",
        is_default=True
    )
    db.add(address)
    db.commit()
    
    # Create a cart
    cart_response = client.post(
        "/api/v1/carts",
        headers=normal_user_token_headers
    )
    cart_id = cart_response.json()["id"]
    
    # Add item to cart
    item_data = {
        "product_id": product.id,
        "quantity": 1
    }
    client.post(
        f"/api/v1/carts/{cart_id}/items",
        json=item_data,
        headers=normal_user_token_headers
    )
    
    # Create an order from the cart
    order_data = {
        "cart_id": cart_id,
        "shipping_address_id": address.id,
        "billing_address_id": address.id,
        "payment_method": "credit_card"
    }
    client.post(
        "/api/v1/orders",
        json=order_data,
        headers=normal_user_token_headers
    )
    
    # Get all orders for the user
    response = client.get(
        "/api/v1/orders",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "id" in data[0]
    assert "status" in data[0]
    assert "created_at" in data[0]


def test_get_order_by_id(client, normal_user_token_headers, db):
    """Test getting an order by ID."""
    # First create an order (reusing the setup from test_create_order_from_cart)
    from app.models.product import Product
    from app.models.category import Category
    from app.models.brand import Brand
    from app.models.address import Address
    from app.models.user import User
    import uuid
    
    # Get the current user
    user_response = client.get("/api/v1/users/me", headers=normal_user_token_headers)
    user_id = user_response.json()["id"]
    
    # Create test category
    category = Category(
        id=str(uuid.uuid4()),
        name="Get Order Category",
        slug="get-order-category",
        description="Test category for getting order",
        is_active=True
    )
    db.add(category)
    
    # Create test brand
    brand = Brand(
        id=str(uuid.uuid4()),
        name="Get Order Brand",
        slug="get-order-brand",
        description="Test brand for getting order",
        is_active=True
    )
    db.add(brand)
    
    # Create test product
    product = Product(
        id=str(uuid.uuid4()),
        name="Get Order Product",
        slug="get-order-product",
        description="Test product for getting order",
        price=29.99,
        category_id=category.id,
        brand_id=brand.id,
        is_active=True,
        sku="GET-ORD-001"
    )
    db.add(product)
    
    # Create test address
    address = Address(
        id=str(uuid.uuid4()),
        user_id=user_id,
        first_name="Get",
        last_name="Order",
        street_address_1="321 Get St",
        city="Get City",
        postal_code="13579",
        country="Get Country",
        address_type="shipping",
        is_default=True
    )
    db.add(address)
    db.commit()
    
    # Create a cart
    cart_response = client.post(
        "/api/v1/carts",
        headers=normal_user_token_headers
    )
    cart_id = cart_response.json()["id"]
    
    # Add item to cart
    item_data = {
        "product_id": product.id,
        "quantity": 3
    }
    client.post(
        f"/api/v1/carts/{cart_id}/items",
        json=item_data,
        headers=normal_user_token_headers
    )
    
    # Create an order from the cart
    order_data = {
        "cart_id": cart_id,
        "shipping_address_id": address.id,
        "billing_address_id": address.id,
        "payment_method": "credit_card"
    }
    order_response = client.post(
        "/api/v1/orders",
        json=order_data,
        headers=normal_user_token_headers
    )
    order_id = order_response.json()["id"]
    
    # Get the order by ID
    response = client.get(
        f"/api/v1/orders/{order_id}",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["status"] == "pending"
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product.id
    assert data["items"][0]["quantity"] == 3
    assert data["total_amount"] == 89.97  # 29.99 * 3


def test_get_order_not_found(client, superuser_token_headers):
    """Test getting a non-existent order."""
    import uuid
    non_existent_id = str(uuid.uuid4())
    response = client.get(
        f"/api/v1/orders/{non_existent_id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 404
    assert "Order not found" in response.json()["detail"]


def test_cancel_order(client, normal_user_token_headers, db):
    """Test canceling an order."""
    # First create an order (reusing the setup from test_create_order_from_cart)
    from app.models.product import Product
    from app.models.category import Category
    from app.models.brand import Brand
    from app.models.address import Address
    from app.models.user import User
    import uuid
    
    # Get the current user
    user_response = client.get("/api/v1/users/me", headers=normal_user_token_headers)
    user_id = user_response.json()["id"]
    
    # Create test category
    category = Category(
        id=str(uuid.uuid4()),
        name="Cancel Order Category",
        slug="cancel-order-category",
        description="Test category for canceling order",
        is_active=True
    )
    db.add(category)
    
    # Create test brand
    brand = Brand(
        id=str(uuid.uuid4()),
        name="Cancel Order Brand",
        slug="cancel-order-brand",
        description="Test brand for canceling order",
        is_active=True
    )
    db.add(brand)
    
    # Create test product
    product = Product(
        id=str(uuid.uuid4()),
        name="Cancel Order Product",
        slug="cancel-order-product",
        description="Test product for canceling order",
        price=19.99,
        category_id=category.id,
        brand_id=brand.id,
        is_active=True,
        sku="CANCEL-ORD-001"
    )
    db.add(product)
    
    # Create test address
    address = Address(
        id=str(uuid.uuid4()),
        user_id=user_id,
        first_name="Cancel",
        last_name="Order",
        street_address_1="654 Cancel St",
        city="Cancel City",
        postal_code="24680",
        country="Cancel Country",
        address_type="shipping",
        is_default=True
    )
    db.add(address)
    db.commit()
    
    # Create a cart
    cart_response = client.post(
        "/api/v1/carts",
        headers=normal_user_token_headers
    )
    cart_id = cart_response.json()["id"]
    
    # Add item to cart
    item_data = {
        "product_id": product.id,
        "quantity": 4
    }
    client.post(
        f"/api/v1/carts/{cart_id}/items",
        json=item_data,
        headers=normal_user_token_headers
    )
    
    # Create an order from the cart
    order_data = {
        "cart_id": cart_id,
        "shipping_address_id": address.id,
        "billing_address_id": address.id,
        "payment_method": "credit_card"
    }
    order_response = client.post(
        "/api/v1/orders",
        json=order_data,
        headers=normal_user_token_headers
    )
    order_id = order_response.json()["id"]
    
    # Cancel the order
    response = client.put(
        f"/api/v1/orders/{order_id}/cancel",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["status"] == "cancelled"


def test_cancel_shipped_order(client, normal_user_token_headers, db):
    """Test canceling an order that has already been shipped."""
    # First create an order (reusing the setup from test_create_order_from_cart)
    from app.models.product import Product
    from app.models.category import Category
    from app.models.brand import Brand
    from app.models.address import Address
    from app.models.user import User
    from app.models.order import Order
    import uuid
    
    # Get the current user
    user_response = client.get("/api/v1/users/me", headers=normal_user_token_headers)
    user_id = user_response.json()["id"]
    
    # Create test category
    category = Category(
        id=str(uuid.uuid4()),
        name="Shipped Order Category",
        slug="shipped-order-category",
        description="Test category for shipped order",
        is_active=True
    )
    db.add(category)
    
    # Create test brand
    brand = Brand(
        id=str(uuid.uuid4()),
        name="Shipped Order Brand",
        slug="shipped-order-brand",
        description="Test brand for shipped order",
        is_active=True
    )
    db.add(brand)
    
    # Create test product
    product = Product(
        id=str(uuid.uuid4()),
        name="Shipped Order Product",
        slug="shipped-order-product",
        description="Test product for shipped order",
        price=9.99,
        category_id=category.id,
        brand_id=brand.id,
        is_active=True,
        sku="SHIP-ORD-001"
    )
    db.add(product)
    
    # Create test address
    address = Address(
        id=str(uuid.uuid4()),
        user_id=user_id,
        first_name="Shipped",
        last_name="Order",
        street_address_1="987 Shipped St",
        city="Shipped City",
        postal_code="97531",
        country="Shipped Country",
        address_type="shipping",
        is_default=True
    )
    db.add(address)
    db.commit()
    
    # Create a cart
    cart_response = client.post(
        "/api/v1/carts",
        headers=normal_user_token_headers
    )
    cart_id = cart_response.json()["id"]
    
    # Add item to cart
    item_data = {
        "product_id": product.id,
        "quantity": 5
    }
    client.post(
        f"/api/v1/carts/{cart_id}/items",
        json=item_data,
        headers=normal_user_token_headers
    )
    
    # Create an order from the cart
    order_data = {
        "cart_id": cart_id,
        "shipping_address_id": address.id,
        "billing_address_id": address.id,
        "payment_method": "credit_card"
    }
    order_response = client.post(
        "/api/v1/orders",
        json=order_data,
        headers=normal_user_token_headers
    )
    order_id = order_response.json()["id"]
    
    # Update the order status to shipped directly in the database
    order = db.query(Order).filter(Order.id == order_id).first()
    order.status = "shipped"
    db.commit()
    
    # Try to cancel the shipped order
    response = client.put(
        f"/api/v1/orders/{order_id}/cancel",
        headers=normal_user_token_headers
    )
    assert response.status_code == 400
    assert "Cannot cancel order with status: shipped" in response.json()["detail"]