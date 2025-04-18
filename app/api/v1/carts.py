from typing import Any, Optional

from fastapi import APIRouter, Body, Cookie, Depends, Header, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_active_user,
    get_optional_current_user,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.cart import (
    Cart,
    CartItem,
    CartItemCreate,
    CartItemUpdate,
    CartSummary,
)
from app.services.cart import cart_service

router = APIRouter()


@router.get("", response_model=Cart)
def read_cart(
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> Any:
    """
    Get the current cart.

    Uses the following order of precedence:
    1. User authentication (if logged in)
    2. Session ID from X-Session-ID header
    3. Session ID from cookie
    """
    # Determine the session identifier
    session_identifier = x_session_id or session_id

    # Get or create cart based on user or session
    if current_user:
        cart = cart_service.get_or_create_cart(db, user_id=current_user.id)
    elif session_identifier:
        cart = cart_service.get_or_create_cart(db, session_id=session_identifier)
    else:
        # No way to identify the cart
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user authentication or session identifier provided",
        )

    return cart


@router.get("/summary", response_model=CartSummary)
def read_cart_summary(
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> Any:
    """
    Get a summary of the current cart (lighter weight than full cart).
    """
    # Determine the session identifier
    session_identifier = x_session_id or session_id

    # Get cart based on user or session
    if current_user:
        cart = cart_service.get_cart(db, user_id=current_user.id)
    elif session_identifier:
        cart = cart_service.get_cart(db, session_id=session_identifier)
    else:
        # No way to identify the cart
        return None

    if not cart:
        return None

    return {
        "id": cart.id,
        "item_count": cart.item_count,
        "subtotal": cart.subtotal,
    }


@router.post("/items", response_model=CartItem, status_code=status.HTTP_201_CREATED)
def add_cart_item(
        *,
        db: Session = Depends(get_db),
        item_in: CartItemCreate,
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> Any:
    """
    Add an item to the cart.
    """
    # Determine the session identifier
    session_identifier = x_session_id or session_id

    # Get or create cart based on user or session
    if current_user:
        cart = cart_service.get_or_create_cart(db, user_id=current_user.id)
    elif session_identifier:
        cart = cart_service.get_or_create_cart(db, session_id=session_identifier)
    else:
        # No way to identify the cart
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user authentication or session identifier provided",
        )

    # Add item to cart
    return cart_service.add_item(
        db,
        cart_id=cart.id,
        product_id=item_in.product_id,
        quantity=item_in.quantity,
        variant_id=item_in.variant_id,
        metadata=item_in.item_metadata,
    )


@router.put("/items/{item_id}", response_model=Optional[CartItem])
def update_cart_item(
        *,
        db: Session = Depends(get_db),
        item_id: str = Path(..., description="Cart item ID"),
        item_in: CartItemUpdate,
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> Any:
    """
    Update a cart item's quantity.
    """
    # Determine the session identifier
    session_identifier = x_session_id or session_id

    # Get cart based on user or session
    if current_user:
        cart = cart_service.get_cart(db, user_id=current_user.id)
    elif session_identifier:
        cart = cart_service.get_cart(db, session_id=session_identifier)
    else:
        # No way to identify the cart
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user authentication or session identifier provided",
        )

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    # Update item quantity
    return cart_service.update_item_quantity(
        db, cart_id=cart.id, item_id=item_id, quantity=item_in.quantity
    )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
        *,
        db: Session = Depends(get_db),
        item_id: str = Path(..., description="Cart item ID"),
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> None:
    """
    Remove an item from the cart.
    """
    # Determine the session identifier
    session_identifier = x_session_id or session_id

    # Get cart based on user or session
    if current_user:
        cart = cart_service.get_cart(db, user_id=current_user.id)
    elif session_identifier:
        cart = cart_service.get_cart(db, session_id=session_identifier)
    else:
        # No way to identify the cart
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user authentication or session identifier provided",
        )

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    # Remove item from cart
    cart_service.remove_item(db, cart_id=cart.id, item_id=item_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
        *,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> None:
    """
    Remove all items from the cart.
    """
    # Determine the session identifier
    session_identifier = x_session_id or session_id

    # Get cart based on user or session
    if current_user:
        cart = cart_service.get_cart(db, user_id=current_user.id)
    elif session_identifier:
        cart = cart_service.get_cart(db, session_id=session_identifier)
    else:
        # No way to identify the cart
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user authentication or session identifier provided",
        )

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    # Clear cart
    cart_service.clear_cart(db, cart_id=cart.id)


@router.post("/coupon", response_model=Cart)
def apply_coupon(
        *,
        db: Session = Depends(get_db),
        coupon_code: str = Body(..., embed=True),
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> Any:
    """
    Apply a coupon to the cart.
    """
    # Determine the session identifier
    session_identifier = x_session_id or session_id

    # Get cart based on user or session
    if current_user:
        cart = cart_service.get_cart(db, user_id=current_user.id)
    elif session_identifier:
        cart = cart_service.get_cart(db, session_id=session_identifier)
    else:
        # No way to identify the cart
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user authentication or session identifier provided",
        )

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    # Apply coupon
    return cart_service.apply_coupon(db, cart_id=cart.id, coupon_code=coupon_code)


@router.delete("/coupon", response_model=Cart)
def remove_coupon(
        *,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> Any:
    """
    Remove a coupon from the cart.
    """
    # Determine the session identifier
    session_identifier = x_session_id or session_id

    # Get cart based on user or session
    if current_user:
        cart = cart_service.get_cart(db, user_id=current_user.id)
    elif session_identifier:
        cart = cart_service.get_cart(db, session_id=session_identifier)
    else:
        # No way to identify the cart
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user authentication or session identifier provided",
        )

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    # Remove coupon
    return cart_service.remove_coupon(db, cart_id=cart.id)


@router.post("/associate-user", response_model=Cart)
def associate_user_with_cart(
        *,
        db: Session = Depends(get_db),
        session_id: str = Body(..., embed=True),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Associate a user with a cart (e.g., after login).
    """
    # Get cart by session ID
    cart = cart_service.get_cart(db, session_id=session_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    # Associate user with cart
    return cart_service.associate_user_with_cart(db, cart_id=cart.id, user_id=current_user.id)
