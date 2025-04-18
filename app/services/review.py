import uuid
from typing import List, Optional, Tuple

from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewReplyCreate, ReviewReplyUpdate
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    ForbiddenException,
)
from app.models.review import Review, ReviewReply
from app.repositories.review import review_repository


class ReviewService:
    """
    Review service for business logic.
    """

    def get_by_id(self, db: Session, review_id: uuid.UUID) -> Review:
        """
        Get a review by ID.
        """
        review = review_repository.get_with_relations(db, id=review_id)
        if not review:
            raise NotFoundException(detail="Review not found")
        return review

    def get_by_product_id(
            self, db: Session, product_id: uuid.UUID, page: int = 1, size: int = 20
    ) -> Tuple[List[Review], int]:
        """
        Get reviews for a product with pagination.
        """
        skip = (page - 1) * size
        return review_repository.get_by_product_id(db, product_id=product_id, skip=skip, limit=size)

    def get_by_user_id(
            self, db: Session, user_id: uuid.UUID, page: int = 1, size: int = 20
    ) -> Tuple[List[Review], int]:
        """
        Get reviews by a user with pagination.
        """
        skip = (page - 1) * size
        return review_repository.get_by_user_id(db, user_id=user_id, skip=skip, limit=size)

    def get_pending_reviews(
            self, db: Session, page: int = 1, size: int = 20
    ) -> Tuple[List[Review], int]:
        """
        Get pending reviews for moderation with pagination.
        """
        skip = (page - 1) * size
        return review_repository.get_pending_reviews(db, skip=skip, limit=size)

    def create(
            self, db: Session, user_id: uuid.UUID, review_in: ReviewCreate
    ) -> Review:
        """
        Create a new review.
        """
        # Check if product exists
        from app.models.product import Product
        product = db.query(Product).filter(Product.id == review_in.product_id).first()
        if not product:
            raise NotFoundException(detail="Product not found")

        # Check if user has already reviewed this product
        existing_review = db.query(Review).filter(
            Review.product_id == review_in.product_id,
            Review.user_id == user_id
        ).first()

        if existing_review:
            raise BadRequestException(detail="You have already reviewed this product")

        # Check if user has purchased this product (for verified purchase badge)
        from app.models.order import Order, OrderItem, OrderStatus

        # Look for completed orders containing this product
        verified_purchase = db.query(Order).join(OrderItem).filter(
            Order.user_id == user_id,
            Order.status == OrderStatus.COMPLETED,
            OrderItem.product_id == review_in.product_id
        ).first() is not None

        # Create review
        review_data = review_in.dict()
        review_data["user_id"] = user_id
        review_data["is_verified_purchase"] = verified_purchase
        review_data["moderation_status"] = "pending"  # All reviews need moderation
        review_data["is_approved"] = False  # Starts unapproved until moderated

        return review_repository.create(db, obj_in=review_data)

    def update(
            self, db: Session, review_id: uuid.UUID, user_id: uuid.UUID, review_in: ReviewUpdate
    ) -> Review:
        """
        Update a review.
        """
        review = review_repository.get(db, id=review_id)
        if not review:
            raise NotFoundException(detail="Review not found")

        # Only the author can update their review
        if str(review.user_id) != str(user_id):
            raise ForbiddenException(detail="You can only update your own reviews")

        # Reset moderation status if content is updated
        update_data = review_in.dict(exclude_unset=True)
        if "content" in update_data or "rating" in update_data or "title" in update_data:
            update_data["moderation_status"] = "pending"
            update_data["is_approved"] = False
            update_data["is_edited"] = True

            from datetime import datetime
            update_data["edited_at"] = datetime.utcnow()

        return review_repository.update(db, db_obj=review, obj_in=update_data)

    def delete(
            self, db: Session, review_id: uuid.UUID, user_id: uuid.UUID, is_admin: bool = False
    ) -> None:
        """
        Delete a review.
        """
        review = review_repository.get(db, id=review_id)
        if not review:
            raise NotFoundException(detail="Review not found")

        # Only the author or an admin can delete a review
        if not is_admin and str(review.user_id) != str(user_id):
            raise ForbiddenException(detail="You can only delete your own reviews")

        review_repository.remove(db, id=review_id)

    def add_reply(
            self, db: Session, review_id: uuid.UUID, user_id: uuid.UUID, reply_in: ReviewReplyCreate
    ) -> ReviewReply:
        """
        Add a reply to a review.
        """
        review = review_repository.get(db, id=review_id)
        if not review:
            raise NotFoundException(detail="Review not found")

        # Users can only reply to approved reviews
        if not review.is_approved and str(review.user_id) != str(user_id):
            raise BadRequestException(detail="You cannot reply to an unapproved review")

        return review_repository.add_reply(db, review_id=review_id, user_id=user_id, reply_in=reply_in)

    def update_reply(
            self, db: Session, reply_id: uuid.UUID, user_id: uuid.UUID, reply_in: ReviewReplyUpdate,
            is_admin: bool = False
    ) -> ReviewReply:
        """
        Update a reply.
        """
        reply = review_repository.get_reply(db, reply_id=reply_id)
        if not reply:
            raise NotFoundException(detail="Reply not found")

        # Only the author or an admin can update a reply
        if not is_admin and str(reply.user_id) != str(user_id):
            raise ForbiddenException(detail="You can only update your own replies")

        return review_repository.update_reply(db, db_reply=reply, reply_in=reply_in)

    def delete_reply(
            self, db: Session, reply_id: uuid.UUID, user_id: uuid.UUID, is_admin: bool = False
    ) -> None:
        """
        Delete a reply.
        """
        reply = review_repository.get_reply(db, reply_id=reply_id)
        if not reply:
            raise NotFoundException(detail="Reply not found")

        # Only the author or an admin can delete a reply
        if not is_admin and str(reply.user_id) != str(user_id):
            raise ForbiddenException(detail="You can only delete your own replies")

        review_repository.remove_reply(db, reply_id=reply_id)

    def moderate_review(
            self, db: Session, review_id: uuid.UUID, moderator_id: uuid.UUID,
            status: str, notes: Optional[str] = None
    ) -> Review:
        """
        Moderate a review.
        """
        # Validate status
        valid_statuses = ["approved", "rejected"]
        if status not in valid_statuses:
            raise BadRequestException(detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        review = review_repository.get(db, id=review_id)
        if not review:
            raise NotFoundException(detail="Review not found")

        return review_repository.update_moderation_status(
            db, review_id=review_id, moderator_id=moderator_id,
            moderation_status=status, moderation_notes=notes
        )

    def vote_helpful(
            self, db: Session, review_id: uuid.UUID
    ) -> Review:
        """
        Vote a review as helpful.
        """
        review = review_repository.get(db, id=review_id)
        if not review:
            raise NotFoundException(detail="Review not found")

        review.helpful_votes += 1
        db.add(review)
        db.commit()
        db.refresh(review)

        return review

    def vote_not_helpful(
            self, db: Session, review_id: uuid.UUID
    ) -> Review:
        """
        Vote a review as not helpful.
        """
        review = review_repository.get(db, id=review_id)
        if not review:
            raise NotFoundException(detail="Review not found")

        review.not_helpful_votes += 1
        db.add(review)
        db.commit()
        db.refresh(review)

        return review


review_service = ReviewService()
