import datetime
import uuid
from typing import List, Optional

from pydantic import BaseModel


# Shared properties
class CategoryBase(BaseModel):
    """Base category schema with common properties."""
    name: str
    slug: str
    description: Optional[str] = None
    is_active: Optional[bool] = True
    image_url: Optional[str] = None
    display_order: Optional[int] = 0


# Properties to receive via API on creation
class CategoryCreate(CategoryBase):
    """Schema for category creation."""
    parent_id: Optional[uuid.UUID] = None


# Properties to receive via API on update
class CategoryUpdate(BaseModel):
    """Schema for category update."""
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    parent_id: Optional[uuid.UUID] = None
    image_url: Optional[str] = None
    display_order: Optional[int] = None


# Properties shared by models stored in DB
class CategoryInDBBase(CategoryBase):
    """Base schema for categories in DB."""
    id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


# Properties to return to client
class Category(CategoryInDBBase):
    """Schema for category response."""
    pass


# Recursive category model for tree structure
class CategoryTreeItem(Category):
    """Schema for category tree item with children."""
    children: List['CategoryTreeItem'] = []


CategoryTreeItem.model_rebuild()


# Schema for category with parent reference
class CategoryWithParent(Category):
    """Schema for category with parent reference."""
    parent: Optional[Category] = None


# Schema for category list
class CategoryList(BaseModel):
    """Schema for category list response."""
    items: List[Category]
    total: int


# Schema for category tree
class CategoryTree(BaseModel):
    """Schema for category tree response."""
    items: List[CategoryTreeItem]
