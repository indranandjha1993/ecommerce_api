from typing import Any, Optional

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_active_superuser,
    get_optional_current_user,
)
from app.api.dependencies.pagination import PaginationParams, get_pagination
from app.db.session import get_db
from app.models.user import User
from app.schemas.coupon import (
    Coupon,
    CouponCreate,
    CouponUpdate,
    CouponList,
    CouponValidationRequest,
    CouponValidationResponse,
    CouponApplicationRequest,
    CouponApplicationResponse,
)
from app.services.coupon import coupon_service

router = APIRouter()


@router.get("", response_model=CouponList)
def read_coupons(
        *,
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get all coupons with pagination. Only for superusers.
    """
    coupons, total = coupon_service.get_all(db, skip=pagination.skip, limit=pagination.size)

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": coupons,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }


@router.get("/valid", response_model=CouponList)
def read_valid_coupons(
        *,
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get valid coupons with pagination. Only for superusers.
    """
    coupons, total = coupon_service.get_valid_coupons(
        db, page=pagination.page, size=pagination.size
    )

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": coupons,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }


@router.get("/expired", response_model=CouponList)
def read_expired_coupons(
        *,
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get expired coupons with pagination. Only for superusers.
    """
    coupons, total = coupon_service.get_expired_coupons(
        db, page=pagination.page, size=pagination.size
    )

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": coupons,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }


@router.post("", response_model=Coupon, status_code=status.HTTP_201_CREATED)
def create_coupon(
        *,
        db: Session = Depends(get_db),
        coupon_in: CouponCreate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create a new coupon. Only for superusers.
    """
    return coupon_service.create(db, coupon_in=coupon_in)


@router.get("/{coupon_id}", response_model=Coupon)
def read_coupon(
        *,
        db: Session = Depends(get_db),
        coupon_id: str = Path(..., description="The coupon ID"),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get a specific coupon by ID. Only for superusers.
    """
    return coupon_service.get_by_id(db, coupon_id=coupon_id)


@router.get("/code/{code}", response_model=Coupon)
def read_coupon_by_code(
        *,
        db: Session = Depends(get_db),
        code: str = Path(..., description="The coupon code"),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get a specific coupon by code. Only for superusers.
    """
    return coupon_service.get_by_code(db, code=code)


@router.put("/{coupon_id}", response_model=Coupon)
def update_coupon(
        *,
        db: Session = Depends(get_db),
        coupon_id: str = Path(..., description="The coupon ID"),
        coupon_in: CouponUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a coupon. Only for superusers.
    """
    return coupon_service.update(db, coupon_id=coupon_id, coupon_in=coupon_in)


@router.delete("/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coupon(
        *,
        db: Session = Depends(get_db),
        coupon_id: str = Path(..., description="The coupon ID"),
        current_user: User = Depends(get_current_active_superuser),
) -> None:
    """
    Delete a coupon. Only for superusers.
    """
    coupon_service.delete(db, coupon_id=coupon_id)


@router.post("/validate", response_model=CouponValidationResponse)
def validate_coupon(
        *,
        db: Session = Depends(get_db),
        validation: CouponValidationRequest,
        current_user: Optional[User] = Depends(get_optional_current_user),
) -> Any:
    """
    Validate a coupon.
    """
    coupon = coupon_service.validate_coupon(
        db,
        code=validation.code,
        user_id=current_user.id if current_user else None,
        order_total=validation.order_total,
        items=validation.items
    )

    discount_amount = coupon_service.calculate_discount(
        coupon,
        order_total=validation.order_total or 0,
        items=validation.items
    )

    return {
        "coupon": coupon,
        "discount_amount": discount_amount,
        "message": "Coupon is valid"
    }


@router.post("/apply", response_model=CouponApplicationResponse)
def apply_coupon(
        *,
        db: Session = Depends(get_db),
        application: CouponApplicationRequest,
        current_user: Optional[User] = Depends(get_optional_current_user),
) -> Any:
    """
    Apply a coupon to an order.
    """
    coupon, discount_amount = coupon_service.apply_coupon(
        db,
        code=application.code,
        order_id=application.order_id,
        user_id=current_user.id if current_user else None,
        order_total=application.order_total,
        items=application.items
    )

    return {
        "coupon": coupon,
        "discount_amount": discount_amount,
        "message": "Coupon applied successfully"
    }
