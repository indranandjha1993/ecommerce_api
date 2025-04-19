"""
Inventory repository for data access operations.
"""
import uuid
from typing import List, Optional, Tuple, Any

from sqlalchemy.orm import Session, joinedload

from app.models.inventory import Inventory, InventoryLocation, StockMovement, StockMovementType
from app.repositories.base import BaseRepository
from app.schemas.inventory import (
    InventoryUpdate,
    InventoryLocationCreate,
    InventoryLocationUpdate,
    StockMovementCreate
)


class InventoryRepository(BaseRepository[Inventory, Any, InventoryUpdate]):
    """
    Inventory repository for data access operations.
    """

    def get_with_relations(self, db: Session, id: uuid.UUID) -> Optional[Inventory]:
        """
        Get an inventory record by ID with related entities.
        """
        return (
            db.query(Inventory)
            .filter(Inventory.id == id)
            .options(
                joinedload(Inventory.product),
                joinedload(Inventory.variant),
                joinedload(Inventory.location),
                joinedload(Inventory.stock_movements)
            )
            .first()
        )

    def get_by_product(
            self, db: Session, product_id: uuid.UUID, variant_id: Optional[uuid.UUID] = None
    ) -> Optional[Inventory]:
        """
        Get inventory for a specific product and variant.
        """
        query = db.query(Inventory).filter(Inventory.product_id == product_id)

        if variant_id:
            query = query.filter(Inventory.variant_id == variant_id)
        else:
            query = query.filter(Inventory.variant_id.is_(None))

        return query.first()

    def get_low_stock_items(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Inventory], int]:
        """
        Get inventory items with low stock.
        """
        query = (
            db.query(Inventory)
            .filter(Inventory.quantity <= Inventory.reorder_point)
            .filter(Inventory.reorder_point.isnot(None))
            .options(
                joinedload(Inventory.product),
                joinedload(Inventory.variant),
                joinedload(Inventory.location)
            )
        )

        total = query.count()
        items = query.offset(skip).limit(limit).all()

        return items, total

    def get_out_of_stock_items(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Inventory], int]:
        """
        Get inventory items that are out of stock.
        """
        query = (
            db.query(Inventory)
            .filter(Inventory.quantity == 0)
            .options(
                joinedload(Inventory.product),
                joinedload(Inventory.variant),
                joinedload(Inventory.location)
            )
        )

        total = query.count()
        items = query.offset(skip).limit(limit).all()

        return items, total

    def get_by_location(
            self, db: Session, location_id: uuid.UUID, *, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Inventory], int]:
        """
        Get inventory items at a specific location.
        """
        query = (
            db.query(Inventory)
            .filter(Inventory.location_id == location_id)
            .options(
                joinedload(Inventory.product),
                joinedload(Inventory.variant)
            )
        )

        total = query.count()
        items = query.offset(skip).limit(limit).all()

        return items, total

    def update_quantity(
            self, db: Session, inventory_id: uuid.UUID, quantity: int
    ) -> Inventory:
        """
        Update an inventory item's quantity.
        """
        inventory = self.get(db, id=inventory_id)
        if not inventory:
            raise ValueError("Inventory not found")

        inventory.quantity = quantity
        db.add(inventory)
        db.commit()
        db.refresh(inventory)

        return inventory

    def adjust_quantity(
            self, db: Session, inventory_id: uuid.UUID, change: int,
            movement_type: StockMovementType, reference_id: Optional[uuid.UUID] = None,
            reference_type: Optional[str] = None, notes: Optional[str] = None,
            user_id: Optional[uuid.UUID] = None
    ) -> Tuple[Inventory, StockMovement]:
        """
        Adjust an inventory item's quantity with a stock movement record.
        """
        inventory = self.get(db, id=inventory_id)
        if not inventory:
            raise ValueError("Inventory not found")

        # Update quantity
        inventory.quantity += change

        # Ensure quantity doesn't go below 0
        if inventory.quantity < 0:
            inventory.quantity = 0

        # Create stock movement record
        stock_movement = StockMovement(
            inventory_id=inventory_id,
            quantity=change,
            movement_type=movement_type,
            reference_id=reference_id,
            reference_type=reference_type,
            notes=notes,
            user_id=user_id
        )

        db.add(inventory)
        db.add(stock_movement)
        db.commit()
        db.refresh(inventory)
        db.refresh(stock_movement)

        return inventory, stock_movement

    def reserve_stock(
            self, db: Session, inventory_id: uuid.UUID, quantity: int,
            order_id: Optional[uuid.UUID] = None, notes: Optional[str] = None
    ) -> Inventory:
        """
        Reserve stock for an order.
        """
        inventory = self.get(db, id=inventory_id)
        if not inventory:
            raise ValueError("Inventory not found")

        if inventory.available_quantity < quantity:
            raise ValueError("Not enough stock available")

        # Update reserved quantity
        inventory.reserved_quantity += quantity

        # Create stock movement record
        stock_movement = StockMovement(
            inventory_id=inventory_id,
            quantity=quantity,
            movement_type=StockMovementType.RESERVED,
            reference_id=order_id,
            reference_type="order" if order_id else None,
            notes=notes
        )

        db.add(inventory)
        db.add(stock_movement)
        db.commit()
        db.refresh(inventory)

        return inventory

    def release_reserved_stock(
            self, db: Session, inventory_id: uuid.UUID, quantity: int,
            order_id: Optional[uuid.UUID] = None, notes: Optional[str] = None
    ) -> Inventory:
        """
        Release previously reserved stock.
        """
        inventory = self.get(db, id=inventory_id)
        if not inventory:
            raise ValueError("Inventory not found")

        # Update reserved quantity
        inventory.reserved_quantity -= quantity

        # Ensure reserved quantity doesn't go below 0
        if inventory.reserved_quantity < 0:
            inventory.reserved_quantity = 0

        # Create stock movement record
        stock_movement = StockMovement(
            inventory_id=inventory_id,
            quantity=quantity,
            movement_type=StockMovementType.RELEASED,
            reference_id=order_id,
            reference_type="order" if order_id else None,
            notes=notes
        )

        db.add(inventory)
        db.add(stock_movement)
        db.commit()
        db.refresh(inventory)

        return inventory

    def get_stock_movements(
            self, db: Session, inventory_id: uuid.UUID,
            *, skip: int = 0, limit: int = 100
    ) -> Tuple[List[StockMovement], int]:
        """
        Get stock movements for an inventory item.
        """
        query = (
            db.query(StockMovement)
            .filter(StockMovement.inventory_id == inventory_id)
            .order_by(StockMovement.created_at.desc())
        )

        total = query.count()
        movements = query.offset(skip).limit(limit).all()

        return movements, total

    def create_stock_movement(
            self, db: Session, movement_in: StockMovementCreate
    ) -> StockMovement:
        """
        Create a stock movement record.
        """
        stock_movement = StockMovement(
            inventory_id=movement_in.inventory_id,
            quantity=movement_in.quantity,
            movement_type=movement_in.movement_type,
            reference_id=movement_in.reference_id,
            reference_type=movement_in.reference_type,
            notes=movement_in.notes,
            user_id=movement_in.user_id
        )

        db.add(stock_movement)
        db.commit()
        db.refresh(stock_movement)

        return stock_movement


class InventoryLocationRepository(BaseRepository[InventoryLocation, InventoryLocationCreate, InventoryLocationUpdate]):
    """
    Inventory location repository for data access operations.
    """

    def get_with_inventory(
            self, db: Session, id: uuid.UUID
    ) -> Optional[InventoryLocation]:
        """
        Get an inventory location with its inventory items.
        """
        return (
            db.query(InventoryLocation)
            .filter(InventoryLocation.id == id)
            .options(
                joinedload(InventoryLocation.inventory_items)
                .joinedload(Inventory.product)
            )
            .first()
        )

    def get_by_code(self, db: Session, code: str) -> Optional[InventoryLocation]:
        """
        Get an inventory location by code.
        """
        return db.query(InventoryLocation).filter(InventoryLocation.code == code).first()

    def create_with_code_check(
            self, db: Session, obj_in: InventoryLocationCreate
    ) -> InventoryLocation:
        """
        Create an inventory location with code uniqueness check.
        """
        existing_location = self.get_by_code(db, code=obj_in.code)
        if existing_location:
            raise ValueError(f"Location with code '{obj_in.code}' already exists")

        db_obj = InventoryLocation(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj


inventory_repository = InventoryRepository(Inventory)
inventory_location_repository = InventoryLocationRepository(InventoryLocation)
