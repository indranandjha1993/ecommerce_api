from typing import Any

from fastapi import APIRouter, Depends, Path, Body, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_active_user,
    get_current_active_superuser,
)
from app.api.dependencies.pagination import PaginationParams, get_pagination
from app.db.session import get_db
from app.models.user import User
from app.schemas.review import (
    Review,
    ReviewCreate,
    ReviewUpdate,
    ReviewList,
    ReviewReply,
    ReviewReplyCreate,
    ReviewReplyUpdate,
    ReviewModerationUpdate,
)
from app.services.review import review_service

router = APIRouter()


@router.get("/product/{product_id}", response_model=ReviewList)
def read_product_reviews(
        *,
        db: Session = Depends(get_db),
        product_id: str = Path(..., description="The product ID"),
        pagination: PaginationParams = Depends(get_pagination),
) -> Any:
    """
    Get reviews for a specific product.
    """
    reviews, total = review_service.get_by_product_id(
        db, product_id=product_id, page=pagination.page, size=pagination.size
    )

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": reviews,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }


@router.get("/me", response_model=ReviewList)
def read_user_reviews(
        *,
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get reviews by the current user.
    """
    reviews, total = review_service.get_by_user_id(
        db, user_id=current_user.id, page=pagination.page, size=pagination.size
    )

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": reviews,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }


@router.post("", response_model=Review, status_code=status.HTTP_201_CREATED)
def create_review(
        *,
        db: Session = Depends(get_db),
        review_in: ReviewCreate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new review.
    """
    return review_service.create(db, user_id=current_user.id, review_in=review_in)


@router.get("/{review_id}", response_model=Review)
def read_review(
        *,
        db: Session = Depends(get_db),
        review_id: str = Path(..., description="The review ID"),
) -> Any:
    """
    Get a specific review by ID.
    """
    return review_service.get_by_id(db, review_id=review_id)


@router.put("/{review_id}", response_model=Review)
def update_review(
        *,
        db: Session = Depends(get_db),
        review_id: str = Path(..., description="The review ID"),
        review_in: ReviewUpdate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a review.
    """
    return review_service.update(
        db, review_id=review_id, user_id=current_user.id, review_in=review_in
    )


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
        *,
        db: Session = Depends(get_db),
        review_id: str = Path(..., description="The review ID"),
        current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a review.
    """
    review_service.delete(
        db, review_id=review_id, user_id=current_user.id, is_admin=current_user.is_superuser
    )


@router.post("/{review_id}/replies", response_model=ReviewReply, status_code=status.HTTP_201_CREATED)
def create_review_reply(
        *,
        db: Session = Depends(get_db),
        review_id: str = Path(..., description="The review ID"),
        reply_in: ReviewReplyCreate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Add a reply to a review.
    """
    return review_service.add_reply(
        db, review_id=review_id, user_id=current_user.id, reply_in=reply_in
    )


@router.put("/replies/{reply_id}", response_model=ReviewReply)
def update_review_reply(
        *,
        db: Session = Depends(get_db),
        reply_id: str = Path(..., description="The reply ID"),
        reply_in: ReviewReplyUpdate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a review reply.
    """
    return review_service.update_reply(
        db, reply_id=reply_id, user_id=current_user.id,
        reply_in=reply_in, is_admin=current_user.is_superuser
    )


@router.delete("/replies/{reply_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review_reply(
        *,
        db: Session = Depends(get_db),
        reply_id: str = Path(..., description="The reply ID"),
        current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a review reply.
    """
    review_service.delete_reply(
        db, reply_id=reply_id, user_id=current_user.id, is_admin=current_user.is_superuser
    )


@router.post("/{review_id}/helpful")
def vote_review_helpful(
        *,
        db: Session = Depends(get_db),
        review_id: str = Path(..., description="The review ID"),
) -> Any:
    """
    Vote a review as helpful.
    """
    review_service.vote_helpful(db, review_id=review_id)
    return {"message": "Thank you for your feedback"}


@router.post("/{review_id}/not-helpful")
def vote_review_not_helpful(
        *,
        db: Session = Depends(get_db),
        review_id: str = Path(..., description="The review ID"),
) -> Any:
    """
    Vote a review as not helpful.
    """
    review_service.vote_not_helpful(db, review_id=review_id)
    return {"message": "Thank you for your feedback"}


# Admin endpoints
@router.get("/admin/pending", response_model=ReviewList)
def read_pending_reviews(
        *,
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get pending reviews for moderation. Only for superusers.
    """
    reviews, total = review_service.get_pending_reviews(
        db, page=pagination.page, size=pagination.size
    )

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": reviews,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }


@router.post("/admin/{review_id}/moderate", response_model=Review)
def moderate_review(
        *,
        db: Session = Depends(get_db),
        review_id: str = Path(..., description="The review ID"),
        moderation: ReviewModerationUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Moderate a review. Only for superusers.
    """
    return review_service.moderate_review(
        db, review_id=review_id, moderator_id=current_user.id,
        status=moderation.status, notes=moderation.notes
    )


@router.post("/admin/{review_id}/feature", response_model=Review)
def feature_review(
        *,
        db: Session = Depends(get_db),
        review_id: str = Path(..., description="The review ID"),
        featured: bool = Body(..., embed=True),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Feature or unfeature a review. Only for superusers.
    """
    review = review_service.get_by_id(db, review_id=review_id)
    review.is_featured = featured
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
