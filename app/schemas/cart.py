import datetime
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.schemas.product import Product, ProductVariant


# CartItem schemas
class CartItemBase(BaseModel):
    """Base cart item schema with common properties."""
    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None
    quantity: int = 1
    item_metadata: Optional[Dict[str, Any]] = None


class CartItemCreate(CartItemBase):
    """Schema for cart item creation."""
    pass


class CartItemUpdate(BaseModel):
    """Schema for cart item update."""
    quantity: int


class CartItemInDBBase(CartItemBase):
    """Base schema for cart items in DB."""
    id: uuid.UUID
    cart_id: uuid.UUID
    unit_price: Optional[Decimal] = None
    added_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class CartItemInDB(CartItemInDBBase):
    """Schema for cart item stored in DB."""
    pass


class CartItem(CartItemInDBBase):
    """Schema for cart item response."""
    product: Product
    variant: Optional[ProductVariant] = None
    subtotal: Decimal


# Cart schemas
class CartBase(BaseModel):
    """Base cart schema with common properties."""
    cart_metadata: Optional[Dict[str, Any]] = None


class CartCreate(CartBase):
    """Schema for cart creation."""
    user_id: Optional[uuid.UUID] = None
    session_id: Optional[str] = None


class CartUpdate(CartBase):
    """Schema for cart update."""
    pass


class CartInDBBase(CartBase):
    """Base schema for carts in DB."""
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    session_id: Optional[str] = None
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    last_activity: datetime.datetime

    model_config = {"from_attributes": True}


class CartInDB(CartInDBBase):
    """Schema for cart stored in DB."""
    pass


class Cart(CartInDBBase):
    """Schema for cart response."""
    items: List[CartItem] = []
    subtotal: Decimal
    item_count: int


# Cart summary (lightweight version for quick access)
class CartSummary(BaseModel):
    """Schema for cart summary response."""
    id: uuid.UUID
    item_count: int
    subtotal: Decimal

    model_config = {"from_attributes": True}
