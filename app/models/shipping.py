import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class ShippingStatus(str, enum.Enum):
    """Enum for shipping status."""
    PENDING = "pending"
    PROCESSING = "processing"
    READY_FOR_PICKUP = "ready_for_pickup"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    RETURNED = "returned"
    FAILED = "failed"


class ShippingCarrier(str, enum.Enum):
    """Enum for shipping carriers."""
    USPS = "usps"
    UPS = "ups"
    FEDEX = "fedex"
    DHL = "dhl"
    CUSTOM = "custom"


class Shipping(Base):
    """Shipping model for handling order shipments."""

    __tablename__ = "shipping"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)

    # Shipping information
    carrier = Column(Enum(ShippingCarrier), nullable=True)
    carrier_name = Column(String(100), nullable=True)  # For custom carriers
    tracking_number = Column(String(100), nullable=True)
    tracking_url = Column(String(512), nullable=True)
    status = Column(Enum(ShippingStatus), default=ShippingStatus.PENDING)

    # Package information
    package_weight = Column(Numeric(precision=10, scale=2), nullable=True)
    package_weight_unit = Column(String(10), nullable=True, default="kg")
    package_dimensions = Column(String(100), nullable=True)  # Format: "LxWxH"
    package_dimensions_unit = Column(String(10), nullable=True, default="cm")

    # Timing information
    estimated_delivery = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    # Shipping method details
    shipping_method = Column(String(100), nullable=True)
    shipping_rate = Column(Numeric(precision=10, scale=2), nullable=True)

    # Additional data
    shipping_metadata = Column(JSONB, nullable=True)
    notes = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="shipping_details")
    packages = relationship("ShipmentPackage", back_populates="shipment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Shipping(id={self.id}, order_id={self.order_id}, tracking={self.tracking_number}, status={self.status})>"

    @property
    def tracking_link(self):
        """Generate a tracking link for the shipment."""
        if not self.tracking_number:
            return None

        if self.tracking_url:
            return self.tracking_url

        # Generate tracking URLs for common carriers
        if self.carrier == ShippingCarrier.USPS:
            return f"https://tools.usps.com/go/TrackConfirmAction?tLabels={self.tracking_number}"
        elif self.carrier == ShippingCarrier.UPS:
            return f"https://www.ups.com/track?tracknum={self.tracking_number}"
        elif self.carrier == ShippingCarrier.FEDEX:
            return f"https://www.fedex.com/apps/fedextrack/?tracknumbers={self.tracking_number}"
        elif self.carrier == ShippingCarrier.DHL:
            return f"https://www.dhl.com/us-en/home/tracking/tracking-express.html?submit=1&tracking-id={self.tracking_number}"

        return None


class ShipmentPackage(Base):
    """ShipmentPackage model for individual packages in a shipment."""

    __tablename__ = "shipment_packages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipping.id"), nullable=False)

    # Package information
    package_number = Column(Integer, nullable=False)  # For multi-package shipments
    tracking_number = Column(String(100), nullable=True)

    # Package details
    weight = Column(Numeric(precision=10, scale=2), nullable=True)
    weight_unit = Column(String(10), nullable=True, default="kg")
    dimensions = Column(String(100), nullable=True)  # Format: "LxWxH"
    dimensions_unit = Column(String(10), nullable=True, default="cm")

    # Status
    status = Column(Enum(ShippingStatus), default=ShippingStatus.PENDING)

    # Additional data
    package_metadata = Column(JSONB, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    shipment = relationship("Shipping", back_populates="packages")
    items = relationship("ShipmentItem", back_populates="package", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ShipmentPackage(id={self.id}, shipment_id={self.shipment_id}, package_number={self.package_number})>"


class ShipmentItem(Base):
    """ShipmentItem model for items in a package."""

    __tablename__ = "shipment_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id = Column(UUID(as_uuid=True), ForeignKey("shipment_packages.id"), nullable=False)
    order_item_id = Column(UUID(as_uuid=True), ForeignKey("order_items.id"), nullable=False)

    # Item information
    quantity = Column(Integer, nullable=False)

    # Additional data
    shipment_item_metadata = Column(JSONB, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    package = relationship("ShipmentPackage", back_populates="items")
    order_item = relationship("OrderItem")

    def __repr__(self):
        return f"<ShipmentItem(id={self.id}, package_id={self.package_id}, order_item_id={self.order_item_id}, quantity={self.quantity})>"
