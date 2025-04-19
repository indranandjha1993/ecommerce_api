import datetime
import uuid
from decimal import Decimal
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, field_validator

from app.models.coupon import DiscountType


# Coupon schemas
class CouponBase(BaseModel):
    """Base coupon schema with common properties."""
    code: str
    name: Optional[str] = None
    description: Optional[str] = None
    discount_type: DiscountType
    discount_value: Decimal
    buy_quantity: Optional[int] = None
    get_quantity: Optional[int] = None
    usage_limit: Optional[int] = None
    usage_limit_per_user: Optional[int] = None
    minimum_order_amount: Optional[Decimal] = None
    minimum_quantity: Optional[int] = None
    is_active: bool = True
    starts_at: Optional[datetime.datetime] = None
    expires_at: Optional[datetime.datetime] = None
    is_first_order_only: bool = False
    is_one_time_use: bool = False
    applies_to_all_products: bool = True
    product_ids: Optional[List[uuid.UUID]] = None
    category_ids: Optional[List[uuid.UUID]] = None
    exclude_product_ids: Optional[List[uuid.UUID]] = None
    exclude_category_ids: Optional[List[uuid.UUID]] = None
    applies_to_all_customers: bool = True
    customer_ids: Optional[List[uuid.UUID]] = None
    coupon_metadata: Optional[Dict[str, Any]] = None

    @field_validator('code')
    def code_must_be_uppercase(cls, v):
        """Validate that the coupon code is uppercase."""
        return v.upper()

    @field_validator('discount_value')
    def validate_discount_value(cls, v, values):
        """Validate discount value based on discount type."""
        if 'discount_type' in values:
            if values['discount_type'] == DiscountType.PERCENTAGE and v > 100:
                raise ValueError("Percentage discount cannot exceed 100%")
        return v

    @field_validator('buy_quantity', 'get_quantity')
    def validate_buy_x_get_y(cls, v, values):
        """Validate buy X get Y quantities."""
        if 'discount_type' in values and values['discount_type'] == DiscountType.BUY_X_GET_Y:
            if v is None or v <= 0:
                raise ValueError("Buy X Get Y quantities must be positive")
        return v


class CouponCreate(CouponBase):
    """Schema for coupon creation."""
    pass


class CouponUpdate(BaseModel):
    """Schema for coupon update."""
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[Decimal] = None
    buy_quantity: Optional[int] = None
    get_quantity: Optional[int] = None
    usage_limit: Optional[int] = None
    usage_limit_per_user: Optional[int] = None
    minimum_order_amount: Optional[Decimal] = None
    minimum_quantity: Optional[int] = None
    is_active: Optional[bool] = None
    starts_at: Optional[datetime.datetime] = None
    expires_at: Optional[datetime.datetime] = None
    is_first_order_only: Optional[bool] = None
    is_one_time_use: Optional[bool] = None
    applies_to_all_products: Optional[bool] = None
    product_ids: Optional[List[uuid.UUID]] = None
    category_ids: Optional[List[uuid.UUID]] = None
    exclude_product_ids: Optional[List[uuid.UUID]] = None
    exclude_category_ids: Optional[List[uuid.UUID]] = None
    applies_to_all_customers: Optional[bool] = None
    customer_ids: Optional[List[uuid.UUID]] = None
    coupon_metadata: Optional[Dict[str, Any]] = None

    @field_validator('code')
    def code_must_be_uppercase(cls, v):
        """Validate that the coupon code is uppercase."""
        if v is not None:
            return v.upper()
        return v

    @field_validator('discount_value')
    def validate_discount_value(cls, v, values):
        """Validate discount value based on discount type."""
        if v is not None and 'discount_type' in values and values['discount_type'] is not None:
            if values['discount_type'] == DiscountType.PERCENTAGE and v > 100:
                raise ValueError("Percentage discount cannot exceed 100%")
        return v


class CouponInDBBase(CouponBase):
    """Base schema for coupons in DB."""
    id: uuid.UUID
    current_usage_count: int = 0
    created_at: datetime.datetime
    updated_at: datetime.datetime
    created_by: Optional[uuid.UUID] = None

    model_config = {"from_attributes": True}


class Coupon(CouponInDBBase):
    """Schema for coupon response."""
    is_expired: bool
    is_started: bool
    is_valid: bool
    is_usage_limit_reached: bool


# Coupon Usage schemas
class CouponUsageBase(BaseModel):
    """Base coupon usage schema with common properties."""
    coupon_id: uuid.UUID
    order_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    discount_amount: Decimal


class CouponUsageInDBBase(CouponUsageBase):
    """Base schema for coupon usage in DB."""
    id: uuid.UUID
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class CouponUsage(CouponUsageInDBBase):
    """Schema for coupon usage response."""
    pass


# Coupon List schemas
class CouponList(BaseModel):
    """Schema for coupon list response."""
    items: List[Coupon]
    total: int
    page: int
    size: int
    pages: int


# Coupon Validation schemas
class CouponValidationRequest(BaseModel):
    """Schema for coupon validation request."""
    code: str
    order_total: Optional[Decimal] = None
    items: Optional[List[Dict[str, Any]]] = None


class CouponValidationResponse(BaseModel):
    """Schema for coupon validation response."""
    coupon: Coupon
    discount_amount: Decimal
    message: str = "Coupon is valid"


# Coupon Application schemas
class CouponApplicationRequest(BaseModel):
    """Schema for coupon application request."""
    code: str
    order_id: uuid.UUID
    order_total: Decimal
    items: Optional[List[Dict[str, Any]]] = None


class CouponApplicationResponse(BaseModel):
    """Schema for coupon application response."""
    coupon: Coupon
    discount_amount: Decimal
    message: str = "Coupon applied successfully"
