import datetime
import uuid
from typing import List, Optional

from pydantic import BaseModel

from app.models.inventory import StockStatus, StockMovementType
from app.schemas.product import Product, ProductVariant


# Inventory Location schemas
class InventoryLocationBase(BaseModel):
    """Base inventory location schema with common properties."""
    name: str
    code: str
    description: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_active: Optional[bool] = True


class InventoryLocationCreate(InventoryLocationBase):
    """Schema for inventory location creation."""
    pass


class InventoryLocationUpdate(BaseModel):
    """Schema for inventory location update."""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_active: Optional[bool] = None


class InventoryLocationInDBBase(InventoryLocationBase):
    """Base schema for inventory locations in DB."""
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class InventoryLocation(InventoryLocationInDBBase):
    """Schema for inventory location response."""
    inventory_count: Optional[int] = None


# Inventory schemas
class InventoryBase(BaseModel):
    """Base inventory schema with common properties."""
    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None
    quantity: int = 0
    reserved_quantity: int = 0
    reorder_point: Optional[int] = None
    reorder_quantity: Optional[int] = None
    location_id: Optional[uuid.UUID] = None
    bin_location: Optional[str] = None
    status: Optional[StockStatus] = StockStatus.IN_STOCK


class InventoryCreate(InventoryBase):
    """Schema for inventory creation."""
    pass


class InventoryUpdate(BaseModel):
    """Schema for inventory update."""
    quantity: Optional[int] = None
    reserved_quantity: Optional[int] = None
    reorder_point: Optional[int] = None
    reorder_quantity: Optional[int] = None
    location_id: Optional[uuid.UUID] = None
    bin_location: Optional[str] = None
    status: Optional[StockStatus] = None


class InventoryInDBBase(InventoryBase):
    """Base schema for inventory in DB."""
    id: uuid.UUID
    last_checked: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class Inventory(InventoryInDBBase):
    """Schema for inventory response."""
    product: Optional[Product] = None
    variant: Optional[ProductVariant] = None
    location: Optional[InventoryLocation] = None
    available_quantity: int


# Stock Movement schemas
class StockMovementBase(BaseModel):
    """Base stock movement schema with common properties."""
    inventory_id: uuid.UUID
    quantity: int
    movement_type: StockMovementType
    reference_id: Optional[uuid.UUID] = None
    reference_type: Optional[str] = None
    notes: Optional[str] = None
    user_id: Optional[uuid.UUID] = None


class StockMovementCreate(StockMovementBase):
    """Schema for stock movement creation."""
    pass


class StockMovementInDBBase(StockMovementBase):
    """Base schema for stock movements in DB."""
    id: uuid.UUID
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class StockMovement(StockMovementInDBBase):
    """Schema for stock movement response."""
    pass


class StockMovementList(BaseModel):
    """Schema for stock movement list response."""
    items: List[StockMovement]
    total: int
    page: int
    size: int
    pages: int


# Inventory List schemas
class InventoryList(BaseModel):
    """Schema for inventory list response."""
    items: List[Inventory]
    total: int
    page: int
    size: int
    pages: int


# Inventory Location List schemas
class InventoryLocationList(BaseModel):
    """Schema for inventory location list response."""
    items: List[InventoryLocation]
    total: int
    page: int = 1
    size: int = 100
    pages: int


# Schemas for inventory adjustments
class InventoryAdjustment(BaseModel):
    """Schema for inventory adjustment."""
    quantity: int
    notes: Optional[str] = None


class InventoryReservation(BaseModel):
    """Schema for inventory reservation."""
    quantity: int
    order_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class StockMovementFilter(BaseModel):
    """Schema for stock movement filter."""
    movement_type: Optional[StockMovementType] = None
    reference_type: Optional[str] = None
    reference_id: Optional[uuid.UUID] = None
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
