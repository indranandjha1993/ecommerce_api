from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Cookie, Depends, Header, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_active_user,
    get_current_active_superuser,
    get_optional_current_user,
)
from app.api.dependencies.pagination import PaginationParams, get_pagination
from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
)
from app.db.session import get_db
from app.models.order import OrderStatus, PaymentStatus
from app.models.payment import PaymentProvider
from app.models.shipping import ShippingCarrier, ShippingStatus
from app.models.user import User
from app.schemas.order import (
    Order,
    OrderCreate,
    OrderUpdate,
    OrderAdminUpdate,
    OrderList,
    Payment,
)
from app.services.order import order_service

router = APIRouter()


@router.post("", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(
        *,
        db: Session = Depends(get_db),
        order_in: OrderCreate,
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> Any:
    """
    Create a new order from a cart.
    """
    # Determine the session identifier
    session_identifier = x_session_id or session_id

    # Validate cart_id
    if not order_in.cart_id:
        raise BadRequestException(detail="Cart ID is required")

    # Create order
    return order_service.create_from_cart(
        db,
        cart_id=order_in.cart_id,
        order_data=order_in,
        user_id=current_user.id if current_user else None
    )


@router.get("/me", response_model=OrderList)
def read_user_orders(
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all orders for the current user.
    """
    orders, total = order_service.get_user_orders(
        db, user_id=current_user.id, page=pagination.page, size=pagination.size
    )

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": orders,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }


@router.get("/me/{order_id}", response_model=Order)
def read_user_order(
        *,
        db: Session = Depends(get_db),
        order_id: str,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific order for the current user.
    """
    order = order_service.get_by_id(db, order_id=order_id)

    # Check if order belongs to user
    if str(order.user_id) != str(current_user.id):
        raise ForbiddenException(detail="Not authorized to access this order")

    return order


@router.get("/guest/{guest_token}", response_model=Order)
def read_guest_order(
        *,
        db: Session = Depends(get_db),
        guest_token: str,
) -> Any:
    """
    Get a guest order by token.
    """
    return order_service.get_by_guest_token(db, guest_token=guest_token)


@router.get("/number/{order_number}", response_model=Order)
def read_order_by_number(
        *,
        db: Session = Depends(get_db),
        order_number: str,
        current_user: Optional[User] = Depends(get_optional_current_user),
) -> Any:
    """
    Get an order by order number.
    """
    order = order_service.get_by_order_number(db, order_number=order_number)

    # Check authorization - only admin or order owner can view
    if current_user:
        if not current_user.is_superuser and str(order.user_id) != str(current_user.id):
            raise ForbiddenException(detail="Not authorized to access this order")
    else:
        # For anonymous users, they must provide the guest token
        if not order.guest_token:
            raise ForbiddenException(detail="Not authorized to access this order")

    return order


@router.put("/me/{order_id}", response_model=Order)
def update_user_order(
        *,
        db: Session = Depends(get_db),
        order_id: str,
        order_in: OrderUpdate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a specific order for the current user.
    """
    order = order_service.get_by_id(db, order_id=order_id)

    # Check if order belongs to user
    if str(order.user_id) != str(current_user.id):
        raise ForbiddenException(detail="Not authorized to update this order")

    # Check if order can be updated (certain statuses may not allow updates)
    if order.status not in [OrderStatus.PENDING, OrderStatus.ON_HOLD]:
        raise BadRequestException(detail="Order cannot be updated in its current status")

    # Update only allowed fields for users
    allowed_fields = ["customer_notes"]
    update_data = {k: v for k, v in order_in.model_dump(exclude_unset=True).items() if k in allowed_fields}

    if not update_data:
        return order

    return order_service.update(db, order_id=order_id, order_in=OrderUpdate(**update_data))


@router.post("/me/{order_id}/cancel", response_model=Order)
def cancel_user_order(
        *,
        db: Session = Depends(get_db),
        order_id: str,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Cancel a specific order for the current user.
    """
    order = order_service.get_by_id(db, order_id=order_id)

    # Check if order belongs to user
    if str(order.user_id) != str(current_user.id):
        raise ForbiddenException(detail="Not authorized to cancel this order")

    # Check if order can be cancelled
    if not order.can_be_cancelled:
        raise BadRequestException(detail="Order cannot be cancelled in its current status")

    return order_service.cancel_order(db, order_id=order_id)


@router.post("/me/{order_id}/payment", response_model=Payment)
def process_user_payment(
        *,
        db: Session = Depends(get_db),
        order_id: str,
        provider: PaymentProvider = Body(...),
        amount: float = Body(...),
        payment_data: Dict[str, Any] = Body(...),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Process a payment for a specific order.
    """
    order = order_service.get_by_id(db, order_id=order_id)

    # Check if order belongs to user
    if str(order.user_id) != str(current_user.id):
        raise ForbiddenException(detail="Not authorized to pay for this order")

    # Check if payment is required
    if order.payment_status == PaymentStatus.PAID:
        raise BadRequestException(detail="Order is already paid")

    # Process payment
    from decimal import Decimal
    return order_service.process_payment(
        db, order_id=order_id, provider=provider,
        amount=Decimal(str(amount)), payment_data=payment_data
    )


# Admin endpoints
@router.get("", response_model=OrderList)
def read_orders(
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get all orders with pagination. Only for superusers.
    """
    if status:
        orders, total = order_service.get_orders_by_status(
            db, status=status, page=pagination.page, size=pagination.size
        )
    else:
        orders, total = order_service.get_all(
            db, page=pagination.page, size=pagination.size
        )

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": orders,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }


@router.get("/{order_id}", response_model=Order)
def read_order(
        *,
        db: Session = Depends(get_db),
        order_id: str,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get a specific order by ID. Only for superusers.
    """
    return order_service.get_by_id(db, order_id=order_id)


@router.put("/{order_id}", response_model=Order)
def update_order(
        *,
        db: Session = Depends(get_db),
        order_id: str,
        order_in: OrderAdminUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a specific order. Only for superusers.
    """
    return order_service.update_admin(db, order_id=order_id, order_in=order_in)


@router.post("/{order_id}/cancel", response_model=Order)
def cancel_order(
        *,
        db: Session = Depends(get_db),
        order_id: str,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Cancel a specific order. Only for superusers.
    """
    return order_service.cancel_order(db, order_id=order_id)


@router.post("/{order_id}/shipping", response_model=Order)
def update_order_shipping(
        *,
        db: Session = Depends(get_db),
        order_id: str,
        carrier: Optional[ShippingCarrier] = Body(None),
        tracking_number: Optional[str] = Body(None),
        status: Optional[ShippingStatus] = Body(None),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update shipping information for a specific order. Only for superusers.
    """
    # Update shipping
    shipping = order_service.update_shipping(
        db, order_id=order_id, carrier=carrier,
        tracking_number=tracking_number, status=status
    )

    # Return updated order
    return order_service.get_by_id(db, order_id=order_id)
