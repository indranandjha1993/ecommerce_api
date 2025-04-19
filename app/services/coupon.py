import uuid
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any

from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.models.coupon import Coupon, DiscountType
from app.repositories.coupon import coupon_repository
from app.schemas.coupon import CouponCreate, CouponUpdate
from app.utils.datetime_utils import utcnow


class CouponService:
    """
    Coupon service for business logic.
    """
    
    def _normalize_datetime(self, dt):
        """Normalize datetime for comparison by removing timezone info."""
        if dt is None:
            return None
        if dt.tzinfo:
            return dt.replace(tzinfo=None)
        return dt

    def get_by_id(self, db: Session, coupon_id: uuid.UUID) -> Coupon:
        """
        Get a coupon by ID.
        """
        coupon = coupon_repository.get_with_usage(db, id=coupon_id)
        if not coupon:
            raise NotFoundException(detail="Coupon not found")
        return coupon

    def get_by_code(self, db: Session, code: str) -> Coupon:
        """
        Get a coupon by code.
        """
        coupon = coupon_repository.get_by_code_with_usage(db, code=code)
        if not coupon:
            raise NotFoundException(detail="Coupon not found")
        return coupon

    def get_all(
            self, db: Session, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Coupon], int]:
        """
        Get all coupons with pagination.
        """
        coupons = coupon_repository.get_multi(db, skip=skip, limit=limit)
        total = coupon_repository.get_count(db)
        return coupons, total

    def get_valid_coupons(
            self, db: Session, page: int = 1, size: int = 20
    ) -> Tuple[List[Coupon], int]:
        """
        Get valid coupons with pagination.
        """
        skip = (page - 1) * size
        return coupon_repository.get_valid_coupons(db, skip=skip, limit=size)

    def get_expired_coupons(
            self, db: Session, page: int = 1, size: int = 20
    ) -> Tuple[List[Coupon], int]:
        """
        Get expired coupons with pagination.
        """
        skip = (page - 1) * size
        return coupon_repository.get_expired_coupons(db, skip=skip, limit=size)

    def create(self, db: Session, coupon_in: CouponCreate) -> Coupon:
        """
        Create a new coupon.
        """
        # Validate percentage discount
        if coupon_in.discount_type == DiscountType.PERCENTAGE and coupon_in.discount_value > 100:
            raise BadRequestException(detail="Percentage discount cannot exceed 100%")
        
        # Validate negative discount
        if coupon_in.discount_value < 0:
            raise BadRequestException(detail="Discount value cannot be negative")
            
        try:
            return coupon_repository.create_with_code_check(db, obj_in=coupon_in)
        except ValueError as e:
            raise BadRequestException(detail=str(e))

    def update(self, db: Session, coupon_id: uuid.UUID, coupon_in: CouponUpdate) -> Coupon:
        """
        Update a coupon.
        """
        coupon = coupon_repository.get(db, id=coupon_id)
        if not coupon:
            raise NotFoundException(detail="Coupon not found")

        try:
            return coupon_repository.update_with_code_check(db, db_obj=coupon, obj_in=coupon_in)
        except ValueError as e:
            raise BadRequestException(detail=str(e))

    def delete(self, db: Session, coupon_id: uuid.UUID) -> None:
        """
        Delete a coupon.
        """
        coupon = coupon_repository.get(db, id=coupon_id)
        if not coupon:
            raise NotFoundException(detail="Coupon not found")

        # Check if coupon has been used
        if coupon.current_usage_count > 0:
            raise BadRequestException(detail="Cannot delete a coupon that has been used")

        coupon_repository.remove(db, id=coupon_id)

    def validate_coupon(
            self,
            db: Session,
            code: str,
            user_id: Optional[uuid.UUID] = None,
            order_total: Optional[Decimal] = None,
            items: Optional[List[Dict[str, Any]]] = None
    ) -> Coupon:
        """
        Validate a coupon for use.
        """
        coupon = self.get_by_code(db, code=code)

        # Check if coupon is active
        if not coupon.is_active:
            raise BadRequestException(detail="This coupon is inactive")

        # Check start date
        now = self._normalize_datetime(utcnow())
        if coupon.starts_at:
            starts_at = self._normalize_datetime(coupon.starts_at)
            if starts_at > now:
                raise BadRequestException(detail="This coupon is not yet active")

        # Check expiry date
        if coupon.expires_at:
            expires_at = self._normalize_datetime(coupon.expires_at)
            if expires_at < now:
                raise BadRequestException(detail="This coupon has expired")

        # Check usage limit
        if coupon.usage_limit and coupon.current_usage_count >= coupon.usage_limit:
            raise BadRequestException(detail="This coupon has reached its usage limit")

        # Check user-specific restrictions
        if user_id:
            # Check if coupon is restricted to specific users
            if not coupon.applies_to_all_customers and coupon.customer_ids:
                if str(user_id) not in [str(cid) for cid in coupon.customer_ids]:
                    raise BadRequestException(detail="This coupon is not available for your account")

            # Check user usage limit
            if coupon.usage_limit_per_user:
                usage_count = coupon_repository.get_user_usage_count(db, coupon_id=coupon.id, user_id=user_id)
                if usage_count >= coupon.usage_limit_per_user:
                    raise BadRequestException(detail="You have reached the usage limit for this coupon")

            # Check first-order only
            if coupon.is_first_order_only:
                # Check if user has any previous orders
                from app.models.order import Order
                previous_orders = db.query(Order).filter(Order.user_id == user_id).count()
                if previous_orders > 0:
                    raise BadRequestException(detail="This coupon is only valid for first orders")

        # Check minimum order requirements
        if coupon.minimum_order_amount and order_total:
            if order_total < coupon.minimum_order_amount:
                raise BadRequestException(
                    detail=f"Order total must be at least {coupon.minimum_order_amount} to use this coupon"
                )

        # Check minimum quantity requirement
        if coupon.minimum_quantity and items:
            total_quantity = sum(item.get("quantity", 0) for item in items)
            if total_quantity < coupon.minimum_quantity:
                raise BadRequestException(
                    detail=f"You must add at least {coupon.minimum_quantity} items to use this coupon"
                )

        # Check product and category restrictions
        if items and not coupon.applies_to_all_products:
            # Get product IDs from items
            product_ids = [str(item.get("product_id")) for item in items if "product_id" in item]

            # Get category IDs from products
            from app.models.product import Product
            products = db.query(Product).filter(Product.id.in_(product_ids)).all()
            category_ids = [str(product.category_id) for product in products if product.category_id]

            # Check product inclusions
            if coupon.product_ids and not any(pid in coupon.product_ids for pid in product_ids):
                raise BadRequestException(detail="This coupon does not apply to any items in your cart")

            # Check category inclusions
            if coupon.category_ids and not any(cid in coupon.category_ids for cid in category_ids):
                raise BadRequestException(detail="This coupon does not apply to any items in your cart")

            # Check product exclusions
            if coupon.exclude_product_ids and all(pid in coupon.exclude_product_ids for pid in product_ids):
                raise BadRequestException(detail="This coupon does not apply to any items in your cart")

            # Check category exclusions
            if coupon.exclude_category_ids and all(cid in coupon.exclude_category_ids for cid in category_ids):
                raise BadRequestException(detail="This coupon does not apply to any items in your cart")

        return coupon

    def calculate_discount(
            self,
            coupon: Coupon,
            order_total: Decimal,
            items: Optional[List[Dict[str, Any]]] = None
    ) -> Decimal:
        """
        Calculate the discount amount for a coupon.
        """
        if coupon.discount_type == DiscountType.PERCENTAGE:
            return (order_total * Decimal(coupon.discount_value) / Decimal(100)).quantize(Decimal("0.01"))

        elif coupon.discount_type == DiscountType.FIXED_AMOUNT:
            return min(order_total, Decimal(coupon.discount_value)).quantize(Decimal("0.01"))

        elif coupon.discount_type == DiscountType.FREE_SHIPPING:
            # This would need additional shipping cost information
            # For now, return 0
            return Decimal("0.00")

        elif coupon.discount_type == DiscountType.BUY_X_GET_Y and items:
            # This is a simplified calculation for buy X get Y
            # A more complex implementation would need to consider specific products
            if not coupon.buy_quantity or not coupon.get_quantity:
                return Decimal("0.00")

            # Calculate how many "free" items qualify
            total_quantity = sum(item.get("quantity", 0) for item in items)
            sets = total_quantity // (coupon.buy_quantity + coupon.get_quantity)

            if sets <= 0:
                return Decimal("0.00")

            # Calculate average price of items
            total_price = sum(
                Decimal(str(item.get("unit_price", 0))) * Decimal(str(item.get("quantity", 0)))
                for item in items
            )
            avg_price = total_price / Decimal(total_quantity)

            # Discount for Y items in each set
            return (Decimal(sets) * Decimal(coupon.get_quantity) * avg_price).quantize(Decimal("0.01"))

        return Decimal("0.00")

    def apply_coupon(
            self,
            db: Session,
            code: str,
            order_id: uuid.UUID,
            user_id: Optional[uuid.UUID] = None,
            order_total: Decimal = Decimal("0.00"),
            items: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[Coupon, Decimal]:
        """
        Apply a coupon to an order and record its usage.
        """
        # Validate coupon
        coupon = self.validate_coupon(
            db, code=code, user_id=user_id, order_total=order_total, items=items
        )

        # Calculate discount
        discount_amount = self.calculate_discount(coupon, order_total, items)

        # Record coupon usage
        coupon_repository.record_usage(
            db,
            coupon_id=coupon.id,
            order_id=order_id,
            user_id=user_id,
            discount_amount=float(discount_amount)
        )

        return coupon, discount_amount


coupon_service = CouponService()
