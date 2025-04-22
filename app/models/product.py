from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Product(BaseModel):
    """Product model for the main product catalog."""

    __tablename__ = "products"

    # Core product information
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(512), nullable=True)

    # Pricing information
    price = Column(Numeric(precision=10, scale=2), nullable=False)
    compare_price = Column(Numeric(precision=10, scale=2), nullable=True)
    cost_price = Column(Numeric(precision=10, scale=2), nullable=True)

    # Inventory information
    sku = Column(String(100), nullable=True, unique=True)
    barcode = Column(String(100), nullable=True, unique=True)
    weight = Column(Float, nullable=True)
    weight_unit = Column(String(10), nullable=True)

    # Product status and visibility
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_digital = Column(Boolean, default=False)
    is_taxable = Column(Boolean, default=True)
    tax_class = Column(String(100), nullable=True)

    # Relationships by ID
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id"), nullable=True)

    # SEO fields
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(String(512), nullable=True)
    meta_keywords = Column(String(512), nullable=True)

    # Additional data (can store structured or unstructured data)
    additional_data = Column(JSONB, nullable=True)

    # Relationships
    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    attribute_values = relationship("ProductAttributeValue", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product")
    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name})>"

    @property
    def average_rating(self):
        """Calculate the average rating for this product."""
        if not self.reviews:
            return None

        total = sum(review.rating for review in self.reviews)
        return total / len(self.reviews)

    @property
    def has_variants(self):
        """Check if the product has variants."""
        return len(self.variants) > 0

    @property
    def is_in_stock(self):
        """Check if the product is in stock."""
        if self.has_variants:
            return any(variant.is_in_stock for variant in self.variants)
        return self.inventory and self.inventory.quantity > 0

    @property
    def primary_image(self):
        """Get the primary image for this product."""
        primary = next((img for img in self.images if img.is_primary), None)
        if primary:
            return primary
        return self.images[0] if self.images else None


class ProductImage(BaseModel):
    """Product image model."""

    __tablename__ = "product_images"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=True)

    # Image data
    image_url = Column(String(512), nullable=False)
    alt_text = Column(String(255), nullable=True)
    is_primary = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)

    # Relationships
    product = relationship("Product", back_populates="images")
    variant = relationship("ProductVariant", back_populates="images")

    def __repr__(self):
        return f"<ProductImage(id={self.id}, product_id={self.product_id})>"


class ProductAttribute(BaseModel):
    """Product attribute model (e.g., Color, Size, Material)."""

    __tablename__ = "product_attributes"

    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # Relationships
    values = relationship("ProductAttributeValue", back_populates="attribute", cascade="all, delete-orphan")
    variant_attributes = relationship("ProductVariantAttribute", back_populates="attribute")

    def __repr__(self):
        return f"<ProductAttribute(id={self.id}, name={self.name})>"


class ProductAttributeValue(BaseModel):
    """Product attribute value model (e.g., Red, XL, Cotton)."""

    __tablename__ = "product_attribute_values"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    attribute_id = Column(UUID(as_uuid=True), ForeignKey("product_attributes.id"), nullable=False)

    # Value information
    value = Column(String(255), nullable=False)

    # Relationships
    product = relationship("Product", back_populates="attribute_values")
    attribute = relationship("ProductAttribute", back_populates="values")
    variant_attributes = relationship("ProductVariantAttribute", back_populates="attribute_value")

    def __repr__(self):
        return f"<ProductAttributeValue(id={self.id}, attribute={self.attribute.name if self.attribute else None}, value={self.value})>"
