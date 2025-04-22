from sqlalchemy import (
    Boolean,
    Column,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Brand(BaseModel):
    """Brand model for organizing products by manufacturer/brand."""

    __tablename__ = "brands"

    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Brand details
    logo_url = Column(String(512), nullable=True)
    website = Column(String(512), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)

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
