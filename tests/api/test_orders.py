from decimal import Decimal

from app.models.cart import Cart, CartItem


def test_create_order_from_cart(client, db, normal_user_token_headers):
    """
    Test creating an order from a cart.
    """
    # First create a product
    from app.models.product import Product
    from app.models.inventory import Inventory

    product = Product(
        name="Test Order Product",
        slug="test-order-product",
        description="Test order product description",
        price=Decimal("199.99"),
        is_active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Create inventory for the product
    inventory = Inventory(
        product_id=product.id,
        quantity=10
    )
    db.add(inventory)
    db.commit()

    # Create a cart
    cart = Cart(
        is_active=True
    )
    db.add(cart)
    db.commit()
    db.refresh(cart)

    # Add product to cart
    cart_item = CartItem(
        cart_id=cart.id,
        product_id=product.id,
        quantity=2
    )
    db.add(cart_item)
    db.commit()

    # Create an order from the cart
    order_data = {
        "cart_id": str(cart.id),  # Convert UUID to string
        "customer_email": "test@example.com",
        "customer_name": "Test User",
        "customer_phone": "555-123-4567",
        "shipping_address": {
            "first_name": "Test",
            "last_name": "User",
            "street_address_1": "123 Test St",
            "city": "Test City",
            "postal_code": "12345",
            "country": "Test Country"
        },
        "shipping_method": "standard",
        "payment_method": "credit_card",
        "payment_details": {},
        "customer_notes": "",
        "use_shipping_for_billing": True,
        "metadata": {}
    }

    response = client.post(
        "/api/v1/orders",
        json=order_data,
        headers=normal_user_token_headers
    )

    # Debugging info if needed
    if response.status_code != 201:
        print(f"Error response: {response.json()}")

    assert response.status_code == 201
    data = response.json()
    assert data["customer_email"] == order_data["customer_email"]
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2

    # Check that cart is now inactive
    db.refresh(cart)
    assert not cart.is_active


def test_create_order_empty_cart(client, db, normal_user_token_headers):
    """
    Test creating an order with an empty cart.
    """
    # Create an empty cart
    cart = Cart(
        is_active=True
    )
    db.add(cart)
    db.commit()
    db.refresh(cart)

    # Try to create an order from the empty cart
    order_data = {
        "cart_id": str(cart.id),  # Convert UUID to string
        "customer_email": "test@example.com",
        "customer_name": "Test User",
        "customer_phone": "555-123-4567",
        "shipping_address": {
            "first_name": "Test",
            "last_name": "User",
            "street_address_1": "123 Test St",
            "city": "Test City",
            "postal_code": "12345",
            "country": "Test Country"
        },
        "shipping_method": "standard",
        "payment_method": "credit_card",
        "payment_details": {},
        "customer_notes": "",
        "use_shipping_for_billing": True,
        "metadata": {}
    }

    response = client.post(
        "/api/v1/orders",
        json=order_data,
        headers=normal_user_token_headers
    )

    # Print the response for debugging
    print(f"Empty cart response: {response.json()}")

    assert response.status_code == 400

    # Check error message - may be formatted differently
    error_detail = response.json().get("detail", "")
    if isinstance(error_detail, str):
        assert "Cart is empty" in error_detail
    elif isinstance(error_detail, dict):
        assert "Cart is empty" in error_detail.get("msg", "")
    elif isinstance(error_detail, list) and len(error_detail) > 0:
        assert any("Cart is empty" in str(err) for err in error_detail)
    else:
        assert False, f"Unexpected error format: {error_detail}"


def test_get_user_orders(client, db, normal_user_token_headers):
    """
    Test getting orders for the current user.
    """
    # Create a user order
    from app.models.order import Order, OrderStatus, PaymentStatus
    from app.models.user import User
    from app.models.address import Address
    from app.models.order import OrderItem

    # Get the user ID from token
    user = db.query(User).filter(User.email == "test@example.com").first()

    # Create addresses for the order
    shipping_address = Address(
        user_id=user.id,
        first_name="Test",
        last_name="User",
        street_address_1="123 Test St",
        city="Test City",
        postal_code="12345",
        country="Test Country",
        address_type="shipping"
    )
    db.add(shipping_address)
    db.commit()
    db.refresh(shipping_address)

    billing_address = Address(
        user_id=user.id,
        first_name="Test",
        last_name="User",
        street_address_1="123 Test St",
        city="Test City",
        postal_code="12345",
        country="Test Country",
        address_type="billing"
    )
    db.add(billing_address)
    db.commit()
    db.refresh(billing_address)

    # Create order
    order = Order(
        order_number="TEST-123",
        user_id=user.id,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        subtotal=Decimal("100.00"),
        shipping_amount=Decimal("10.00"),
        tax_amount=Decimal("10.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("120.00"),
        currency="USD",
        customer_email="test@example.com",
        customer_name="Test User",
        shipping_address_id=shipping_address.id,
        billing_address_id=billing_address.id
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Create a product for the order item
    from app.models.product import Product

    product = Product(
        name="Test Product For Order",
        slug="test-product-for-order",
        description="Test product for order",
        price=Decimal("100.00"),
        is_active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Create order item to ensure item_count is populated
    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=product.name,
        product_sku="TEST-SKU",
        quantity=2,
        unit_price=Decimal("50.00"),
        subtotal=Decimal("100.00"),
        tax_amount=Decimal("10.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("110.00")
    )
    db.add(order_item)
    db.commit()
    db.refresh(order)

    # Get user orders
    response = client.get(
        "/api/v1/orders/me",
        headers=normal_user_token_headers
    )

    # Debugging info
    if response.status_code != 200:
        print(f"Error in user orders: {response.json()}")

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1

    # Check order data - now item_count should be populated
    assert data["items"][0]["order_number"] == "TEST-123"
    # We created one order item with quantity 2
    assert data["items"][0]["item_count"] == 1
    
    # Check cache headers
    assert "Cache-Control" in response.headers
    assert "private" in response.headers["Cache-Control"]


def test_get_order_by_id(client, db, normal_user_token_headers):
    """
    Test getting a specific order by ID.
    """
    # Create a user order
    from app.models.order import Order, OrderStatus, PaymentStatus, OrderItem
    from app.models.user import User
    from app.models.address import Address
    from app.models.product import Product

    # Get the user ID from token
    user = db.query(User).filter(User.email == "test@example.com").first()

    # Create addresses for the order
    shipping_address = Address(
        user_id=user.id,
        first_name="Test",
        last_name="User",
        street_address_1="123 Test St",
        city="Test City",
        postal_code="12345",
        country="Test Country",
        address_type="shipping"
    )
    db.add(shipping_address)
    db.commit()
    db.refresh(shipping_address)

    billing_address = Address(
        user_id=user.id,
        first_name="Test",
        last_name="User",
        street_address_1="123 Test St",
        city="Test City",
        postal_code="12345",
        country="Test Country",
        address_type="billing"
    )
    db.add(billing_address)
    db.commit()
    db.refresh(billing_address)

    # Create product for order item
    product = Product(
        name="Test Product For Order ID",
        slug="test-product-for-order-id",
        description="Test product for order ID",
        price=Decimal("100.00"),
        is_active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Create order
    order = Order(
        order_number="TEST-456",
        user_id=user.id,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        subtotal=Decimal("100.00"),
        shipping_amount=Decimal("10.00"),
        tax_amount=Decimal("10.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("120.00"),
        currency="USD",
        customer_email="test@example.com",
        customer_name="Test User",
        shipping_address_id=shipping_address.id,
        billing_address_id=billing_address.id
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Add order item
    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=product.name,
        product_sku="TEST-SKU-456",
        quantity=1,
        unit_price=Decimal("100.00"),
        subtotal=Decimal("100.00"),
        tax_amount=Decimal("10.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("110.00")
    )
    db.add(order_item)
    db.commit()
    db.refresh(order)

    # Get order by ID
    response = client.get(
        f"/api/v1/orders/me/{str(order.id)}",  # Convert UUID to string
        headers=normal_user_token_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["order_number"] == "TEST-456"


def test_cancel_order(client, db, normal_user_token_headers):
    """
    Test cancelling an order.
    """
    # Create a user order
    from app.models.order import Order, OrderStatus, PaymentStatus, OrderItem
    from app.models.user import User
    from app.models.address import Address
    from app.models.product import Product

    # Get the user ID from token
    user = db.query(User).filter(User.email == "test@example.com").first()

    # Create addresses for the order
    shipping_address = Address(
        user_id=user.id,
        first_name="Test",
        last_name="User",
        street_address_1="123 Test St",
        city="Test City",
        postal_code="12345",
        country="Test Country",
        address_type="shipping"
    )
    db.add(shipping_address)
    db.commit()
    db.refresh(shipping_address)

    billing_address = Address(
        user_id=user.id,
        first_name="Test",
        last_name="User",
        street_address_1="123 Test St",
        city="Test City",
        postal_code="12345",
        country="Test Country",
        address_type="billing"
    )
    db.add(billing_address)
    db.commit()
    db.refresh(billing_address)

    # Create product for order item
    product = Product(
        name="Test Product For Cancel",
        slug="test-product-for-cancel",
        description="Test product for cancel",
        price=Decimal("100.00"),
        is_active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Create order
    order = Order(
        order_number="TEST-789",
        user_id=user.id,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        subtotal=Decimal("100.00"),
        shipping_amount=Decimal("10.00"),
        tax_amount=Decimal("10.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("120.00"),
        currency="USD",
        customer_email="test@example.com",
        customer_name="Test User",
        shipping_address_id=shipping_address.id,
        billing_address_id=billing_address.id
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Add order item
    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=product.name,
        product_sku="TEST-SKU-789",
        quantity=1,
        unit_price=Decimal("100.00"),
        subtotal=Decimal("100.00"),
        tax_amount=Decimal("10.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("110.00")
    )
    db.add(order_item)
    db.commit()
    db.refresh(order)

    # Cancel order
    response = client.post(
        f"/api/v1/orders/me/{str(order.id)}/cancel",  # Convert UUID to string
        headers=normal_user_token_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"


def test_cancel_shipped_order(client, db, normal_user_token_headers):
    """
    Test cancelling a shipped order (should not be allowed).
    """
    # Create a user order that's already shipped
    from app.models.order import Order, OrderStatus, PaymentStatus, OrderItem
    from app.models.user import User
    from app.models.address import Address
    from app.models.product import Product

    # Get the user ID from token
    user = db.query(User).filter(User.email == "test@example.com").first()

    # Create addresses for the order
    shipping_address = Address(
        user_id=user.id,
        first_name="Test",
        last_name="User",
        street_address_1="123 Test St",
        city="Test City",
        postal_code="12345",
        country="Test Country",
        address_type="shipping"
    )
    db.add(shipping_address)
    db.commit()
    db.refresh(shipping_address)

    billing_address = Address(
        user_id=user.id,
        first_name="Test",
        last_name="User",
        street_address_1="123 Test St",
        city="Test City",
        postal_code="12345",
        country="Test Country",
        address_type="billing"
    )
    db.add(billing_address)
    db.commit()
    db.refresh(billing_address)

    # Create product for order item
    product = Product(
        name="Test Product For Shipped",
        slug="test-product-for-shipped",
        description="Test product for shipped order",
        price=Decimal("100.00"),
        is_active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Create order
    order = Order(
        order_number="TEST-SHIPPED",
        user_id=user.id,
        status=OrderStatus.SHIPPED,
        payment_status=PaymentStatus.PAID,
        subtotal=Decimal("100.00"),
        shipping_amount=Decimal("10.00"),
        tax_amount=Decimal("10.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("120.00"),
        currency="USD",
        customer_email="test@example.com",
        customer_name="Test User",
        shipping_address_id=shipping_address.id,
        billing_address_id=billing_address.id
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Add order item
    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=product.name,
        product_sku="TEST-SKU-SHIPPED",
        quantity=1,
        unit_price=Decimal("100.00"),
        subtotal=Decimal("100.00"),
        tax_amount=Decimal("10.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("110.00")
    )
    db.add(order_item)
    db.commit()
    db.refresh(order)

    # Try to cancel shipped order
    response = client.post(
        f"/api/v1/orders/me/{str(order.id)}/cancel",  # Convert UUID to string
        headers=normal_user_token_headers
    )

    assert response.status_code == 400
    # Print the response for debugging
    print(f"Cancel shipped order response: {response.json()}")
    assert "cannot be cancelled" in response.json()["detail"]


def test_order_by_number(client, db, normal_user_token_headers):
    """
    Test getting an order by order number.
    """
    # Create a user order
    from app.models.order import Order, OrderStatus, PaymentStatus, OrderItem
    from app.models.user import User
    from app.models.address import Address
    from app.models.product import Product

    # Get the user ID from token
    user = db.query(User).filter(User.email == "test@example.com").first()

    # Create addresses for the order
    shipping_address = Address(
        user_id=user.id,
        first_name="Test",
        last_name="User",
        street_address_1="123 Test St",
        city="Test City",
        postal_code="12345",
        country="Test Country",
        address_type="shipping"
    )
    db.add(shipping_address)
    db.commit()
    db.refresh(shipping_address)

    billing_address = Address(
        user_id=user.id,
        first_name="Test",
        last_name="User",
        street_address_1="123 Test St",
        city="Test City",
        postal_code="12345",
        country="Test Country",
        address_type="billing"
    )
    db.add(billing_address)
    db.commit()
    db.refresh(billing_address)

    # Create product for order item
    product = Product(
        name="Test Product For Number",
        slug="test-product-for-number",
        description="Test product for order number",
        price=Decimal("100.00"),
        is_active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Create order
    order_number = "TEST-NUMBER-123"
    order = Order(
        order_number=order_number,
        user_id=user.id,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        subtotal=Decimal("100.00"),
        shipping_amount=Decimal("10.00"),
        tax_amount=Decimal("10.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("120.00"),
        currency="USD",
        customer_email="test@example.com",
        customer_name="Test User",
        shipping_address_id=shipping_address.id,
        billing_address_id=billing_address.id
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Add order item
    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=product.name,
        product_sku="TEST-SKU-NUMBER",
        quantity=1,
        unit_price=Decimal("100.00"),
        subtotal=Decimal("100.00"),
        tax_amount=Decimal("10.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("110.00")
    )
    db.add(order_item)
    db.commit()
    db.refresh(order)

    # Get order by number
    response = client.get(
        f"/api/v1/orders/number/{order_number}",
        headers=normal_user_token_headers
    )
    
    # Check cache headers
    assert "Cache-Control" in response.headers
    assert "private" in response.headers["Cache-Control"]

    assert response.status_code == 200
    data = response.json()
    assert data["order_number"] == order_number
    
def test_admin_orders_with_payment_status(client, db, superuser_token_headers):
    """
    Test admin endpoint to get orders filtered by payment status.
    """
    # Create test orders with different payment statuses
    from app.models.order import Order, OrderStatus, PaymentStatus
    from app.models.user import User
    from app.models.address import Address

    # Get or create a user
    user = db.query(User).filter(User.email == "test@example.com").first()
    if not user:
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Create address for the orders
    shipping_address = Address(
        user_id=user.id,
        first_name="Payment Test",
        last_name="User",
        street_address_1="123 Payment St",
        city="Payment City",
        postal_code="12345",
        country="Payment Country",
        address_type="shipping"
    )
    db.add(shipping_address)
    db.commit()
    db.refresh(shipping_address)

    # Create billing address
    billing_address = Address(
        user_id=user.id,
        first_name="Payment Test",
        last_name="User",
        street_address_1="123 Payment St",
        city="Payment City",
        postal_code="12345",
        country="Payment Country",
        address_type="billing"
    )
    db.add(billing_address)
    db.commit()
    db.refresh(billing_address)
    
    # Create order with PENDING payment status
    order1 = Order(
        order_number="PAYMENT-PENDING",
        user_id=user.id,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        subtotal=Decimal("100.00"),
        shipping_amount=Decimal("10.00"),
        tax_amount=Decimal("10.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("120.00"),
        currency="USD",
        customer_email="test@example.com",
        customer_name="Payment Test User",
        shipping_address_id=shipping_address.id,
        billing_address_id=billing_address.id
    )
    db.add(order1)
    
    # Create order with PAID payment status
    order2 = Order(
        order_number="PAYMENT-PAID",
        user_id=user.id,
        status=OrderStatus.PROCESSING,
        payment_status=PaymentStatus.PAID,
        subtotal=Decimal("200.00"),
        shipping_amount=Decimal("15.00"),
        tax_amount=Decimal("20.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("235.00"),
        currency="USD",
        customer_email="test@example.com",
        customer_name="Payment Test User",
        shipping_address_id=shipping_address.id,
        billing_address_id=billing_address.id
    )
    db.add(order2)
    db.commit()
    db.refresh(order1)
    db.refresh(order2)

    # Test filtering by payment status - PENDING
    response = client.get(
        f"/api/v1/orders?payment_status=pending",
        headers=superuser_token_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    assert all(item["payment_status"] == "pending" for item in data["items"])
    
    # Test filtering by payment status - PAID
    response = client.get(
        f"/api/v1/orders?payment_status=paid",
        headers=superuser_token_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    assert all(item["payment_status"] == "paid" for item in data["items"])
    
    # Check cache headers
    assert "Cache-Control" in response.headers
    assert "private" in response.headers["Cache-Control"]
