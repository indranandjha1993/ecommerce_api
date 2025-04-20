from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Cookie, Depends, Header, HTTPException, Path, Query, Response, status
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
    NotFoundException,
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
        response: Response,
        db: Session = Depends(get_db),
        order_in: OrderCreate,
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> Any:
    """
    Create a new order from a cart.
    
    Converts a shopping cart into an order with shipping and payment information.
    The cart must contain at least one item.
    After successful order creation, the cart will be marked as inactive.
    """
    # Set cache control headers - order creation should not be cached
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    
    try:
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
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/me", response_model=OrderList)
def read_user_orders(
        response: Response,
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all orders for the current user.
    
    Returns a paginated list of orders placed by the authenticated user,
    sorted by creation date (newest first).
    """
    # Set cache control headers - order data is private but can be cached briefly
    response.headers["Cache-Control"] = "private, max-age=60"
    
    try:
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
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/me/{order_id}", response_model=Order)
def read_user_order(
        *,
        response: Response,
        db: Session = Depends(get_db),
        order_id: UUID = Path(..., description="The order ID"),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific order for the current user.
    
    Returns detailed information about a specific order placed by the authenticated user.
    Includes order items, shipping information, and payment details.
    """
    # Set cache control headers - order data is private but can be cached briefly
    response.headers["Cache-Control"] = "private, max-age=60"
    
    try:
        order = order_service.get_by_id(db, order_id=str(order_id))

        # Check if order belongs to user
        if str(order.user_id) != str(current_user.id):
            raise ForbiddenException(detail="Not authorized to access this order")

        return order
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/guest/{guest_token}", response_model=Order)
def read_guest_order(
        *,
        response: Response,
        db: Session = Depends(get_db),
        guest_token: str = Path(..., min_length=8, max_length=64, description="The guest order token"),
) -> Any:
    """
    Get a guest order by token.
    
    Returns detailed information about an order placed by a guest user.
    The guest token is provided to the customer during checkout and
    can be used to track their order without creating an account.
    """
    # Set cache control headers - order data is private but can be cached briefly
    response.headers["Cache-Control"] = "private, max-age=60"
    
    try:
        return order_service.get_by_guest_token(db, guest_token=guest_token)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/number/{order_number}", response_model=Order)
def read_order_by_number(
        *,
        response: Response,
        db: Session = Depends(get_db),
        order_number: str = Path(..., min_length=3, max_length=50, description="The order number"),
        current_user: Optional[User] = Depends(get_optional_current_user),
) -> Any:
    """
    Get an order by order number.
    
    Returns detailed information about an order identified by its order number.
    This endpoint can be used by both authenticated users and guests,
    but authorization checks are performed to ensure only the order owner
    or administrators can access the order details.
    """
    # Set cache control headers - order data is private but can be cached briefly
    response.headers["Cache-Control"] = "private, max-age=60"
    
    try:
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
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/me/{order_id}", response_model=Order)
def update_user_order(
        *,
        response: Response,
        db: Session = Depends(get_db),
        order_id: UUID = Path(..., description="The order ID"),
        order_in: OrderUpdate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a specific order for the current user.
    
    Allows a user to update limited fields of their own order.
    Currently, only customer notes can be updated by regular users.
    The order must be in PENDING or ON_HOLD status to be updated.
    """
    # Set cache control headers - order updates should not be cached
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    
    try:
        order = order_service.get_by_id(db, order_id=str(order_id))

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

        return order_service.update(db, order_id=str(order_id), order_in=OrderUpdate(**update_data))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/me/{order_id}/cancel", response_model=Order)
def cancel_user_order(
        *,
        response: Response,
        db: Session = Depends(get_db),
        order_id: UUID = Path(..., description="The order ID"),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Cancel a specific order for the current user.
    
    Allows a user to cancel their own order if it's in a cancellable state.
    Orders can typically only be cancelled if they are in PENDING or ON_HOLD status
    and haven't been shipped yet.
    """
    # Set cache control headers - order cancellation should not be cached
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    
    try:
        order = order_service.get_by_id(db, order_id=str(order_id))

        # Check if order belongs to user
        if str(order.user_id) != str(current_user.id):
            raise ForbiddenException(detail="Not authorized to cancel this order")

        # Check if order can be cancelled
        if not order.can_be_cancelled:
            raise BadRequestException(detail="Order cannot be cancelled in its current status")

        return order_service.cancel_order(db, order_id=str(order_id))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/me/{order_id}/payment", response_model=Payment)
def process_user_payment(
        *,
        response: Response,
        db: Session = Depends(get_db),
        order_id: UUID = Path(..., description="The order ID"),
        provider: PaymentProvider = Body(..., description="Payment provider (e.g., stripe, paypal)"),
        amount: float = Body(..., gt=0, description="Payment amount"),
        payment_data: Dict[str, Any] = Body(..., description="Provider-specific payment data"),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Process a payment for a specific order.
    
    Processes a payment for an order using the specified payment provider.
    The payment amount must match the order's outstanding balance.
    Payment data is provider-specific and will be passed to the payment processor.
    
    Returns the payment record if successful.
    """
    # Set cache control headers - payment processing should not be cached
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    
    try:
        order = order_service.get_by_id(db, order_id=str(order_id))

        # Check if order belongs to user
        if str(order.user_id) != str(current_user.id):
            raise ForbiddenException(detail="Not authorized to pay for this order")

        # Check if payment is required
        if order.payment_status == PaymentStatus.PAID:
            raise BadRequestException(detail="Order is already paid")

        # Process payment
        from decimal import Decimal
        return order_service.process_payment(
            db, order_id=str(order_id), provider=provider,
            amount=Decimal(str(amount)), payment_data=payment_data
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Admin endpoints
@router.get("", response_model=OrderList)
def read_orders(
        response: Response,
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
        payment_status: Optional[PaymentStatus] = Query(None, description="Filter by payment status"),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get all orders with pagination. Only for superusers.
    
    Returns a paginated list of all orders in the system.
    Can be filtered by order status and/or payment status.
    Results are sorted by creation date (newest first).
    """
    # Set cache control headers - admin data is private but can be cached briefly
    response.headers["Cache-Control"] = "private, max-age=30"
    
    try:
        if status:
            orders, total = order_service.get_orders_by_status(
                db, status=status, page=pagination.page, size=pagination.size
            )
        elif payment_status:
            orders, total = order_service.get_orders_by_payment_status(
                db, payment_status=payment_status, page=pagination.page, size=pagination.size
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
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{order_id}", response_model=Order)
def read_order(
        *,
        response: Response,
        db: Session = Depends(get_db),
        order_id: UUID = Path(..., description="The order ID"),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get a specific order by ID. Only for superusers.
    
    Returns detailed information about a specific order,
    including order items, shipping information, and payment details.
    This admin endpoint provides full access to all order data.
    """
    # Set cache control headers - admin data is private but can be cached briefly
    response.headers["Cache-Control"] = "private, max-age=30"
    
    try:
        return order_service.get_by_id(db, order_id=str(order_id))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{order_id}", response_model=Order)
def update_order(
        *,
        response: Response,
        db: Session = Depends(get_db),
        order_id: UUID = Path(..., description="The order ID"),
        order_in: OrderAdminUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a specific order. Only for superusers.
    
    Allows administrators to update various aspects of an order,
    including status, payment status, shipping details, and more.
    This endpoint provides full update capabilities for order management.
    """
    # Set cache control headers - order updates should not be cached
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    
    try:
        return order_service.update_admin(db, order_id=str(order_id), order_in=order_in)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{order_id}/cancel", response_model=Order)
def cancel_order(
        *,
        response: Response,
        db: Session = Depends(get_db),
        order_id: UUID = Path(..., description="The order ID"),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Cancel a specific order. Only for superusers.
    
    Allows administrators to cancel any order regardless of its current status.
    This is an administrative override that bypasses the normal cancellation rules.
    Use with caution, especially for orders that are already in fulfillment.
    """
    # Set cache control headers - order cancellation should not be cached
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    
    try:
        return order_service.cancel_order(db, order_id=str(order_id))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{order_id}/shipping", response_model=Order)
def update_order_shipping(
        *,
        response: Response,
        db: Session = Depends(get_db),
        order_id: UUID = Path(..., description="The order ID"),
        carrier: Optional[ShippingCarrier] = Body(None, description="Shipping carrier (e.g., ups, fedex)"),
        tracking_number: Optional[str] = Body(None, description="Tracking number for the shipment"),
        status: Optional[ShippingStatus] = Body(None, description="Current shipping status"),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update shipping information for a specific order. Only for superusers.
    
    Allows administrators to update shipping details for an order,
    including the carrier, tracking number, and shipping status.
    This endpoint is typically used when an order is shipped or
    when there are updates to the shipping status.
    """
    # Set cache control headers - shipping updates should not be cached
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    
    try:
        # Update shipping
        shipping = order_service.update_shipping(
            db, order_id=str(order_id), carrier=carrier,
            tracking_number=tracking_number, status=status
        )

        # Return updated order
        return order_service.get_by_id(db, order_id=str(order_id))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
