import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.utils.datetime_utils import utcnow


class DiscountType(str, enum.Enum):
    """Enum for discount types."""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_SHIPPING = "free_shipping"
    BUY_X_GET_Y = "buy_x_get_y"


class Coupon(Base):
    """Coupon model for discounts and promotions."""

    __tablename__ = "coupons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Coupon identification
    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # Discount information
    discount_type = Column(Enum(DiscountType), nullable=False)
    discount_value = Column(Numeric(precision=10, scale=2), nullable=False)  # Percentage or fixed amount

    # For buy X get Y promotions
    buy_quantity = Column(Integer, nullable=True)
    get_quantity = Column(Integer, nullable=True)

    # Usage limits
    usage_limit = Column(Integer, nullable=True)  # Total number of times this coupon can be used
    usage_limit_per_user = Column(Integer, nullable=True)  # Number of times each user can use this coupon
    current_usage_count = Column(Integer, default=0)  # Current total usage count

    # Minimum requirements
    minimum_order_amount = Column(Numeric(precision=10, scale=2), nullable=True)
    minimum_quantity = Column(Integer, nullable=True)

    # Validity
    is_active = Column(Boolean, default=True)
    starts_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Restrictions
    is_first_order_only = Column(Boolean, default=False)
    is_one_time_use = Column(Boolean, default=False)

    # Product scope
    applies_to_all_products = Column(Boolean, default=True)
    product_ids = Column(ARRAY(UUID), nullable=True)  # List of product IDs this coupon applies to
    category_ids = Column(ARRAY(UUID), nullable=True)  # List of category IDs this coupon applies to
    exclude_product_ids = Column(ARRAY(UUID), nullable=True)  # List of product IDs excluded from this coupon
    exclude_category_ids = Column(ARRAY(UUID), nullable=True)  # List of category IDs excluded from this coupon

    # Customer scope
    applies_to_all_customers = Column(Boolean, default=True)
    customer_ids = Column(ARRAY(UUID), nullable=True)  # List of customer IDs this coupon applies to

    # Additional data
    coupon_metadata = Column(JSONB, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    usage_history = relationship("CouponUsage", back_populates="coupon", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Coupon(id={self.id}, code={self.code}, type={self.discount_type}, value={self.discount_value})>"

    def _normalize_datetime(self, dt):
        """Normalize datetime for comparison by removing timezone info."""
        if dt is None:
            return None
        if dt.tzinfo:
            return dt.replace(tzinfo=None)
        return dt

    @property
    def is_expired(self):
        """Check if the coupon is expired."""
        if not self.expires_at:
            return False
        now = self._normalize_datetime(utcnow())
        expires_at = self._normalize_datetime(self.expires_at)
        return expires_at < now

    @property
    def is_started(self):
        """Check if the coupon has started."""
        if not self.starts_at:
            return True
        now = self._normalize_datetime(utcnow())
        starts_at = self._normalize_datetime(self.starts_at)
        return starts_at <= now

    @property
    def is_valid(self):
        """Check if the coupon is currently valid."""
        return self.is_active and self.is_started and not self.is_expired

    @property
    def is_usage_limit_reached(self):
        """Check if the coupon usage limit has been reached."""
        if not self.usage_limit:
            return False
        return self.current_usage_count >= self.usage_limit


class CouponUsage(Base):
    """CouponUsage model for tracking coupon usage."""

    __tablename__ = "coupon_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coupon_id = Column(UUID(as_uuid=True), ForeignKey("coupons.id"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Usage details
    discount_amount = Column(Numeric(precision=10, scale=2), nullable=False)

    # Metadata
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    coupon = relationship("Coupon", back_populates="usage_history")
    order = relationship("Order")
    user = relationship("User")

    def __repr__(self):
        return f"<CouponUsage(id={self.id}, coupon_id={self.coupon_id}, order_id={self.order_id}, amount={self.discount_amount})>"
