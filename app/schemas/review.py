import datetime
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.user import User


# Review schemas
class ReviewBase(BaseModel):
    """Base review schema with common properties."""
    product_id: uuid.UUID
    title: Optional[str] = None
    content: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    media: Optional[Dict[str, Any]] = None


class ReviewCreate(ReviewBase):
    """Schema for review creation."""
    pass


class ReviewUpdate(BaseModel):
    """Schema for review update."""
    title: Optional[str] = None
    content: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    media: Optional[Dict[str, Any]] = None


class ReviewReplyBase(BaseModel):
    """Base review reply schema with common properties."""
    content: str
    moderation_status: Optional[str] = "pending"
    is_approved: Optional[bool] = False


class ReviewReplyCreate(ReviewReplyBase):
    """Schema for review reply creation."""
    pass


class ReviewReplyUpdate(BaseModel):
    """Schema for review reply update."""
    content: Optional[str] = None
    moderation_status: Optional[str] = None
    is_approved: Optional[bool] = None


class ReviewReplyInDBBase(ReviewReplyBase):
    """Base schema for review replies in DB."""
    id: uuid.UUID
    review_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_edited: bool
    edited_at: Optional[datetime.datetime] = None
    moderation_status: str
    is_approved: bool
    moderation_notes: Optional[str] = None
    moderated_by: Optional[uuid.UUID] = None
    moderated_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True


class ReviewReply(ReviewReplyInDBBase):
    """Schema for review reply response."""
    user: Optional[User] = None


class ReviewInDBBase(ReviewBase):
    """Base schema for reviews in DB."""
    id: uuid.UUID
    user_id: uuid.UUID
    order_item_id: Optional[uuid.UUID] = None
    is_verified_purchase: bool
    is_approved: bool
    is_featured: bool
    helpful_votes: int
    not_helpful_votes: int
    moderation_status: str
    moderation_notes: Optional[str] = None
    moderated_by: Optional[uuid.UUID] = None
    moderated_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_edited: bool
    edited_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True


class Review(ReviewInDBBase):
    """Schema for review response."""
    user: Optional[User] = None
    replies: List[ReviewReply] = []
    helpful_percentage: Optional[float] = None


class ReviewList(BaseModel):
    """Schema for review list response."""
    items: List[Review]
    total: int
    page: int
    size: int
    pages: int


class ReviewModerationUpdate(BaseModel):
    """Schema for review moderation update."""
    status: str = Field(..., description="Moderation status: approved or rejected")
    notes: Optional[str] = None
