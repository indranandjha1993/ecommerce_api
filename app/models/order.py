import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class OrderStatus(str, enum.Enum):
    """Enum for order status."""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentStatus(str, enum.Enum):
    """Enum for payment status."""
    PENDING = "pending"
    AUTHORIZED = "authorized"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    VOIDED = "voided"
    FAILED = "failed"


class Order(Base):
    """Order model for managing customer orders."""

    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Can be null for guest orders

    # Status information
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    # Financial information
    subtotal = Column(Numeric(precision=10, scale=2), nullable=False)
    shipping_amount = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    tax_amount = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    discount_amount = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    total_amount = Column(Numeric(precision=10, scale=2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")

    # Customer information
    customer_email = Column(String(255), nullable=False)
    customer_name = Column(String(255), nullable=True)
    customer_phone = Column(String(50), nullable=True)
    customer_notes = Column(Text, nullable=True)

    # Address information
    shipping_address_id = Column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=True)
    billing_address_id = Column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=True)

    # Shipping information
    shipping_method = Column(String(100), nullable=True)
    tracking_number = Column(String(100), nullable=True)
    estimated_delivery = Column(DateTime, nullable=True)

    # Payment information
    payment_method = Column(String(100), nullable=True)
    payment_details = Column(JSONB, nullable=True)  # Encrypted or tokenized payment details

    # Coupon information
    coupon_code = Column(String(50), nullable=True)

    # Additional data
    order_metadata = Column(JSONB, nullable=True)

    # Guest orders use a unique token for lookup
    guest_token = Column(String(255), nullable=True, unique=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # If order was created from a cart
    cart_id = Column(UUID(as_uuid=True), ForeignKey("carts.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    shipping_address = relationship("Address", foreign_keys=[shipping_address_id], back_populates="shipping_orders")
    billing_address = relationship("Address", foreign_keys=[billing_address_id], back_populates="billing_orders")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    shipping_details = relationship("Shipping", back_populates="order", cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, order_number={self.order_number}, status={self.status})>"

    @property
    def is_paid(self):
        """Check if the order is paid."""
        return self.payment_status in [PaymentStatus.PAID, PaymentStatus.PARTIALLY_REFUNDED]

    @property
    def can_be_cancelled(self):
        """Check if the order can be cancelled."""
        return self.status in [OrderStatus.PENDING, OrderStatus.PROCESSING, OrderStatus.ON_HOLD]

    @property
    def can_be_refunded(self):
        """Check if the order can be refunded."""
        return self.is_paid and self.status not in [OrderStatus.REFUNDED, OrderStatus.FAILED, OrderStatus.CANCELLED]


class OrderItem(Base):
    """Order item model for items in an order."""

    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)

    # Product information
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=True)

    # Snapshot of product information at time of purchase
    product_name = Column(String(255), nullable=False)
    product_sku = Column(String(100), nullable=True)
    variant_name = Column(String(255), nullable=True)

    # Pricing and quantity
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(precision=10, scale=2), nullable=False)
    subtotal = Column(Numeric(precision=10, scale=2), nullable=False)
    tax_amount = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    discount_amount = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    total_amount = Column(Numeric(precision=10, scale=2), nullable=False)

    # Additional information
    options = Column(JSONB, nullable=True)  # Store selected options, customizations

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant", back_populates="order_items")
    refund_items = relationship("RefundItem", back_populates="order_item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, product={self.product_name}, quantity={self.quantity})>"


class Refund(Base):
    """Refund model for managing order refunds."""

    __tablename__ = "refunds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)

    # Refund information
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    reason = Column(Text, nullable=True)

    # Payment information
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=True)
    transaction_id = Column(String(255), nullable=True)

    # Status
    status = Column(String(50), default="pending")

    # User who processed the refund
    refunded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Additional data
    refund_metadata = Column(JSONB, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="refunds")
    payment = relationship("Payment")
    items = relationship("RefundItem", back_populates="refund", cascade="all, delete-orphan")
    admin = relationship("User", foreign_keys=[refunded_by])

    def __repr__(self):
        return f"<Refund(id={self.id}, order_id={self.order_id}, amount={self.amount})>"


class RefundItem(Base):
    """Refund item model for items in a refund."""

    __tablename__ = "refund_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    refund_id = Column(UUID(as_uuid=True), ForeignKey("refunds.id"), nullable=False)
    order_item_id = Column(UUID(as_uuid=True), ForeignKey("order_items.id"), nullable=False)

    # Refund information
    quantity = Column(Integer, nullable=False)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    reason = Column(Text, nullable=True)

    # Additional data
    refund_item_metadata = Column(JSONB, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    refund = relationship("Refund", back_populates="items")
    order_item = relationship("OrderItem", back_populates="refund_items")

    def __repr__(self):
        return f"<RefundItem(id={self.id}, order_item_id={self.order_item_id}, quantity={self.quantity})>"
