"""
Cart model for managing shopping carts.
"""
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.utils.datetime_utils import utcnow


class Cart(BaseModel):
    """Cart model for managing shopping carts."""

    __tablename__ = "carts"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Can be null for guest carts

    # Guest carts use a unique token
    session_id = Column(String(255), nullable=True, unique=True, index=True)

    # Additional data (e.g., coupon codes, notes)
    cart_metadata = Column(JSONB, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Activity tracking
    last_activity = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id}, items={len(self.items)})>"

    @property
    def is_empty(self):
        """Check if the cart is empty."""
        return len(self.items) == 0

    @property
    def item_count(self):
        """Get the total number of items in the cart."""
        return sum(item.quantity for item in self.items)

    @property
    def subtotal(self):
        """Calculate the subtotal of all items in the cart."""
        return sum(item.subtotal for item in self.items)


class CartItem(BaseModel):
    """Cart item model for items in a shopping cart."""

    __tablename__ = "cart_items"

    cart_id = Column(UUID(as_uuid=True), ForeignKey("carts.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=True)

    # Quantity and pricing
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(precision=10, scale=2), nullable=True)  # Stored price at time of adding

    # Additional data (e.g., customizations, gift wrapping)
    item_metadata = Column(JSONB, nullable=True)

    # Activity tracking
    added_at = Column(DateTime, default=utcnow)

    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant", back_populates="cart_items")

    def __repr__(self):
        return f"<CartItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"

    @property
    def subtotal(self):
        """Calculate the subtotal for this item."""
        if self.unit_price is not None:
            return self.unit_price * self.quantity

        if self.variant and self.variant.price is not None:
            return self.variant.price * self.quantity

        return self.product.price * self.quantity
