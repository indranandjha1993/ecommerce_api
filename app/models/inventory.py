import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.utils.datetime_utils import utcnow


class StockStatus(str, enum.Enum):
    """Enum for inventory stock status."""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    BACKORDER = "backorder"
    DISCONTINUED = "discontinued"


class Inventory(Base):
    """Inventory model for tracking product stock levels."""

    __tablename__ = "inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=True)

    # Stock information
    quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)
    reorder_point = Column(Integer, nullable=True)
    reorder_quantity = Column(Integer, nullable=True)

    # Location information
    location_id = Column(UUID(as_uuid=True), ForeignKey("inventory_locations.id"), nullable=True)
    bin_location = Column(String(50), nullable=True)

    # Status
    status = Column(Enum(StockStatus), default=StockStatus.IN_STOCK)

    # Metadata
    last_checked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    product = relationship("Product", back_populates="inventory")
    variant = relationship("ProductVariant", back_populates="inventory")
    location = relationship("InventoryLocation", back_populates="inventory_items")
    stock_movements = relationship("StockMovement", back_populates="inventory")

    def __repr__(self):
        return f"<Inventory(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"

    @property
    def available_quantity(self):
        """Get the quantity available for purchase."""
        return max(0, self.quantity - self.reserved_quantity)


class InventoryLocation(Base):
    """Inventory location model for warehouses, stores, etc."""

    __tablename__ = "inventory_locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # Address information
    street_address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state_province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    inventory_items = relationship("Inventory", back_populates="location")

    def __repr__(self):
        return f"<InventoryLocation(id={self.id}, name={self.name})>"


class StockMovementType(str, enum.Enum):
    """Enum for stock movement types."""
    RECEIPT = "receipt"  # Incoming stock
    SALE = "sale"  # Sold to customer
    ADJUSTMENT = "adjustment"  # Manual adjustment
    RETURN = "return"  # Customer return
    TRANSFER = "transfer"  # Transfer between locations
    DAMAGED = "damaged"  # Damaged stock
    RESERVED = "reserved"  # Reserved for order
    RELEASED = "released"  # Released from reservation


class StockMovement(Base):
    """Stock movement model for tracking inventory changes."""

    __tablename__ = "stock_movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_id = Column(UUID(as_uuid=True), ForeignKey("inventory.id"), nullable=False)

    # Movement details
    quantity = Column(Integer, nullable=False)
    movement_type = Column(Enum(StockMovementType), nullable=False)

    # Reference information
    reference_id = Column(UUID(as_uuid=True), nullable=True)  # May point to an order, etc.
    reference_type = Column(String(50), nullable=True)  # Type of reference (order, adjustment, etc.)

    # Notes
    notes = Column(Text, nullable=True)

    # User who made the change
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    inventory = relationship("Inventory", back_populates="stock_movements")
    user = relationship("User")

    def __repr__(self):
        return f"<StockMovement(id={self.id}, inventory_id={self.inventory_id}, quantity={self.quantity}, type={self.movement_type})>"
