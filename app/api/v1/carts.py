from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Cookie, Depends, Header, HTTPException, Path, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_active_user,
    get_optional_current_user,
)
from app.core.exceptions import NotFoundException, BadRequestException
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


@router.post("", response_model=Cart, status_code=status.HTTP_201_CREATED)
def create_cart(
        response: Response,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> Any:
    """
    Create a new cart.
    
    Creates a new shopping cart or returns an existing one.
    The cart is identified by either the authenticated user or a session ID.
    
    Uses the following order of precedence:
    1. User authentication (if logged in)
    2. Session ID from X-Session-ID header
    3. Session ID from cookie
    """
    # Set cache control headers - cart data is private and changes frequently
    response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # Determine the session identifier
        session_identifier = x_session_id or session_id
        
        # Create cart based on user or session
        if current_user:
            cart = cart_service.get_or_create_cart(db, user_id=current_user.id)
        elif session_identifier:
            cart = cart_service.get_or_create_cart(db, session_id=session_identifier)
        else:
            # No way to identify the cart
            raise BadRequestException("No user authentication or session identifier provided")
        
        return cart
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=Cart)
def read_cart(
        response: Response,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> Any:
    """
    Get the current cart.
    
    Retrieves the current shopping cart with all items and pricing information.
    Creates a new cart if one doesn't exist.
    
    Uses the following order of precedence:
    1. User authentication (if logged in)
    2. Session ID from X-Session-ID header
    3. Session ID from cookie
    """
    # Set cache control headers - cart data is private and changes frequently
    response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # Determine the session identifier
        session_identifier = x_session_id or session_id

        # Get or create cart based on user or session
        if current_user:
            cart = cart_service.get_or_create_cart(db, user_id=current_user.id)
        elif session_identifier:
            cart = cart_service.get_or_create_cart(db, session_id=session_identifier)
        else:
            # No way to identify the cart
            raise BadRequestException("No user authentication or session identifier provided")

        return cart
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/summary", response_model=CartSummary)
def read_cart_summary(
        response: Response,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> Any:
    """
    Get a summary of the current cart.
    
    Returns a lightweight summary of the cart with just the item count and subtotal.
    This is useful for displaying cart information in headers or navigation bars
    without loading the full cart details.
    
    Returns null if no cart exists.
    """
    # Set cache control headers - cart data is private and changes frequently
    response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
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
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/items", response_model=CartItem, status_code=status.HTTP_201_CREATED)
def add_cart_item(
        *,
        response: Response,
        db: Session = Depends(get_db),
        item_in: CartItemCreate,
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> Any:
    """
    Add an item to the cart.
    
    Adds a product to the shopping cart with the specified quantity.
    If the product already exists in the cart, the quantity will be increased.
    
    Optionally accepts a product variant ID and custom metadata.
    """
    # Set cache control headers - cart data is private and changes frequently
    response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # Determine the session identifier
        session_identifier = x_session_id or session_id

        # Get or create cart based on user or session
        if current_user:
            cart = cart_service.get_or_create_cart(db, user_id=current_user.id)
        elif session_identifier:
            cart = cart_service.get_or_create_cart(db, session_id=session_identifier)
        else:
            # No way to identify the cart
            raise BadRequestException("No user authentication or session identifier provided")

        # Add item to cart
        return cart_service.add_item(
            db,
            cart_id=cart.id,
            product_id=item_in.product_id,
            quantity=item_in.quantity,
            variant_id=item_in.variant_id,
            metadata=item_in.item_metadata,
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/items/{item_id}", response_model=Optional[CartItem])
def update_cart_item(
        *,
        response: Response,
        db: Session = Depends(get_db),
        item_id: UUID = Path(..., description="Cart item ID"),
        item_in: CartItemUpdate,
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> Any:
    """
    Update a cart item's quantity.
    
    Updates the quantity of an existing item in the cart.
    If the quantity is set to 0, the item will be removed from the cart.
    """
    # Set cache control headers - cart data is private and changes frequently
    response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # Determine the session identifier
        session_identifier = x_session_id or session_id

        # Get cart based on user or session
        if current_user:
            cart = cart_service.get_cart(db, user_id=current_user.id)
        elif session_identifier:
            cart = cart_service.get_cart(db, session_id=session_identifier)
        else:
            # No way to identify the cart
            raise BadRequestException("No user authentication or session identifier provided")

        if not cart:
            raise NotFoundException("Cart not found")

        # Update item quantity
        return cart_service.update_item_quantity(
            db, cart_id=cart.id, item_id=str(item_id), quantity=item_in.quantity
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
        *,
        response: Response,
        db: Session = Depends(get_db),
        item_id: UUID = Path(..., description="Cart item ID"),
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> None:
    """
    Remove an item from the cart.
    
    Completely removes an item from the cart regardless of quantity.
    """
    # Set cache control headers - cart data is private and changes frequently
    response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # Determine the session identifier
        session_identifier = x_session_id or session_id

        # Get cart based on user or session
        if current_user:
            cart = cart_service.get_cart(db, user_id=current_user.id)
        elif session_identifier:
            cart = cart_service.get_cart(db, session_id=session_identifier)
        else:
            # No way to identify the cart
            raise BadRequestException("No user authentication or session identifier provided")

        if not cart:
            raise NotFoundException("Cart not found")

        # Remove item from cart
        cart_service.remove_item(db, cart_id=cart.id, item_id=str(item_id))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
        *,
        response: Response,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> None:
    """
    Remove all items from the cart.
    
    Completely empties the cart, removing all items.
    The cart itself is not deleted, just emptied.
    """
    # Set cache control headers - cart data is private and changes frequently
    response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # Determine the session identifier
        session_identifier = x_session_id or session_id

        # Get cart based on user or session
        if current_user:
            cart = cart_service.get_cart(db, user_id=current_user.id)
        elif session_identifier:
            cart = cart_service.get_cart(db, session_id=session_identifier)
        else:
            # No way to identify the cart
            raise BadRequestException("No user authentication or session identifier provided")

        if not cart:
            raise NotFoundException("Cart not found")

        # Clear cart
        cart_service.clear_cart(db, cart_id=cart.id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/coupon", response_model=Cart)
def apply_coupon(
        *,
        response: Response,
        db: Session = Depends(get_db),
        coupon_code: str = Body(..., embed=True),
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> Any:
    """
    Apply a coupon to the cart.
    
    Applies a discount coupon to the cart.
    The coupon code is validated and the discount is applied if valid.
    Returns the updated cart with the discount applied.
    """
    # Set cache control headers - cart data is private and changes frequently
    response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # Determine the session identifier
        session_identifier = x_session_id or session_id

        # Get cart based on user or session
        if current_user:
            cart = cart_service.get_cart(db, user_id=current_user.id)
        elif session_identifier:
            cart = cart_service.get_cart(db, session_id=session_identifier)
        else:
            # No way to identify the cart
            raise BadRequestException("No user authentication or session identifier provided")

        if not cart:
            raise NotFoundException("Cart not found")

        # Apply coupon
        return cart_service.apply_coupon(db, cart_id=cart.id, coupon_code=coupon_code)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/coupon", response_model=Cart)
def remove_coupon(
        *,
        response: Response,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_optional_current_user),
        session_id: Optional[str] = Cookie(None),
        x_session_id: Optional[str] = Header(None),
) -> Any:
    """
    Remove a coupon from the cart.
    
    Removes any applied coupon from the cart.
    Returns the updated cart with the discount removed.
    """
    # Set cache control headers - cart data is private and changes frequently
    response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # Determine the session identifier
        session_identifier = x_session_id or session_id

        # Get cart based on user or session
        if current_user:
            cart = cart_service.get_cart(db, user_id=current_user.id)
        elif session_identifier:
            cart = cart_service.get_cart(db, session_id=session_identifier)
        else:
            # No way to identify the cart
            raise BadRequestException("No user authentication or session identifier provided")

        if not cart:
            raise NotFoundException("Cart not found")

        # Remove coupon
        return cart_service.remove_coupon(db, cart_id=cart.id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/associate-user", response_model=Cart)
def associate_user_with_cart(
        *,
        response: Response,
        db: Session = Depends(get_db),
        session_id: str = Body(..., embed=True),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Associate a user with a cart (e.g., after login).
    
    Links an anonymous cart (identified by session ID) with a user account.
    This is typically used when a user logs in after adding items to their cart as a guest.
    If the user already has a cart, the items from the session cart will be merged.
    """
    # Set cache control headers - cart data is private and changes frequently
    response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # Get cart by session ID
        cart = cart_service.get_cart(db, session_id=session_id)
        if not cart:
            raise NotFoundException("Cart not found")

        # Associate user with cart
        return cart_service.associate_user_with_cart(db, cart_id=cart.id, user_id=current_user.id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
