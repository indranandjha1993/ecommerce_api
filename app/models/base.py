import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base
from app.utils.datetime_utils import utcnow


class BaseModel(Base):
    """
    Base model class that includes common fields and functionality for all models.
    All models should inherit from this class instead of directly from Base.
    """
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    def __repr__(self):
        """Default string representation for all models."""
        return f"<{self.__class__.__name__}(id={self.id})>"