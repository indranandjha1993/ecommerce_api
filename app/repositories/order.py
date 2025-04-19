import uuid
from typing import List, Optional, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.models.order import Order, OrderStatus, PaymentStatus
from app.repositories.base import BaseRepository
from app.schemas.order import OrderCreate, OrderUpdate
from app.utils.datetime_utils import utcnow


class OrderRepository(BaseRepository[Order, OrderCreate, OrderUpdate]):
    """
    Order repository for data access operations.
    """

    def get_with_relations(self, db: Session, id: uuid.UUID) -> Optional[Order]:
        """
        Get an order by ID with related entities.
        """
        return (
            db.query(Order)
            .filter(Order.id == id)
            .options(
                joinedload(Order.items),
                joinedload(Order.shipping_address),
                joinedload(Order.billing_address),
                joinedload(Order.payments),
                joinedload(Order.shipping_details),
            )
            .first()
        )

    def get_by_order_number(self, db: Session, order_number: str) -> Optional[Order]:
        """
        Get an order by order number.
        """
        return db.query(Order).filter(Order.order_number == order_number).first()

    def get_by_order_number_with_relations(self, db: Session, order_number: str) -> Optional[Order]:
        """
        Get an order by order number with related entities.
        """
        return (
            db.query(Order)
            .filter(Order.order_number == order_number)
            .options(
                joinedload(Order.items),
                joinedload(Order.shipping_address),
                joinedload(Order.billing_address),
                joinedload(Order.payments),
                joinedload(Order.shipping_details),
            )
            .first()
        )

    def get_by_guest_token(self, db: Session, guest_token: str) -> Optional[Order]:
        """
        Get an order by guest token.
        """
        return (
            db.query(Order)
            .filter(Order.guest_token == guest_token)
            .options(
                joinedload(Order.items),
                joinedload(Order.shipping_address),
                joinedload(Order.billing_address),
                joinedload(Order.payments),
                joinedload(Order.shipping_details),
            )
            .first()
        )

    def get_user_orders(
            self, db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Order], int]:
        """
        Get orders for a user with pagination.
        """
        query = db.query(Order).filter(Order.user_id == user_id)
        total = query.count()

        orders = (
            query
            .options(joinedload(Order.items))
            .order_by(desc(Order.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return orders, total

    def get_orders_by_status(
            self, db: Session, status: OrderStatus, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Order], int]:
        """
        Get orders by status with pagination.
        """
        query = db.query(Order).filter(Order.status == status)
        total = query.count()

        orders = (
            query
            .options(joinedload(Order.items))
            .order_by(desc(Order.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return orders, total

    def get_orders_by_date_range(
            self, db: Session, start_date, end_date, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Order], int]:
        """
        Get orders within a date range with pagination.
        """
        query = db.query(Order).filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date
        )
        total = query.count()

        orders = (
            query
            .options(joinedload(Order.items))
            .order_by(desc(Order.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return orders, total

    def update_status(
            self, db: Session, order_id: uuid.UUID, status: OrderStatus
    ) -> Order:
        """
        Update an order's status.
        """
        order = self.get(db, id=order_id)
        if not order:
            raise ValueError("Order not found")

        order.status = status

        # If the order is completed, set the completed_at timestamp
        if status == OrderStatus.COMPLETED and not order.completed_at:
            order.completed_at = utcnow()

        db.add(order)
        db.commit()
        db.refresh(order)

        return order

    def update_payment_status(
            self, db: Session, order_id: uuid.UUID, payment_status: PaymentStatus
    ) -> Order:
        """
        Update an order's payment status.
        """
        order = self.get(db, id=order_id)
        if not order:
            raise ValueError("Order not found")

        order.payment_status = payment_status
        db.add(order)
        db.commit()
        db.refresh(order)

        return order

    def generate_order_number(self, db: Session) -> str:
        """
        Generate a unique order number.
        """

        # Get the current timestamp
        now = utcnow()
        date_part = now.strftime("%Y%m%d")

        # Get the current highest order number for today
        latest_order = (
            db.query(Order)
            .filter(Order.order_number.like(f"{date_part}%"))
            .order_by(desc(Order.order_number))
            .first()
        )

        if latest_order:
            # Extract the sequence number from the latest order
            try:
                seq_num = int(latest_order.order_number[8:]) + 1
            except ValueError:
                seq_num = 1
        else:
            seq_num = 1

        # Format: YYYYMMDD-XXXX (e.g., 20240418-0001)
        order_number = f"{date_part}-{seq_num:04d}"

        return order_number


order_repository = OrderRepository(Order)
