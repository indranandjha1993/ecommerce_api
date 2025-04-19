import datetime
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.schemas.brand import Brand
from app.schemas.category import Category
from pydantic import BaseModel


# ProductImage schemas
class ProductImageBase(BaseModel):
    """Base product image schema with common properties."""
    image_url: str
    alt_text: Optional[str] = None
    is_primary: Optional[bool] = False
    display_order: Optional[int] = 0


class ProductImageCreate(ProductImageBase):
    """Schema for product image creation."""
    pass


class ProductImageUpdate(ProductImageBase):
    """Schema for product image update."""
    image_url: Optional[str] = None


class ProductImageInDBBase(ProductImageBase):
    """Base schema for product images in DB."""
    id: uuid.UUID
    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class ProductImage(ProductImageInDBBase):
    """Schema for product image response."""
    pass


# ProductAttribute schemas
class ProductAttributeBase(BaseModel):
    """Base product attribute schema with common properties."""
    name: str
    slug: str
    description: Optional[str] = None


class ProductAttributeCreate(ProductAttributeBase):
    """Schema for product attribute creation."""
    pass


class ProductAttributeUpdate(ProductAttributeBase):
    """Schema for product attribute update."""
    name: Optional[str] = None
    slug: Optional[str] = None


class ProductAttributeInDBBase(ProductAttributeBase):
    """Base schema for product attributes in DB."""
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class ProductAttribute(ProductAttributeInDBBase):
    """Schema for product attribute response."""
    pass


# ProductAttributeValue schemas
class ProductAttributeValueBase(BaseModel):
    """Base product attribute value schema with common properties."""
    value: str


class ProductAttributeValueCreate(ProductAttributeValueBase):
    """Schema for product attribute value creation."""
    attribute_id: uuid.UUID


class ProductAttributeValueUpdate(ProductAttributeValueBase):
    """Schema for product attribute value update."""
    value: Optional[str] = None


class ProductAttributeValueInDBBase(ProductAttributeValueBase):
    """Base schema for product attribute values in DB."""
    id: uuid.UUID
    product_id: uuid.UUID
    attribute_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class ProductAttributeValueWithAttribute(ProductAttributeValueInDBBase):
    """Schema for product attribute value with attribute response."""
    attribute: ProductAttribute


class ProductAttributeValue(ProductAttributeValueInDBBase):
    """Schema for product attribute value response."""
    pass


# ProductVariant schemas
class ProductVariantAttributeBase(BaseModel):
    """Base product variant attribute schema with common properties."""
    attribute_id: uuid.UUID
    attribute_value_id: uuid.UUID


class ProductVariantAttributeCreate(ProductVariantAttributeBase):
    """Schema for product variant attribute creation."""
    pass


class ProductVariantAttributeInDB(ProductVariantAttributeBase):
    """Schema for product variant attribute in DB."""
    id: uuid.UUID
    variant_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class ProductVariantAttribute(BaseModel):
    """Schema for product variant attribute response."""
    attribute: ProductAttribute
    attribute_value: ProductAttributeValue

    class Config:
        from_attributes = True


class ProductVariantBase(BaseModel):
    """Base product variant schema with common properties."""
    name: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    price: Optional[Decimal] = None
    compare_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    weight: Optional[float] = None
    weight_unit: Optional[str] = None
    is_active: Optional[bool] = True
    additional_data: Optional[Dict[str, Any]] = None


class ProductVariantCreate(ProductVariantBase):
    """Schema for product variant creation."""
    attributes: List[ProductVariantAttributeCreate]


class ProductVariantUpdate(ProductVariantBase):
    """Schema for product variant update."""
    attributes: Optional[List[ProductVariantAttributeCreate]] = None


class ProductVariantInDBBase(ProductVariantBase):
    """Base schema for product variants in DB."""
    id: uuid.UUID
    product_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class ProductVariant(ProductVariantInDBBase):
    """Schema for product variant response."""
    variant_attributes: List[ProductVariantAttribute] = []
    images: List[ProductImage] = []
    inventory_quantity: Optional[int] = 0


# Product schemas
class ProductBase(BaseModel):
    """Base product schema with common properties."""
    name: str
    slug: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Decimal
    compare_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    weight: Optional[float] = None
    weight_unit: Optional[str] = None
    is_active: Optional[bool] = True
    is_featured: Optional[bool] = False
    is_digital: Optional[bool] = False
    is_taxable: Optional[bool] = True
    tax_class: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class ProductCreate(ProductBase):
    """Schema for product creation."""
    category_id: Optional[uuid.UUID] = None
    brand_id: Optional[uuid.UUID] = None
    attributes: Optional[List[ProductAttributeValueCreate]] = None
    variants: Optional[List[ProductVariantCreate]] = None
    images: Optional[List[ProductImageCreate]] = None


class ProductUpdate(BaseModel):
    """Schema for product update."""
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Optional[Decimal] = None
    compare_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    weight: Optional[float] = None
    weight_unit: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_digital: Optional[bool] = None
    is_taxable: Optional[bool] = None
    tax_class: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    brand_id: Optional[uuid.UUID] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class ProductInDBBase(ProductBase):
    """Base schema for products in DB."""
    id: uuid.UUID
    category_id: Optional[uuid.UUID] = None
    brand_id: Optional[uuid.UUID] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class ProductInDB(ProductInDBBase):
    """Schema for product stored in DB."""
    pass


class ProductWithRelations(ProductInDBBase):
    """Schema for product with related entities."""
    category: Optional[Category] = None
    brand: Optional[Brand] = None
    images: List[ProductImage] = []
    variants: List[ProductVariant] = []
    attribute_values: List[ProductAttributeValueWithAttribute] = []
    average_rating: Optional[float] = None
    inventory_quantity: Optional[int] = 0


class Product(ProductInDBBase):
    """Schema for product response."""
    category: Optional[Category] = None
    brand: Optional[Brand] = None
    primary_image: Optional[ProductImage] = None
    inventory_quantity: Optional[int] = 0
    average_rating: Optional[float] = None


# Product list responses
class ProductListItem(BaseModel):
    """Schema for product list item."""
    id: uuid.UUID
    name: str
    slug: str
    price: Decimal
    compare_price: Optional[Decimal] = None
    primary_image: Optional[ProductImage] = None
    is_in_stock: Optional[bool] = True  # Make it optional with default True
    average_rating: Optional[float] = None
    category: Optional[Category] = None
    brand: Optional[Brand] = None

    class Config:
        from_attributes = True


class ProductList(BaseModel):
    """Schema for product list response."""
    items: List[ProductListItem]
    total: int
    page: int
    size: int
    pages: int


# Product search
class ProductSearchQuery(BaseModel):
    """Schema for product search query."""
    query: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    brand_id: Optional[uuid.UUID] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    in_stock: Optional[bool] = None
    attributes: Optional[Dict[str, List[str]]] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"
    page: Optional[int] = 1
    size: Optional[int] = 20
