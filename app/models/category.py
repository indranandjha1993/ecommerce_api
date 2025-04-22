from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Category(BaseModel):
    """Category model for product categorization."""

    __tablename__ = "categories"

    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Hierarchical structure
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True)
    image_url = Column(String(255), nullable=True)
    display_order = Column(Integer, default=0)

    # Relationships
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"
