import uuid
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.cart import Cart, CartItem
from app.models.product_variant import ProductVariant
from app.repositories.base import BaseRepository
from app.schemas.cart import CartCreate, CartUpdate


class CartRepository(BaseRepository[Cart, CartCreate, CartUpdate]):
    """
    Cart repository for data access operations.
    """

    def get_by_user_id(self, db: Session, user_id: uuid.UUID) -> Optional[Cart]:
        """
        Get an active cart for a user.
        """
        return (
            db.query(Cart)
            .filter(Cart.user_id == user_id, Cart.is_active == True)
            .options(
                joinedload(Cart.items).joinedload(CartItem.product),
                joinedload(Cart.items).joinedload(CartItem.variant),
            )
            .order_by(Cart.created_at.desc())
            .first()
        )

    def get_by_session_id(self, db: Session, session_id: str) -> Optional[Cart]:
        """
        Get a cart by session ID.
        """
        return (
            db.query(Cart)
            .filter(Cart.session_id == session_id, Cart.is_active == True)
            .options(
                joinedload(Cart.items).joinedload(CartItem.product),
                joinedload(Cart.items).joinedload(CartItem.variant),
            )
            .first()
        )

    def get_with_items(self, db: Session, cart_id: uuid.UUID) -> Optional[Cart]:
        """
        Get a cart with its items.
        """
        return (
            db.query(Cart)
            .filter(Cart.id == cart_id)
            .options(
                joinedload(Cart.items).joinedload(CartItem.product),
                joinedload(Cart.items).joinedload(CartItem.variant),
            )
            .first()
        )

    def add_item(
            self, db: Session, cart_id: uuid.UUID, product_id: uuid.UUID,
            quantity: int, variant_id: Optional[uuid.UUID] = None,
            metadata: Optional[dict] = None
    ) -> CartItem:
        """
        Add an item to a cart.
        """
        # Check if the item already exists in the cart
        existing_item = db.query(CartItem).filter(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id,
            CartItem.variant_id == variant_id
        ).first()

        if existing_item:
            # Update existing item quantity
            existing_item.quantity += quantity
            db.add(existing_item)
            db.commit()
            db.refresh(existing_item)
            return existing_item

        # Get product price
        if variant_id:
            variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
            unit_price = variant.price if variant and variant.price else None
        else:
            unit_price = None

        # Create new cart item
        cart_item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            variant_id=variant_id,
            quantity=quantity,
            unit_price=unit_price,
            item_metadata=metadata,
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)

        return cart_item

    def update_item_quantity(
            self, db: Session, cart_id: uuid.UUID, item_id: uuid.UUID, quantity: int
    ) -> Optional[CartItem]:
        """
        Update a cart item's quantity.
        """
        item = db.query(CartItem).filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart_id
        ).first()

        if not item:
            return None

        if quantity <= 0:
            # Remove item if quantity is 0 or negative
            db.delete(item)
            db.commit()
            return None

        # Update quantity
        item.quantity = quantity
        db.add(item)
        db.commit()
        db.refresh(item)

        return item

    def remove_item(self, db: Session, cart_id: uuid.UUID, item_id: uuid.UUID) -> bool:
        """
        Remove an item from a cart.
        """
        item = db.query(CartItem).filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart_id
        ).first()

        if not item:
            return False

        db.delete(item)
        db.commit()

        return True

    def clear_items(self, db: Session, cart_id: uuid.UUID) -> bool:
        """
        Remove all items from a cart.
        """
        db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
        db.commit()

        return True

    def merge_carts(self, db: Session, source_cart_id: uuid.UUID, target_cart_id: uuid.UUID) -> Cart:
        """
        Merge items from source cart into target cart.
        """
        source_cart = self.get_with_items(db, cart_id=source_cart_id)
        target_cart = self.get_with_items(db, cart_id=target_cart_id)

        if not source_cart or not target_cart:
            raise ValueError("Source or target cart not found")

        # Process each item in source cart
        for item in source_cart.items:
            # Check if the same item exists in the target cart
            existing_item = db.query(CartItem).filter(
                CartItem.cart_id == target_cart_id,
                CartItem.product_id == item.product_id,
                CartItem.variant_id == item.variant_id
            ).first()

            if existing_item:
                # Update quantity of existing item
                existing_item.quantity += item.quantity
                db.add(existing_item)
            else:
                # Create new item in target cart
                new_item = CartItem(
                    cart_id=target_cart_id,
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    item_metadata=item.item_metadata,
                )
                db.add(new_item)

        # Deactivate source cart
        source_cart.is_active = False
        db.add(source_cart)

        db.commit()
        db.refresh(target_cart)

        return target_cart

    def update_last_activity(self, db: Session, cart_id: uuid.UUID) -> Cart:
        """
        Update the last activity timestamp of a cart.
        """
        from app.utils.datetime_utils import utcnow
        
        cart = self.get(db, id=cart_id)
        if not cart:
            raise ValueError("Cart not found")

        cart.last_activity = utcnow()
        db.add(cart)
        db.commit()
        db.refresh(cart)

        return cart


cart_repository = CartRepository(Cart)
