from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Body, status, Response, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_active_user,
    get_current_active_superuser,
)
from app.api.dependencies.pagination import PaginationParams, get_pagination
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException
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
        response: Response,
        db: Session = Depends(get_db),
        product_id: UUID = Path(..., description="The product ID"),
        pagination: PaginationParams = Depends(get_pagination),
) -> Any:
    """
    Get reviews for a specific product.
    
    Returns a paginated list of approved reviews for the specified product.
    Reviews are sorted by helpfulness and recency.
    """
    # Set cache control headers - reviews change infrequently
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
        reviews, total = review_service.get_by_product_id(
            db, product_id=str(product_id), page=pagination.page, size=pagination.size
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
    except NotFoundException as e:
        # Keep the cache headers but raise the exception
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e),
            headers={"Cache-Control": "public, max-age=60"}  # Shorter cache time for errors
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/me", response_model=ReviewList)
def read_user_reviews(
        *,
        response: Response,
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get reviews by the current user.
    
    Returns a paginated list of reviews created by the authenticated user.
    This includes reviews in all moderation states (pending, approved, rejected).
    """
    # Set shorter cache control headers - personal data should refresh more often
    response.headers["Cache-Control"] = "private, max-age=60"
    
    try:
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
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("", response_model=Review, status_code=status.HTTP_201_CREATED)
def create_review(
        *,
        db: Session = Depends(get_db),
        review_in: ReviewCreate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new review.
    
    Creates a new product review with the provided rating and content.
    Reviews are initially created with a 'pending' moderation status
    and must be approved before they appear publicly.
    """
    try:
        return review_service.create(db, user_id=current_user.id, review_in=review_in)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{review_id}", response_model=Review)
def read_review(
        *,
        response: Response,
        db: Session = Depends(get_db),
        review_id: UUID = Path(..., description="The review ID"),
) -> Any:
    """
    Get a specific review by ID.
    
    Returns detailed information about a specific review, including its
    content, rating, and metadata like creation date and helpfulness votes.
    """
    # Set cache control headers - reviews change infrequently
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
        return review_service.get_by_id(db, review_id=str(review_id))
    except NotFoundException as e:
        # Keep the cache headers but raise the exception
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e),
            headers={"Cache-Control": "public, max-age=60"}  # Shorter cache time for errors
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{review_id}", response_model=Review)
def update_review(
        *,
        db: Session = Depends(get_db),
        review_id: UUID = Path(..., description="The review ID"),
        review_in: ReviewUpdate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a review.
    
    Updates an existing review with new content or rating.
    Users can only update their own reviews unless they are administrators.
    Updated reviews may be subject to re-moderation.
    """
    try:
        return review_service.update(
            db, review_id=str(review_id), user_id=current_user.id, review_in=review_in
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
        *,
        db: Session = Depends(get_db),
        review_id: UUID = Path(..., description="The review ID"),
        current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a review.
    
    Permanently removes a review from the system.
    Users can only delete their own reviews unless they are administrators.
    """
    try:
        review_service.delete(
            db, review_id=str(review_id), user_id=current_user.id, is_admin=current_user.is_superuser
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{review_id}/replies", response_model=ReviewReply, status_code=status.HTTP_201_CREATED)
def create_review_reply(
        *,
        db: Session = Depends(get_db),
        review_id: UUID = Path(..., description="The review ID"),
        reply_in: ReviewReplyCreate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Add a reply to a review.
    
    Creates a new reply to an existing review.
    Replies can be added by any authenticated user, but are typically
    used by store representatives to respond to customer reviews.
    """
    try:
        return review_service.add_reply(
            db, review_id=str(review_id), user_id=current_user.id, reply_in=reply_in
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/replies/{reply_id}", response_model=ReviewReply)
def update_review_reply(
        *,
        db: Session = Depends(get_db),
        reply_id: UUID = Path(..., description="The reply ID"),
        reply_in: ReviewReplyUpdate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a review reply.
    
    Updates an existing reply with new content.
    Users can only update their own replies unless they are administrators.
    """
    try:
        return review_service.update_reply(
            db, reply_id=str(reply_id), user_id=current_user.id,
            reply_in=reply_in, is_admin=current_user.is_superuser
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/replies/{reply_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review_reply(
        *,
        db: Session = Depends(get_db),
        reply_id: UUID = Path(..., description="The reply ID"),
        current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a review reply.
    
    Permanently removes a reply from the system.
    Users can only delete their own replies unless they are administrators.
    """
    try:
        review_service.delete_reply(
            db, reply_id=str(reply_id), user_id=current_user.id, is_admin=current_user.is_superuser
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{review_id}/helpful")
def vote_review_helpful(
        *,
        db: Session = Depends(get_db),
        review_id: UUID = Path(..., description="The review ID"),
) -> Any:
    """
    Vote a review as helpful.
    
    Increases the helpful vote count for a review.
    This helps other customers find the most useful reviews.
    """
    try:
        review_service.vote_helpful(db, review_id=str(review_id))
        return {"message": "Thank you for your feedback"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{review_id}/not-helpful")
def vote_review_not_helpful(
        *,
        db: Session = Depends(get_db),
        review_id: UUID = Path(..., description="The review ID"),
) -> Any:
    """
    Vote a review as not helpful.
    
    Increases the not helpful vote count for a review.
    This helps identify reviews that may not be providing useful information.
    """
    try:
        review_service.vote_not_helpful(db, review_id=str(review_id))
        return {"message": "Thank you for your feedback"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Admin endpoints
@router.get("/admin/pending", response_model=ReviewList)
def read_pending_reviews(
        *,
        response: Response,
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get pending reviews for moderation. Only for superusers.
    
    Returns a paginated list of reviews that are awaiting moderation.
    This endpoint is used by administrators to review and approve/reject
    user-submitted reviews before they appear publicly.
    """
    # Set shorter cache control headers - admin data should refresh more often
    response.headers["Cache-Control"] = "private, max-age=30"
    
    try:
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
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/admin/{review_id}/moderate", response_model=Review)
def moderate_review(
        *,
        db: Session = Depends(get_db),
        review_id: UUID = Path(..., description="The review ID"),
        moderation: ReviewModerationUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Moderate a review. Only for superusers.
    
    Updates the moderation status of a review (approve or reject).
    Approved reviews will be visible to all users, while rejected reviews
    will only be visible to the review author and administrators.
    """
    try:
        return review_service.moderate_review(
            db, review_id=str(review_id), moderator_id=current_user.id,
            status=moderation.status, notes=moderation.notes
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/admin/{review_id}/feature", response_model=Review)
def feature_review(
        *,
        db: Session = Depends(get_db),
        review_id: UUID = Path(..., description="The review ID"),
        featured: bool = Body(..., embed=True),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Feature or unfeature a review. Only for superusers.
    
    Marks a review as featured or removes the featured status.
    Featured reviews are typically displayed prominently on product pages
    or in marketing materials.
    """
    try:
        review = review_service.get_by_id(db, review_id=str(review_id))
        review.is_featured = featured
        db.add(review)
        db.commit()
        db.refresh(review)
        return review
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
