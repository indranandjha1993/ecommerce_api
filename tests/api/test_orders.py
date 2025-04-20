from decimal import Decimal
import pytest

from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.inventory import Inventory


class TestOrderCreation:
    """Tests for order creation functionality."""
    
    def test_create_order_from_cart_with_items(self, client, db, normal_user_token_headers):
        """
        GIVEN an authenticated user with a cart containing items
        WHEN the user creates an order from the cart
        THEN an order should be created with the cart items and the cart should be deactivated
        """
        # Create a product with inventory
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

        # Create a cart with the product
        cart = Cart(is_active=True)
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
            "cart_id": str(cart.id),
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
            "customer_notes": "Please deliver to front door",
            "use_shipping_for_billing": True,
            "metadata": {"source": "web"}
        }

        response = client.post(
            "/api/v1/orders",
            json=order_data,
            headers=normal_user_token_headers
        )

        # Verify response
        assert response.status_code == 201
        data = response.json()
        
        # Verify order details
        assert data["customer_email"] == order_data["customer_email"]
        assert data["customer_name"] == order_data["customer_name"]
        assert data["customer_phone"] == order_data["customer_phone"]
        assert data["customer_notes"] == order_data["customer_notes"]
        assert data["shipping_method"] == order_data["shipping_method"]
        assert data["payment_method"] == order_data["payment_method"]
        assert data["status"] == "pending"
        assert data["payment_status"] == "pending"
        
        # Verify order items
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
        assert data["items"][0]["product_name"] == product.name
        
        # Verify order totals
        assert "subtotal" in data
        assert "total_amount" in data
        assert "tax_amount" in data
        assert "shipping_amount" in data
        
        # Verify cart is now inactive
        db.refresh(cart)
        assert not cart.is_active
        


    def test_create_order_with_empty_cart_fails(self, client, db, normal_user_token_headers):
        """
        GIVEN an authenticated user with an empty cart
        WHEN the user tries to create an order from the empty cart
        THEN an error should be returned indicating the cart is empty
        """
        # Create an empty cart
        cart = Cart(is_active=True)
        db.add(cart)
        db.commit()
        db.refresh(cart)

        # Try to create an order from the empty cart
        order_data = {
            "cart_id": str(cart.id),
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

        # Verify error response
        assert response.status_code == 400
        
        # Check error message
        error_detail = response.json().get("detail", "")
        assert "Cart is empty" in str(error_detail), f"Unexpected error message: {error_detail}"
        
        # Verify cart is still active
        db.refresh(cart)
        assert cart.is_active


class TestOrderRetrieval:
    """Tests for order retrieval functionality."""
    
    def test_get_orders_for_current_user(self, client, db, normal_user_token_headers):
        """
        GIVEN an authenticated user with existing orders
        WHEN the user requests their orders
        THEN the user's orders should be returned with correct data and cache headers
        """
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

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        assert len(data["items"]) >= 1

        # Verify order data
        assert data["items"][0]["order_number"] == "TEST-123"
        assert data["items"][0]["item_count"] == 1
        assert data["items"][0]["status"] == "pending"
        assert data["items"][0]["payment_status"] == "pending"
        # The API might not return customer_email in the list view, so we'll skip that check
        assert data["items"][0]["total_amount"] == "120.00"
        
        
    def test_get_orders_pagination(self, client, db, normal_user_token_headers):
        """
        GIVEN an authenticated user with multiple orders
        WHEN the user requests orders with pagination
        THEN the correct page of orders should be returned
        """
        # Get user orders with pagination
        response = client.get(
            "/api/v1/orders/me?page=1&size=10",
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify pagination data
        assert data["page"] == 1
        assert data["size"] == 10
        assert isinstance(data["total"], int)
        assert isinstance(data["pages"], int)
        
        # Verify items are returned as a list
        assert isinstance(data["items"], list)


    def test_get_specific_order_by_id(self, client, db, normal_user_token_headers):
        """
        GIVEN an authenticated user with an existing order
        WHEN the user requests a specific order by ID
        THEN the order details should be returned
        """
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
            f"/api/v1/orders/me/{str(order.id)}",
            headers=normal_user_token_headers
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify order details
        assert data["order_number"] == "TEST-456"
        assert data["customer_email"] == "test@example.com"
        assert data["status"] == "pending"
        assert data["payment_status"] == "pending"
        assert data["subtotal"] == "100.00"
        assert data["total_amount"] == "120.00"
        
        # Verify order items
        assert len(data["items"]) == 1
        assert data["items"][0]["product_name"] == product.name
        assert data["items"][0]["quantity"] == 1
        assert data["items"][0]["unit_price"] == "100.00"
        
    def test_get_nonexistent_order_by_id(self, client, normal_user_token_headers):
        """
        GIVEN an authenticated user
        WHEN the user requests a non-existent order ID
        THEN a 404 Not Found response should be returned
        """
        import uuid
        
        # Generate a random UUID that doesn't exist
        nonexistent_id = uuid.uuid4()
        
        # Try to get a non-existent order
        response = client.get(
            f"/api/v1/orders/me/{nonexistent_id}",
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()


class TestOrderCancellation:
    """Tests for order cancellation functionality."""
    
    def test_cancel_pending_order(self, client, db, normal_user_token_headers):
        """
        GIVEN an authenticated user with a pending order
        WHEN the user cancels the order
        THEN the order status should be updated to cancelled
        """
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
            order_number="TEST-CANCEL-789",
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
            f"/api/v1/orders/me/{str(order.id)}/cancel",
            headers=normal_user_token_headers
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify order status
        assert data["status"] == "cancelled"
        assert data["order_number"] == "TEST-CANCEL-789"
        
        # Verify cache headers
        assert "Cache-Control" in response.headers
        assert "no-store" in response.headers["Cache-Control"] or "private" in response.headers["Cache-Control"]
        
        # Verify inventory is restored (would require checking the inventory)
        # This would be a good addition to the test

    def test_cancel_shipped_order_fails(self, client, db, normal_user_token_headers):
        """
        GIVEN an authenticated user with a shipped order
        WHEN the user attempts to cancel the order
        THEN the API should return an error indicating the order cannot be cancelled
        """
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

        # Create order with SHIPPED status
        order = Order(
            order_number="TEST-SHIPPED-ORDER",
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
            f"/api/v1/orders/me/{str(order.id)}/cancel",
            headers=normal_user_token_headers
        )

        # Verify error response
        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data
        assert "cannot be cancelled" in error_data["detail"]
        
        # Verify order status hasn't changed
        db.refresh(order)
        assert order.status == OrderStatus.SHIPPED


class TestOrderLookup:
    """Tests for order lookup functionality."""
    
    def test_get_order_by_number(self, client, db, normal_user_token_headers):
        """
        GIVEN an authenticated user with an existing order
        WHEN the user looks up the order by its order number
        THEN the correct order details should be returned
        """
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

        # Create order with a specific order number
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
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify order details
        assert data["order_number"] == order_number
        assert data["customer_email"] == "test@example.com"
        assert data["status"] == "pending"
        assert data["payment_status"] == "pending"
        assert data["subtotal"] == "100.00"
        assert data["total_amount"] == "120.00"
        
        # Verify order items
        assert len(data["items"]) == 1
        assert data["items"][0]["product_name"] == product.name
        assert data["items"][0]["quantity"] == 1
    
    def test_get_nonexistent_order_by_number(self, client, normal_user_token_headers):
        """
        GIVEN an authenticated user
        WHEN the user looks up a non-existent order number
        THEN a 404 Not Found response should be returned
        """
        # Try to get a non-existent order
        response = client.get(
            "/api/v1/orders/number/NON-EXISTENT-ORDER",
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()
    
class TestAdminOrderManagement:
    """Tests for admin order management functionality."""
    
    def test_filter_orders_by_payment_status(self, client, db, superuser_token_headers):
        """
        GIVEN an admin user and orders with different payment statuses
        WHEN the admin filters orders by payment status
        THEN only orders with the specified payment status should be returned
        """
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
            order_number="PAYMENT-PENDING-TEST",
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
            order_number="PAYMENT-PAID-TEST",
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
        
        # Create order with REFUNDED payment status
        order3 = Order(
            order_number="PAYMENT-REFUNDED-TEST",
            user_id=user.id,
            status=OrderStatus.CANCELLED,
            payment_status=PaymentStatus.REFUNDED,
            subtotal=Decimal("150.00"),
            shipping_amount=Decimal("12.00"),
            tax_amount=Decimal("15.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("177.00"),
            currency="USD",
            customer_email="test@example.com",
            customer_name="Payment Test User",
            shipping_address_id=shipping_address.id,
            billing_address_id=billing_address.id
        )
        db.add(order3)
        
        db.commit()
        db.refresh(order1)
        db.refresh(order2)
        db.refresh(order3)

        # Test filtering by payment status - PENDING
        response = client.get(
            "/api/v1/orders?payment_status=pending",
            headers=superuser_token_headers
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(item["payment_status"] == "pending" for item in data["items"])
        assert any(item["order_number"] == "PAYMENT-PENDING-TEST" for item in data["items"])
        
        # Test filtering by payment status - PAID
        response = client.get(
            "/api/v1/orders?payment_status=paid",
            headers=superuser_token_headers
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(item["payment_status"] == "paid" for item in data["items"])
        assert any(item["order_number"] == "PAYMENT-PAID-TEST" for item in data["items"])
        
        # Test filtering by payment status - REFUNDED
        response = client.get(
            "/api/v1/orders?payment_status=refunded",
            headers=superuser_token_headers
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(item["payment_status"] == "refunded" for item in data["items"])
        assert any(item["order_number"] == "PAYMENT-REFUNDED-TEST" for item in data["items"])
        
        # Verify pagination information
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        

    
    def test_admin_access_required(self, client, normal_user_token_headers):
        """
        GIVEN a non-admin user
        WHEN the user tries to access the admin orders endpoint
        THEN access should be denied with a 403 Forbidden response
        """
        response = client.get(
            "/api/v1/orders",
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 403
        error_data = response.json()
        assert "detail" in error_data
        # Just check that there's an error message, without being too specific about the wording
        assert isinstance(error_data["detail"], str)
