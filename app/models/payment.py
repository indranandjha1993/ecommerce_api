import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.utils.datetime_utils import utcnow


class PaymentProvider(str, enum.Enum):
    """Enum for payment providers."""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"
    CREDIT_CARD = "credit_card"
    MANUAL = "manual"


class PaymentType(str, enum.Enum):
    """Enum for payment types."""
    PAYMENT = "payment"
    REFUND = "refund"
    PARTIAL_REFUND = "partial_refund"
    CAPTURE = "capture"
    AUTHORIZATION = "authorization"
    VOID = "void"


class Payment(Base):
    """Payment model for handling order payments."""

    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)

    # Payment information
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    provider = Column(Enum(PaymentProvider), nullable=False)
    payment_type = Column(Enum(PaymentType), default=PaymentType.PAYMENT)
    status = Column(String(50), nullable=False, default="pending")

    # Payment identification
    transaction_id = Column(String(255), nullable=True)  # Provider's transaction ID
    payment_method_id = Column(String(255), nullable=True)  # Stored payment method ID
    payment_intent_id = Column(String(255), nullable=True)  # For payment intent based systems (e.g., Stripe)

    # Customer-facing details
    last_four = Column(String(4), nullable=True)  # Last 4 digits of card
    card_type = Column(String(50), nullable=True)  # Visa, Mastercard, etc.
    expiry_month = Column(String(2), nullable=True)
    expiry_year = Column(String(4), nullable=True)
    cardholder_name = Column(String(255), nullable=True)

    # Security and verification
    is_3d_secure = Column(Boolean, default=False)
    risk_level = Column(String(50), nullable=True)

    # Error handling
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)

    # Additional data
    payment_metadata = Column(JSONB, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, amount={self.amount}, status={self.status})>"

    @property
    def is_successful(self):
        """Check if the payment was successful."""
        return self.status in ["completed", "succeeded", "paid", "captured"]

    @property
    def can_be_refunded(self):
        """Check if the payment can be refunded."""
        return self.is_successful and self.payment_type == PaymentType.PAYMENT

    @property
    def can_be_captured(self):
        """Check if the payment can be captured."""
        return self.status == "authorized" and self.payment_type == PaymentType.AUTHORIZATION
