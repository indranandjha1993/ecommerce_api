import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.utils.datetime_utils import utcnow


class Brand(Base):
    """Brand model for organizing products by manufacturer/brand."""

    __tablename__ = "brands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Brand details
    logo_url = Column(String(512), nullable=True)
    website = Column(String(512), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    products = relationship("Product", back_populates="brand")

    def __repr__(self):
        return f"<Brand(id={self.id}, name={self.name})>"

    # Store the product count as a private attribute
    _product_count = None

    @property
    def product_count(self):
        """Get the number of products associated with this brand."""
        if self._product_count is not None:
            return self._product_count
        return len(self.products)
    
    @product_count.setter
    def product_count(self, value):
        """Set the product count."""
        self._product_count = value
