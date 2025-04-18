import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Category(Base):
    """Category model for product categorization."""

    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Hierarchical structure
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True)
    image_url = Column(String(255), nullable=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"

    @property
    def is_leaf(self):
        """Check if the category is a leaf category (has no children)."""
        return len(self.children) == 0

    @property
    def ancestry(self):
        """Get the category's ancestors in order from root to parent."""
        if not self.parent:
            return []

        ancestors = []
        current = self.parent
        while current:
            ancestors.insert(0, current)
            current = current.parent

        return ancestors

    @property
    def full_path(self):
        """Get the category's full path from root to self as a string."""
        ancestors = self.ancestry
        path = [ancestor.name for ancestor in ancestors]
        path.append(self.name)
        return " > ".join(path)
