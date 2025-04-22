from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.utils.datetime_utils import utcnow


class Review(BaseModel):
    """Review model for product reviews and ratings."""

    __tablename__ = "reviews"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    order_item_id = Column(UUID(as_uuid=True), ForeignKey("order_items.id"), nullable=True)

    # Review content
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    rating = Column(Integer, nullable=False)  # 1-5 star rating

    # Media
    media = Column(JSONB, nullable=True)  # URLs to images, videos

    # Status
    is_verified_purchase = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)

    # Helpful votes
    helpful_votes = Column(Integer, default=0)
    not_helpful_votes = Column(Integer, default=0)

    # Moderation
    moderation_status = Column(String(50), default="pending")  # pending, approved, rejected
    moderation_notes = Column(Text, nullable=True)
    moderated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    moderated_at = Column(DateTime, nullable=True)

    # If the review has been edited
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)

    # Relationships
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", foreign_keys=[user_id], back_populates="reviews")
    order_item = relationship("OrderItem")
    moderator = relationship("User", foreign_keys=[moderated_by])
    replies = relationship("ReviewReply", back_populates="review", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Review(id={self.id}, product_id={self.product_id}, user_id={self.user_id}, rating={self.rating})>"

    @property
    def helpful_percentage(self):
        """Calculate the percentage of helpful votes."""
        total_votes = self.helpful_votes + self.not_helpful_votes
        if total_votes == 0:
            return 0
        return (self.helpful_votes / total_votes) * 100

    @property
    def is_visible(self):
        """Check if the review is visible to customers."""
        return self.is_approved and self.moderation_status == "approved"


class ReviewReply(BaseModel):
    """ReviewReply model for replies to reviews."""

    __tablename__ = "review_replies"

    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Reply content
    content = Column(Text, nullable=False)

    # Status
    is_approved = Column(Boolean, default=False)

    # Moderation
    moderation_status = Column(String(50), default="pending")  # pending, approved, rejected
    moderation_notes = Column(Text, nullable=True)
    moderated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    moderated_at = Column(DateTime, nullable=True)

    # If the reply has been edited
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)

    # Relationships
    review = relationship("Review", back_populates="replies")
    user = relationship("User", foreign_keys=[user_id])
    moderator = relationship("User", foreign_keys=[moderated_by])

    def __repr__(self):
        return f"<ReviewReply(id={self.id}, review_id={self.review_id}, user_id={self.user_id})>"
