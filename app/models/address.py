import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base
from app.utils.datetime_utils import utcnow


class AddressType(str, enum.Enum):
    """Enum for address types."""
    SHIPPING = "shipping"
    BILLING = "billing"
    BOTH = "both"


class Address(Base):
    """Address model for user shipping and billing addresses."""

    __tablename__ = "addresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    address_type = Column(Enum(AddressType), default=AddressType.BOTH)
    is_default = Column(Boolean, default=False)

    # Address fields
    first_name = Column(String(100))
    last_name = Column(String(100))
    company = Column(String(100), nullable=True)
    street_address_1 = Column(String(255), nullable=False)
    street_address_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state_province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships are set dynamically in the configure_relationships function

    def __repr__(self):
        return f"<Address(id={self.id}, user_id={self.user_id}, type={self.address_type})>"

    @property
    def full_name(self):
        """Return the full name associated with this address."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return None

    @property
    def formatted_address(self):
        """Return a formatted address string."""
        parts = [
            self.street_address_1,
            self.street_address_2,
            f"{self.city}, {self.state_province if self.state_province else ''} {self.postal_code}",
            self.country
        ]
        return "\n".join(part for part in parts if part)
