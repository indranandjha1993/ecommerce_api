import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.repositories.cart import cart_repository


class CartService:
    """
    Cart service for business logic.
    """

    def get_cart(
            self, db: Session, *, user_id: Optional[uuid.UUID] = None, session_id: Optional[str] = None
    ) -> Optional[Cart]:
        """
        Get a cart by user ID or session ID. If the cart doesn't exist, return None.
        """
        if user_id:
            return cart_repository.get_by_user_id(db, user_id=user_id)
        elif session_id:
            return cart_repository.get_by_session_id(db, session_id=session_id)
        return None

    def get_or_create_cart(
            self, db: Session, *, user_id: Optional[uuid.UUID] = None, session_id: Optional[str] = None
    ) -> Cart:
        """
        Get a cart by user ID or session ID. If the cart doesn't exist, create it.
        """
        cart = self.get_cart(db, user_id=user_id, session_id=session_id)
        if cart:
            # Update last activity
            return cart_repository.update_last_activity(db, cart_id=cart.id)

        # Create new cart
        cart_data = {"is_active": True}
        if user_id:
            cart_data["user_id"] = user_id
        if session_id:
            cart_data["session_id"] = session_id

        cart = cart_repository.create(db, obj_in=cart_data)
        return cart

    def get_cart_by_id(self, db: Session, *, cart_id: uuid.UUID) -> Cart:
        """
        Get a cart by ID.
        """
        cart = cart_repository.get_with_items(db, cart_id=cart_id)
        if not cart:
            raise NotFoundException(detail="Cart not found")
        return cart

    def add_item(
            self, db: Session, *, cart_id: uuid.UUID, product_id: uuid.UUID,
            quantity: int = 1, variant_id: Optional[uuid.UUID] = None,
            metadata: Optional[Dict[str, Any]] = None
    ) -> CartItem:
        """
        Add an item to a cart. If the item already exists, update its quantity.
        """
        # Check if the cart exists
        cart = cart_repository.get(db, id=cart_id)
        if not cart:
            raise NotFoundException(detail="Cart not found")

        # Verify the product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise NotFoundException(detail="Product not found")

        # Verify the variant exists if provided
        if variant_id:
            variant = db.query(ProductVariant).filter(
                ProductVariant.id == variant_id,
                ProductVariant.product_id == product_id
            ).first()
            if not variant:
                raise NotFoundException(detail="Product variant not found")

        # Check inventory
        from app.models.inventory import Inventory

        if variant_id:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == product_id,
                Inventory.variant_id == variant_id
            ).first()
        else:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == product_id,
                Inventory.variant_id.is_(None)
            ).first()

        # Check if the product is in stock
        if inventory and inventory.quantity < quantity:
            raise BadRequestException(detail="Not enough stock available")

        # Add the item to the cart
        return cart_repository.add_item(
            db,
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
            variant_id=variant_id,
            metadata=metadata
        )

    def update_item_quantity(
            self, db: Session, *, cart_id: uuid.UUID, item_id: uuid.UUID, quantity: int
    ) -> Optional[CartItem]:
        """
        Update a cart item's quantity.
        """
        # Check if the cart exists
        cart = cart_repository.get(db, id=cart_id)
        if not cart:
            raise NotFoundException(detail="Cart not found")

        # Get the cart item
        item = db.query(CartItem).filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart_id
        ).first()

        if not item:
            raise NotFoundException(detail="Cart item not found")

        # If quantity is 0 or negative, remove the item
        if quantity <= 0:
            cart_repository.remove_item(db, cart_id=cart_id, item_id=item_id)
            return None

        # Check inventory
        from app.models.inventory import Inventory

        if item.variant_id:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.variant_id == item.variant_id
            ).first()
        else:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.variant_id.is_(None)
            ).first()

        # Check if the product is in stock
        if inventory and inventory.quantity < quantity:
            raise BadRequestException(detail="Not enough stock available")

        # Update the item quantity
        return cart_repository.update_item_quantity(
            db, cart_id=cart_id, item_id=item_id, quantity=quantity
        )

    def remove_item(self, db: Session, *, cart_id: uuid.UUID, item_id: uuid.UUID) -> bool:
        """
        Remove an item from a cart.
        """
        # Check if the cart exists
        cart = cart_repository.get(db, id=cart_id)
        if not cart:
            raise NotFoundException(detail="Cart not found")

        # Remove the item
        result = cart_repository.remove_item(db, cart_id=cart_id, item_id=item_id)
        if not result:
            raise NotFoundException(detail="Cart item not found")

        return True

    def clear_cart(self, db: Session, *, cart_id: uuid.UUID) -> bool:
        """
        Remove all items from a cart.
        """
        # Check if the cart exists
        cart = cart_repository.get(db, id=cart_id)
        if not cart:
            raise NotFoundException(detail="Cart not found")

        # Clear the cart
        return cart_repository.clear_items(db, cart_id=cart_id)

    def associate_user_with_cart(
            self, db: Session, *, cart_id: uuid.UUID, user_id: uuid.UUID
    ) -> Cart:
        """
        Associate a user with a cart (e.g., after login).
        """
        # Check if the cart exists
        cart = cart_repository.get(db, id=cart_id)
        if not cart:
            raise NotFoundException(detail="Cart not found")

        # Check if user already has an active cart
        user_cart = cart_repository.get_by_user_id(db, user_id=user_id)

        if user_cart:
            # Merge the anonymous cart into the user's cart
            return cart_repository.merge_carts(db, source_cart_id=cart_id, target_cart_id=user_cart.id)
        else:
            # Associate the cart with the user
            cart.user_id = user_id
            db.add(cart)
            db.commit()
            db.refresh(cart)
            return cart

    def apply_coupon(self, db: Session, *, cart_id: uuid.UUID, coupon_code: str) -> Cart:
        """
        Apply a coupon to a cart.
        """
        # Check if the cart exists
        cart = cart_repository.get_with_items(db, cart_id=cart_id)
        if not cart:
            raise NotFoundException(detail="Cart not found")

        # Validate coupon
        from app.models.coupon import Coupon
        from datetime import datetime

        coupon = db.query(Coupon).filter(
            Coupon.code == coupon_code,
            Coupon.is_active == True
        ).first()

        if not coupon:
            raise BadRequestException(detail="Invalid coupon code")

        # Check if coupon is valid (dates, usage limits)
        now = datetime.utcnow()

        if coupon.starts_at and coupon.starts_at > now:
            raise BadRequestException(detail="Coupon is not yet active")

        if coupon.expires_at and coupon.expires_at < now:
            raise BadRequestException(detail="Coupon has expired")

        if coupon.usage_limit and coupon.current_usage_count >= coupon.usage_limit:
            raise BadRequestException(detail="Coupon usage limit reached")

        # Check minimum requirements
        if coupon.minimum_order_amount and cart.subtotal < coupon.minimum_order_amount:
            raise BadRequestException(
                detail=f"Order total must be at least {coupon.minimum_order_amount} to use this coupon"
            )

        # Todo: More coupon validations (product/category restrictions, first order only)

        # Store coupon in cart metadata
        if not cart.cart_metadata:
            cart.cart_metadata = {}

        cart.cart_metadata["coupon_code"] = coupon_code
        db.add(cart)
        db.commit()
        db.refresh(cart)

        return cart

    def remove_coupon(self, db: Session, *, cart_id: uuid.UUID) -> Cart:
        """
        Remove a coupon from a cart.
        """
        # Check if the cart exists
        cart = cart_repository.get(db, id=cart_id)
        if not cart:
            raise NotFoundException(detail="Cart not found")

        # Remove coupon from metadata
        if cart.cart_metadata and "coupon_code" in cart.cart_metadata:
            cart.cart_metadata.pop("coupon_code")
            db.add(cart)
            db.commit()
            db.refresh(cart)

        return cart


cart_service = CartService()
