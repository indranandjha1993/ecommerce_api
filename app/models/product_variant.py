import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class ProductVariant(Base):
    """ProductVariant model for handling product variations."""

    __tablename__ = "product_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)

    # Variant information
    name = Column(String(255), nullable=True)
    sku = Column(String(100), nullable=True, unique=True)
    barcode = Column(String(100), nullable=True, unique=True)

    # Pricing information
    price = Column(Numeric(precision=10, scale=2), nullable=True)
    compare_price = Column(Numeric(precision=10, scale=2), nullable=True)
    cost_price = Column(Numeric(precision=10, scale=2), nullable=True)

    # Stock information
    weight = Column(Float, nullable=True)
    weight_unit = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True)

    # Additional data
    additional_data = Column(JSONB, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="variants")
    variant_attributes = relationship("ProductVariantAttribute", back_populates="variant", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="variant", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="variant", uselist=False, cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="variant")
    order_items = relationship("OrderItem", back_populates="variant")

    def __repr__(self):
        return f"<ProductVariant(id={self.id}, product_id={self.product_id}, sku={self.sku})>"

    @property
    def is_in_stock(self):
        """Check if the variant is in stock."""
        return self.inventory and self.inventory.quantity > 0

    @property
    def effective_price(self):
        """Get the effective price for this variant."""
        if self.price is not None:
            return self.price
        return self.product.price

    @property
    def attributes_display(self):
        """Get a display string for the variant's attributes."""
        if not self.variant_attributes:
            return ""

        attributes = []
        for attr in self.variant_attributes:
            attributes.append(f"{attr.attribute.name}: {attr.attribute_value.value}")

        return ", ".join(attributes)


class ProductVariantAttribute(Base):
    """Links a ProductVariant to its specific attribute values."""

    __tablename__ = "product_variant_attributes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=False)
    attribute_id = Column(UUID(as_uuid=True), ForeignKey("product_attributes.id"), nullable=False)
    attribute_value_id = Column(UUID(as_uuid=True), ForeignKey("product_attribute_values.id"), nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    variant = relationship("ProductVariant", back_populates="variant_attributes")
    attribute = relationship("ProductAttribute", back_populates="variant_attributes")
    attribute_value = relationship("ProductAttributeValue", back_populates="variant_attributes")

    def __repr__(self):
        return f"<ProductVariantAttribute(variant_id={self.variant_id}, attribute={self.attribute.name}, value={self.attribute_value.value})>"
