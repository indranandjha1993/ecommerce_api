import datetime
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.models.order import OrderStatus, PaymentStatus
from app.schemas.address import OrderAddress
from app.schemas.product import Product, ProductVariant


# OrderItem schemas
class OrderItemBase(BaseModel):
    """Base order item schema with common properties."""
    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None
    quantity: int
    unit_price: Decimal
    product_name: str
    product_sku: Optional[str] = None
    variant_name: Optional[str] = None
    tax_amount: Decimal = Decimal("0.00")
    discount_amount: Decimal = Decimal("0.00")
    options: Optional[Dict[str, Any]] = None


class OrderItemCreate(OrderItemBase):
    """Schema for order item creation."""
    pass


class OrderItemInDBBase(OrderItemBase):
    """Base schema for order items in DB."""
    id: uuid.UUID
    order_id: uuid.UUID
    subtotal: Decimal
    total_amount: Decimal
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class OrderItem(OrderItemInDBBase):
    """Schema for order item response."""
    product: Optional[Product] = None
    variant: Optional[ProductVariant] = None


# Payment schemas
class PaymentBase(BaseModel):
    """Base payment schema with common properties."""
    amount: Decimal
    provider: str
    status: str
    transaction_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    payment_intent_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    payment_metadata: Optional[Dict[str, Any]] = None


class PaymentCreate(PaymentBase):
    """Schema for payment creation."""
    payment_type: str = "payment"
    currency: str = "USD"


class PaymentInDBBase(PaymentBase):
    """Base schema for payments in DB."""
    id: uuid.UUID
    order_id: uuid.UUID
    currency: str
    payment_type: str
    last_four: Optional[str] = None
    card_type: Optional[str] = None
    expiry_month: Optional[str] = None
    expiry_year: Optional[str] = None
    cardholder_name: Optional[str] = None
    is_3d_secure: bool = False
    risk_level: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    processed_at: Optional[datetime.datetime] = None

    model_config = {"from_attributes": True}


class Payment(PaymentInDBBase):
    """Schema for payment response."""
    pass


# Shipping schemas
class ShippingBase(BaseModel):
    """Base shipping schema with common properties."""
    carrier: Optional[str] = None
    carrier_name: Optional[str] = None
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None
    status: str
    shipping_method: Optional[str] = None
    shipping_rate: Optional[Decimal] = None
    estimated_delivery: Optional[datetime.datetime] = None
    notes: Optional[str] = None
    shipping_metadata: Optional[Dict[str, Any]] = None


class ShippingCreate(ShippingBase):
    """Schema for shipping creation."""
    pass


class ShippingInDBBase(ShippingBase):
    """Base schema for shipping in DB."""
    id: uuid.UUID
    order_id: uuid.UUID
    package_weight: Optional[Decimal] = None
    package_weight_unit: Optional[str] = None
    package_dimensions: Optional[str] = None
    package_dimensions_unit: Optional[str] = None
    shipped_at: Optional[datetime.datetime] = None
    delivered_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class Shipping(ShippingInDBBase):
    """Schema for shipping response."""
    tracking_link: Optional[str] = None


# Order schemas
class OrderBase(BaseModel):
    """Base order schema with common properties."""
    customer_email: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_notes: Optional[str] = None
    shipping_method: Optional[str] = None
    payment_method: Optional[str] = None
    payment_details: Optional[Dict[str, Any]] = None
    coupon_code: Optional[str] = None
    order_metadata: Optional[Dict[str, Any]] = None


class OrderCreate(OrderBase):
    """Schema for order creation."""
    cart_id: Optional[uuid.UUID] = None
    shipping_address: OrderAddress
    billing_address: Optional[OrderAddress] = None
    use_shipping_for_billing: bool = True


class OrderUpdate(BaseModel):
    """Schema for order update."""
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    customer_notes: Optional[str] = None
    shipping_method: Optional[str] = None
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[datetime.datetime] = None
    payment_method: Optional[str] = None
    order_metadata: Optional[Dict[str, Any]] = None


class OrderAdminUpdate(OrderUpdate):
    """Schema for order update by admin."""
    subtotal: Optional[Decimal] = None
    shipping_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None


class OrderInDBBase(OrderBase):
    """Base schema for orders in DB."""
    id: uuid.UUID
    order_number: str
    user_id: Optional[uuid.UUID] = None
    status: OrderStatus
    payment_status: PaymentStatus
    subtotal: Decimal
    shipping_amount: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    currency: str
    shipping_address_id: Optional[uuid.UUID] = None
    billing_address_id: Optional[uuid.UUID] = None
    guest_token: Optional[str] = None
    cart_id: Optional[uuid.UUID] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None

    model_config = {"from_attributes": True}


class OrderInDB(OrderInDBBase):
    """Schema for order stored in DB."""
    pass


class Order(OrderInDBBase):
    """Schema for order response."""
    items: List[OrderItem] = []
    shipping_address: Optional[OrderAddress] = None
    billing_address: Optional[OrderAddress] = None
    payments: List[Payment] = []
    shipping_details: List[Shipping] = []


# Order summary (lightweight version for lists)
class OrderSummary(BaseModel):
    """Schema for order summary response."""
    id: uuid.UUID
    order_number: str
    status: OrderStatus
    payment_status: PaymentStatus
    total_amount: Decimal
    currency: str
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    item_count: int

    model_config = {"from_attributes": True}


# Order list
class OrderList(BaseModel):
    """Schema for order list response."""
    items: List[OrderSummary]
    total: int
    page: int
    size: int
    pages: int
