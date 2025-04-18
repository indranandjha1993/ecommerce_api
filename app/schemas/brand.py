import datetime
import uuid
from typing import List, Optional

from pydantic import BaseModel


# Shared properties
class BrandBase(BaseModel):
    """Base brand schema with common properties."""
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = True
    is_featured: Optional[bool] = False


# Properties to receive via API on creation
class BrandCreate(BrandBase):
    """Schema for brand creation."""
    pass


# Properties to receive via API on update
class BrandUpdate(BaseModel):
    """Schema for brand update."""
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


# Properties shared by models stored in DB
class BrandInDBBase(BrandBase):
    """Base schema for brands in DB."""
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True


# Properties to return to client
class Brand(BrandInDBBase):
    """Schema for brand response."""
    product_count: Optional[int] = 0


# Schema for brand list
class BrandList(BaseModel):
    """Schema for brand list response."""
    items: List[Brand]
    total: int
    page: int
    size: int
    pages: int
