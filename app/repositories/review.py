import uuid
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from app.models.review import Review, ReviewReply
from app.repositories.base import BaseRepository
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewReplyCreate, ReviewReplyUpdate
from app.utils.datetime_utils import utcnow


class ReviewRepository(BaseRepository[Review, ReviewCreate, ReviewUpdate]):
    """
    Review repository for data access operations.
    """

    def get_with_relations(self, db: Session, id: uuid.UUID) -> Optional[Review]:
        """
        Get a review by ID with related entities.
        """
        return (
            db.query(Review)
            .filter(Review.id == id)
            .options(
                joinedload(Review.user),
                joinedload(Review.product),
                joinedload(Review.replies).joinedload(ReviewReply.user)
            )
            .first()
        )

    def get_by_product_id(
            self, db: Session, product_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Review], int]:
        """
        Get reviews for a product with pagination.
        """
        query = (
            db.query(Review)
            .filter(Review.product_id == product_id, Review.is_approved == True)
            .options(
                joinedload(Review.user),
                joinedload(Review.replies).joinedload(ReviewReply.user)
            )
            .order_by(Review.created_at.desc())
        )

        total = query.count()
        reviews = query.offset(skip).limit(limit).all()

        return reviews, total

    def get_by_user_id(
            self, db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Review], int]:
        """
        Get reviews by a user with pagination.
        """
        query = (
            db.query(Review)
            .filter(Review.user_id == user_id)
            .options(
                joinedload(Review.product),
                joinedload(Review.replies).joinedload(ReviewReply.user)
            )
            .order_by(Review.created_at.desc())
        )

        total = query.count()
        reviews = query.offset(skip).limit(limit).all()

        return reviews, total

    def get_pending_reviews(
            self, db: Session, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Review], int]:
        """
        Get pending reviews for moderation with pagination.
        """
        query = (
            db.query(Review)
            .filter(Review.moderation_status == "pending")
            .options(
                joinedload(Review.user),
                joinedload(Review.product)
            )
            .order_by(Review.created_at.asc())
        )

        total = query.count()
        reviews = query.offset(skip).limit(limit).all()

        return reviews, total

    def add_reply(
            self, db: Session, review_id: uuid.UUID, user_id: uuid.UUID, reply_in: ReviewReplyCreate
    ) -> ReviewReply:
        """
        Add a reply to a review.
        """
        db_reply = ReviewReply(
            review_id=review_id,
            user_id=user_id,
            content=reply_in.content,
            moderation_status="pending" if reply_in.moderation_status is None else reply_in.moderation_status,
            is_approved=False if reply_in.is_approved is None else reply_in.is_approved
        )
        db.add(db_reply)
        db.commit()
        db.refresh(db_reply)
        return db_reply

    def get_reply(
            self, db: Session, reply_id: uuid.UUID
    ) -> Optional[ReviewReply]:
        """
        Get a reply by ID.
        """
        return (
            db.query(ReviewReply)
            .filter(ReviewReply.id == reply_id)
            .options(
                joinedload(ReviewReply.user),
                joinedload(ReviewReply.review)
            )
            .first()
        )

    def update_reply(
            self, db: Session, db_reply: ReviewReply, reply_in: ReviewReplyUpdate
    ) -> ReviewReply:
        """
        Update a reply.
        """
        update_data = reply_in.model_dump(exclude_unset=True)

        # Mark as edited if content is changed
        if "content" in update_data and update_data["content"] != db_reply.content:
            from datetime import datetime
            update_data["is_edited"] = True
            update_data["edited_at"] = utcnow()

        for field in update_data:
            setattr(db_reply, field, update_data[field])

        db.add(db_reply)
        db.commit()
        db.refresh(db_reply)
        return db_reply

    def remove_reply(
            self, db: Session, reply_id: uuid.UUID
    ) -> bool:
        """
        Remove a reply.
        """
        reply = db.query(ReviewReply).filter(ReviewReply.id == reply_id).first()
        if not reply:
            return False

        db.delete(reply)
        db.commit()
        return True

    def update_moderation_status(
            self, db: Session, review_id: uuid.UUID, moderator_id: uuid.UUID,
            moderation_status: str, moderation_notes: Optional[str] = None
    ) -> Review:
        """
        Update the moderation status of a review.
        """
        review = self.get(db, id=review_id)
        if not review:
            raise ValueError("Review not found")

        from datetime import datetime

        review.moderation_status = moderation_status
        review.moderation_notes = moderation_notes
        review.moderated_by = moderator_id
        review.moderated_at = utcnow()

        # If approved, update is_approved flag
        if moderation_status == "approved":
            review.is_approved = True
        elif moderation_status == "rejected":
            review.is_approved = False

        db.add(review)
        db.commit()
        db.refresh(review)
        return review


review_repository = ReviewRepository(Review)
