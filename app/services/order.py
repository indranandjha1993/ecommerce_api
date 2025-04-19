import secrets
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.payment import Payment, PaymentProvider, PaymentType
from app.models.shipping import Shipping, ShippingStatus, ShippingCarrier
from app.repositories.order import order_repository
from app.schemas.order import OrderCreate, OrderUpdate, OrderAdminUpdate
from app.services.cart import cart_service
from app.utils.datetime_utils import utcnow


class OrderService:
    """
    Order service for business logic.
    """

    def get_by_id(self, db: Session, order_id: uuid.UUID) -> Order:
        """
        Get an order by ID.
        """
        order = order_repository.get_with_relations(db, id=order_id)
        if not order:
            raise NotFoundException(detail="Order not found")
        return order

    def get_by_order_number(self, db: Session, order_number: str) -> Order:
        """
        Get an order by order number.
        """
        order = order_repository.get_by_order_number_with_relations(db, order_number=order_number)
        if not order:
            raise NotFoundException(detail="Order not found")
        return order

    def get_by_guest_token(self, db: Session, guest_token: str) -> Order:
        """
        Get an order by guest token.
        """
        order = order_repository.get_by_guest_token(db, guest_token=guest_token)
        if not order:
            raise NotFoundException(detail="Order not found")
        return order

    def get_user_orders(
            self, db: Session, user_id: uuid.UUID, page: int = 1, size: int = 20
    ) -> Tuple[List[Order], int]:
        """
        Get orders for a user with pagination.
        """
        skip = (page - 1) * size
        return order_repository.get_user_orders(db, user_id=user_id, skip=skip, limit=size)

    def get_orders_by_status(
            self, db: Session, status: OrderStatus, page: int = 1, size: int = 20
    ) -> Tuple[List[Order], int]:
        """
        Get orders by status with pagination.
        """
        skip = (page - 1) * size
        return order_repository.get_orders_by_status(db, status=status, skip=skip, limit=size)

    def get_all(self, db: Session, page: int = 1, size: int = 20) -> Tuple[List[Order], int]:
        """
        Get all orders with pagination.
        """
        skip = (page - 1) * size
        orders = order_repository.get_multi(db, skip=skip, limit=size)
        total = order_repository.get_count(db)
        return orders, total

    def create_from_cart(
            self, db: Session, cart_id: uuid.UUID, order_data: OrderCreate, user_id: Optional[uuid.UUID] = None
    ) -> Order:
        """
        Create an order from a cart.
        """
        # Get the cart with items
        cart = cart_service.get_cart_by_id(db, cart_id=cart_id)

        # Verify cart has items
        if not cart.items:
            raise BadRequestException(detail="Cart is empty")

        # Check inventory for each item
        from app.models.inventory import Inventory

        for item in cart.items:
            if item.variant_id:
                inventory = db.query(Inventory).filter(
                    Inventory.product_id == item.product_id,
                    Inventory.variant_id == item.variant_id
                ).first()
            else:
                inventory = db.query(Inventory).filter(
                    Inventory.product_id == item.product_id,
                    Inventory.variant_id.is_(None)
                ).first()

            if not inventory or inventory.quantity < item.quantity:
                product_name = item.product.name
                if item.variant:
                    product_name += f" ({item.variant.name})"
                raise BadRequestException(detail=f"Not enough stock for {product_name}")

        # Create shipping address
        from app.models.address import Address

        shipping_address = Address(
            user_id=user_id,
            address_type="shipping",
            **order_data.shipping_address.model_dump()
        )
        db.add(shipping_address)
        db.flush()

        # Create billing address if needed
        if order_data.use_shipping_for_billing:
            billing_address_id = shipping_address.id
        elif order_data.billing_address:
            billing_address = Address(
                user_id=user_id,
                address_type="billing",
                **order_data.billing_address.model_dump()
            )
            db.add(billing_address)
            db.flush()
            billing_address_id = billing_address.id
        else:
            billing_address_id = None

        # Calculate order totals
        subtotal = cart.subtotal
        shipping_amount = Decimal("0.00")  # Will be calculated based on shipping method

        # Apply tax rate (simplified - would be more complex in real application)
        tax_rate = Decimal("0.10")  # 10% tax rate
        tax_amount = subtotal * tax_rate

        # Apply discount from coupon if any
        discount_amount = Decimal("0.00")
        coupon_code = None

        if cart.cart_metadata and "coupon_code" in cart.cart_metadata:
            coupon_code = cart.cart_metadata["coupon_code"]
            # Calculate discount (simplified - would be more complex in real application)
            from app.models.coupon import Coupon, DiscountType

            coupon = db.query(Coupon).filter(Coupon.code == coupon_code).first()
            if coupon:
                if coupon.discount_type == DiscountType.PERCENTAGE:
                    discount_amount = subtotal * (coupon.discount_value / 100)
                elif coupon.discount_type == DiscountType.FIXED_AMOUNT:
                    discount_amount = min(subtotal, coupon.discount_value)
                elif coupon.discount_type == DiscountType.FREE_SHIPPING:
                    shipping_amount = Decimal("0.00")

        # Calculate total
        total_amount = subtotal + shipping_amount + tax_amount - discount_amount

        # Generate unique order number
        order_number = order_repository.generate_order_number(db)

        # Generate guest token if user is not authenticated
        guest_token = None
        if not user_id:
            guest_token = secrets.token_urlsafe(32)

        # Create order
        order = Order(
            order_number=order_number,
            user_id=user_id,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            subtotal=subtotal,
            shipping_amount=shipping_amount,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            currency="USD",  # Default currency
            customer_email=order_data.customer_email,
            customer_name=order_data.customer_name,
            customer_phone=order_data.customer_phone,
            customer_notes=order_data.customer_notes,
            shipping_address_id=shipping_address.id,
            billing_address_id=billing_address_id,
            shipping_method=order_data.shipping_method,
            payment_method=order_data.payment_method,
            payment_details=order_data.payment_details,
            coupon_code=coupon_code,
            order_metadata=order_data.order_metadata,
            guest_token=guest_token,
            cart_id=cart.id,
        )
        db.add(order)
        db.flush()

        # Create order items
        for cart_item in cart.items:
            product = cart_item.product
            variant = cart_item.variant

            # Determine unit price
            if cart_item.unit_price is not None:
                unit_price = cart_item.unit_price
            elif variant and variant.price is not None:
                unit_price = variant.price
            else:
                unit_price = product.price

            # Calculate item tax
            item_tax = unit_price * cart_item.quantity * tax_rate

            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                variant_id=variant.id if variant else None,
                product_name=product.name,
                product_sku=product.sku,
                variant_name=variant.name if variant else None,
                quantity=cart_item.quantity,
                unit_price=unit_price,
                subtotal=unit_price * cart_item.quantity,
                tax_amount=item_tax,
                discount_amount=Decimal("0.00"),  # Item-level discounts would be calculated here
                total_amount=(unit_price * cart_item.quantity) + item_tax,
                options=cart_item.item_metadata,
            )
            db.add(order_item)

            # Update inventory
            if variant:
                inventory = db.query(Inventory).filter(
                    Inventory.product_id == product.id,
                    Inventory.variant_id == variant.id
                ).first()
            else:
                inventory = db.query(Inventory).filter(
                    Inventory.product_id == product.id,
                    Inventory.variant_id.is_(None)
                ).first()

            if inventory:
                inventory.quantity -= cart_item.quantity
                db.add(inventory)

        # Create a new shipping record
        shipping = Shipping(
            order_id=order.id,
            status=ShippingStatus.PENDING,
            shipping_method=order_data.shipping_method,
        )
        db.add(shipping)

        # Mark cart as inactive
        cart.is_active = False
        db.add(cart)

        db.commit()
        db.refresh(order)

        return order

    def update(self, db: Session, order_id: uuid.UUID, order_in: OrderUpdate) -> Order:
        """
        Update an order.
        """
        order = order_repository.get(db, id=order_id)
        if not order:
            raise NotFoundException(detail="Order not found")

        # Update order fields
        update_data = order_in.model_dump(exclude_unset=True)

        # Handle status change
        if "status" in update_data:
            new_status = update_data["status"]

            # Validate status transition
            self._validate_status_transition(order.status, new_status)

            # Set completed_at timestamp if order is being completed
            if new_status == OrderStatus.COMPLETED and not order.completed_at:
                from datetime import datetime
                update_data["completed_at"] = utcnow()

        # Update order
        order = order_repository.update(db, db_obj=order, obj_in=update_data)

        return order

    def update_admin(self, db: Session, order_id: uuid.UUID, order_in: OrderAdminUpdate) -> Order:
        """
        Update an order with admin privileges.
        """
        order = order_repository.get(db, id=order_id)
        if not order:
            raise NotFoundException(detail="Order not found")

        # Update order fields
        update_data = order_in.model_dump(exclude_unset=True)

        # Handle status change
        if "status" in update_data:
            new_status = update_data["status"]

            # Set completed_at timestamp if order is being completed
            if new_status == OrderStatus.COMPLETED and not order.completed_at:
                from datetime import datetime
                update_data["completed_at"] = utcnow()

        # Update order
        order = order_repository.update(db, db_obj=order, obj_in=update_data)

        return order

    def cancel_order(self, db: Session, order_id: uuid.UUID) -> Order:
        """
        Cancel an order.
        """
        order = order_repository.get_with_relations(db, id=order_id)
        if not order:
            raise NotFoundException(detail="Order not found")

        # Check if order can be cancelled
        if not order.can_be_cancelled:
            raise BadRequestException(detail="This order cannot be cancelled")

        # Update order status
        order = order_repository.update_status(db, order_id=order_id, status=OrderStatus.CANCELLED)

        # Restore inventory
        from app.models.inventory import Inventory

        for item in order.items:
            if item.variant_id:
                inventory = db.query(Inventory).filter(
                    Inventory.product_id == item.product_id,
                    Inventory.variant_id == item.variant_id
                ).first()
            else:
                inventory = db.query(Inventory).filter(
                    Inventory.product_id == item.product_id,
                    Inventory.variant_id.is_(None)
                ).first()

            if inventory:
                inventory.quantity += item.quantity
                db.add(inventory)

        db.commit()
        db.refresh(order)

        return order

    def process_payment(
            self, db: Session, order_id: uuid.UUID,
            provider: PaymentProvider, amount: Decimal,
            payment_data: Dict[str, Any]
    ) -> Payment:
        """
        Process a payment for an order.
        """
        order = order_repository.get(db, id=order_id)
        if not order:
            raise NotFoundException(detail="Order not found")

        # Create payment record
        payment = Payment(
            order_id=order.id,
            amount=amount,
            currency=order.currency,
            provider=provider,
            payment_type=PaymentType.PAYMENT,
            status="pending",
            transaction_id=payment_data.get("transaction_id"),
            payment_method_id=payment_data.get("payment_method_id"),
            payment_intent_id=payment_data.get("payment_intent_id"),
            last_four=payment_data.get("last_four"),
            card_type=payment_data.get("card_type"),
            expiry_month=payment_data.get("expiry_month"),
            expiry_year=payment_data.get("expiry_year"),
            cardholder_name=payment_data.get("cardholder_name"),
            payment_metadata=payment_data.get("metadata"),
        )
        db.add(payment)

        # Update payment status based on provider
        if provider == PaymentProvider.CASH_ON_DELIVERY:
            # For COD, payment is pending until delivery
            payment.status = "pending"
            order.payment_status = PaymentStatus.PENDING
            order.status = OrderStatus.PROCESSING
        elif provider == PaymentProvider.BANK_TRANSFER:
            # For bank transfer, payment is pending until confirmed
            payment.status = "pending"
            order.payment_status = PaymentStatus.PENDING
            order.status = OrderStatus.ON_HOLD
        else:
            # For credit card, PayPal, etc., payment is usually processed immediately
            payment.status = "completed"
            order.payment_status = PaymentStatus.PAID
            order.status = OrderStatus.PROCESSING

        db.add(order)
        db.commit()
        db.refresh(payment)

        return payment

    def update_shipping(
            self, db: Session, order_id: uuid.UUID,
            carrier: Optional[ShippingCarrier] = None,
            tracking_number: Optional[str] = None,
            status: Optional[ShippingStatus] = None
    ) -> Shipping:
        """
        Update shipping information for an order.
        """
        order = order_repository.get(db, id=order_id)
        if not order:
            raise NotFoundException(detail="Order not found")

        # Get or create shipping record
        shipping = db.query(Shipping).filter(Shipping.order_id == order_id).first()
        if not shipping:
            shipping = Shipping(order_id=order_id, status=ShippingStatus.PENDING)
            db.add(shipping)
            db.flush()

        # Update shipping fields
        if carrier:
            shipping.carrier = carrier
        if tracking_number:
            shipping.tracking_number = tracking_number
        if status:
            shipping.status = status

            # Update shipped_at and delivered_at timestamps
            from datetime import datetime
            if status == ShippingStatus.IN_TRANSIT and not shipping.shipped_at:
                shipping.shipped_at = utcnow()
            elif status == ShippingStatus.DELIVERED and not shipping.delivered_at:
                shipping.delivered_at = utcnow()

            # Update order status based on shipping status
            if status == ShippingStatus.DELIVERED:
                order.status = OrderStatus.DELIVERED
                db.add(order)

        db.add(shipping)
        db.commit()
        db.refresh(shipping)

        return shipping

    def _validate_status_transition(self, current_status: OrderStatus, new_status: OrderStatus) -> bool:
        """
        Validate order status transition.
        """
        # Define valid status transitions
        valid_transitions = {
            OrderStatus.PENDING: [
                OrderStatus.PROCESSING,
                OrderStatus.ON_HOLD,
                OrderStatus.CANCELLED
            ],
            OrderStatus.PROCESSING: [
                OrderStatus.SHIPPED,
                OrderStatus.ON_HOLD,
                OrderStatus.CANCELLED
            ],
            OrderStatus.ON_HOLD: [
                OrderStatus.PROCESSING,
                OrderStatus.CANCELLED
            ],
            OrderStatus.SHIPPED: [
                OrderStatus.DELIVERED,
                OrderStatus.RETURNED,
                OrderStatus.FAILED
            ],
            OrderStatus.DELIVERED: [
                OrderStatus.COMPLETED,
                OrderStatus.RETURNED
            ],
            OrderStatus.COMPLETED: [
                OrderStatus.RETURNED,
                OrderStatus.REFUNDED
            ],
            OrderStatus.RETURNED: [
                OrderStatus.REFUNDED
            ],
            OrderStatus.CANCELLED: [
                OrderStatus.REFUNDED
            ],
            OrderStatus.REFUNDED: [
            ],
            OrderStatus.FAILED: [
                OrderStatus.PROCESSING,
                OrderStatus.CANCELLED
            ],
        }

        # Check if transition is valid
        if new_status not in valid_transitions.get(current_status, []):
            raise BadRequestException(
                detail=f"Invalid status transition from {current_status} to {new_status}"
            )

        return True


order_service = OrderService()
