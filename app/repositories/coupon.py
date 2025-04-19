import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session, joinedload

from app.models.coupon import Coupon, CouponUsage
from app.repositories.base import BaseRepository
from app.schemas.coupon import CouponCreate, CouponUpdate
from app.utils.datetime_utils import utcnow


class CouponRepository(BaseRepository[Coupon, CouponCreate, CouponUpdate]):
    """
    Coupon repository for data access operations.
    """

    def get_by_code(self, db: Session, code: str) -> Optional[Coupon]:
        """
        Get a coupon by code.
        """
        return db.query(Coupon).filter(Coupon.code == code).first()

    def get_with_usage(self, db: Session, id: uuid.UUID) -> Optional[Coupon]:
        """
        Get a coupon by ID with usage history.
        """
        return (
            db.query(Coupon)
            .filter(Coupon.id == id)
            .options(joinedload(Coupon.usage_history))
            .first()
        )

    def get_by_code_with_usage(self, db: Session, code: str) -> Optional[Coupon]:
        """
        Get a coupon by code with usage history.
        """
        return (
            db.query(Coupon)
            .filter(Coupon.code == code)
            .options(joinedload(Coupon.usage_history))
            .first()
        )

    def get_valid_coupons(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Coupon], int]:
        """
        Get valid coupons with pagination.
        """
        now = utcnow()

        query = (
            db.query(Coupon)
            .filter(Coupon.is_active == True)
            .filter(
                or_(
                    Coupon.starts_at.is_(None),
                    Coupon.starts_at <= now
                )
            )
            .filter(
                or_(
                    Coupon.expires_at.is_(None),
                    Coupon.expires_at > now
                )
            )
            .filter(
                or_(
                    Coupon.usage_limit.is_(None),
                    Coupon.current_usage_count < Coupon.usage_limit
                )
            )
        )

        total = query.count()
        coupons = query.offset(skip).limit(limit).all()

        return coupons, total

    def get_expired_coupons(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Coupon], int]:
        """
        Get expired coupons with pagination.
        """
        now = utcnow()

        query = (
            db.query(Coupon)
            .filter(
                or_(
                    Coupon.is_active == False,
                    and_(
                        Coupon.expires_at.isnot(None),
                        Coupon.expires_at <= now
                    ),
                    and_(
                        Coupon.usage_limit.isnot(None),
                        Coupon.current_usage_count >= Coupon.usage_limit
                    )
                )
            )
        )

        total = query.count()
        coupons = query.offset(skip).limit(limit).all()

        return coupons, total

    def create_with_code_check(self, db: Session, obj_in: CouponCreate) -> Coupon:
        """
        Create a coupon with code uniqueness check.
        """
        # Check if a coupon with this code already exists
        existing_coupon = self.get_by_code(db, code=obj_in.code)
        if existing_coupon:
            raise ValueError(f"A coupon with code '{obj_in.code}' already exists")

        # Create coupon
        return self.create(db, obj_in=obj_in)

    def update_with_code_check(
            self, db: Session, *, db_obj: Coupon, obj_in: CouponUpdate
    ) -> Coupon:
        """
        Update a coupon with code uniqueness check.
        """
        # Check if code is being changed and if it's already in use
        if obj_in.code and obj_in.code != db_obj.code:
            existing_coupon = self.get_by_code(db, code=obj_in.code)
            if existing_coupon and existing_coupon.id != db_obj.id:
                raise ValueError(f"A coupon with code '{obj_in.code}' already exists")

        # Update coupon
        return self.update(db, db_obj=db_obj, obj_in=obj_in)

    def record_usage(
            self, db: Session, coupon_id: uuid.UUID, order_id: uuid.UUID,
            user_id: Optional[uuid.UUID], discount_amount: float
    ) -> CouponUsage:
        """
        Record coupon usage.
        """
        # Get the coupon
        coupon = self.get(db, id=coupon_id)
        if not coupon:
            raise ValueError("Coupon not found")

        # Increment usage count
        coupon.current_usage_count += 1
        db.add(coupon)

        # Create usage record
        usage = CouponUsage(
            coupon_id=coupon_id,
            order_id=order_id,
            user_id=user_id,
            discount_amount=discount_amount
        )
        db.add(usage)
        db.commit()
        db.refresh(usage)

        return usage

    def get_user_usage_count(
            self, db: Session, coupon_id: uuid.UUID, user_id: uuid.UUID
    ) -> int:
        """
        Get the number of times a user has used a coupon.
        """
        return (
            db.query(CouponUsage)
            .filter(
                CouponUsage.coupon_id == coupon_id,
                CouponUsage.user_id == user_id
            )
            .count()
        )


coupon_repository = CouponRepository(Coupon)
