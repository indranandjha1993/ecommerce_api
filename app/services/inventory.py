import uuid
from typing import List, Optional, Tuple

from app.schemas.inventory import (
    InventoryUpdate,
    InventoryLocationCreate,
    InventoryLocationUpdate,
    StockMovementCreate
)
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.models.inventory import Inventory, InventoryLocation, StockMovement, StockMovementType
from app.repositories.inventory import inventory_repository, inventory_location_repository


class InventoryService:
    """
    Inventory service for business logic.
    """

    def get_by_id(self, db: Session, inventory_id: uuid.UUID) -> Inventory:
        """
        Get an inventory record by ID.
        """
        inventory = inventory_repository.get_with_relations(db, id=inventory_id)
        if not inventory:
            raise NotFoundException(detail="Inventory not found")
        return inventory

    def get_by_product(
            self, db: Session, product_id: uuid.UUID, variant_id: Optional[uuid.UUID] = None
    ) -> Inventory:
        """
        Get inventory for a specific product and variant.
        """
        inventory = inventory_repository.get_by_product(
            db, product_id=product_id, variant_id=variant_id
        )
        if not inventory:
            raise NotFoundException(detail="Inventory not found for this product")
        return inventory

    def get_low_stock_items(
            self, db: Session, page: int = 1, size: int = 20
    ) -> Tuple[List[Inventory], int]:
        """
        Get inventory items with low stock.
        """
        skip = (page - 1) * size
        return inventory_repository.get_low_stock_items(db, skip=skip, limit=size)

    def get_out_of_stock_items(
            self, db: Session, page: int = 1, size: int = 20
    ) -> Tuple[List[Inventory], int]:
        """
        Get inventory items that are out of stock.
        """
        skip = (page - 1) * size
        return inventory_repository.get_out_of_stock_items(db, skip=skip, limit=size)

    def update_quantity(
            self, db: Session, inventory_id: uuid.UUID, quantity: int,
            user_id: Optional[uuid.UUID] = None, notes: Optional[str] = None
    ) -> Inventory:
        """
        Update an inventory item's quantity.
        """
        inventory = inventory_repository.get(db, id=inventory_id)
        if not inventory:
            raise NotFoundException(detail="Inventory not found")

        # Calculate the change in quantity
        change = quantity - inventory.quantity

        # If there's no change, return the inventory
        if change == 0:
            return inventory

        # Determine the movement type
        movement_type = StockMovementType.ADJUSTMENT
        if change > 0:
            movement_type = StockMovementType.RECEIPT

        # Adjust the quantity with a stock movement record
        inventory, _ = inventory_repository.adjust_quantity(
            db,
            inventory_id=inventory_id,
            change=change,
            movement_type=movement_type,
            notes=notes,
            user_id=user_id
        )

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
        try:
            inventory, stock_movement = inventory_repository.adjust_quantity(
                db,
                inventory_id=inventory_id,
                change=change,
                movement_type=movement_type,
                reference_id=reference_id,
                reference_type=reference_type,
                notes=notes,
                user_id=user_id
            )
            return inventory, stock_movement
        except ValueError as e:
            raise NotFoundException(detail=str(e))

    def reserve_stock(
            self, db: Session, inventory_id: uuid.UUID, quantity: int,
            order_id: Optional[uuid.UUID] = None, notes: Optional[str] = None
    ) -> Inventory:
        """
        Reserve stock for an order.
        """
        try:
            return inventory_repository.reserve_stock(
                db,
                inventory_id=inventory_id,
                quantity=quantity,
                order_id=order_id,
                notes=notes
            )
        except ValueError as e:
            raise BadRequestException(detail=str(e))

    def release_reserved_stock(
            self, db: Session, inventory_id: uuid.UUID, quantity: int,
            order_id: Optional[uuid.UUID] = None, notes: Optional[str] = None
    ) -> Inventory:
        """
        Release previously reserved stock.
        """
        try:
            return inventory_repository.release_reserved_stock(
                db,
                inventory_id=inventory_id,
                quantity=quantity,
                order_id=order_id,
                notes=notes
            )
        except ValueError as e:
            raise NotFoundException(detail=str(e))

    def get_stock_movements(
            self, db: Session, inventory_id: uuid.UUID, page: int = 1, size: int = 20
    ) -> Tuple[List[StockMovement], int]:
        """
        Get stock movements for an inventory item.
        """
        inventory = inventory_repository.get(db, id=inventory_id)
        if not inventory:
            raise NotFoundException(detail="Inventory not found")

        skip = (page - 1) * size
        return inventory_repository.get_stock_movements(
            db, inventory_id=inventory_id, skip=skip, limit=size
        )

    def create_stock_movement(
            self, db: Session, movement_in: StockMovementCreate
    ) -> StockMovement:
        """
        Create a stock movement record.
        """
        inventory = inventory_repository.get(db, id=movement_in.inventory_id)
        if not inventory:
            raise NotFoundException(detail="Inventory not found")

        return inventory_repository.create_stock_movement(db, movement_in=movement_in)

    # Inventory Location methods
    def get_location_by_id(self, db: Session, location_id: uuid.UUID) -> InventoryLocation:
        """
        Get an inventory location by ID.
        """
        location = inventory_location_repository.get_with_inventory(db, id=location_id)
        if not location:
            raise NotFoundException(detail="Inventory location not found")
        return location

    def get_location_by_code(self, db: Session, code: str) -> InventoryLocation:
        """
        Get an inventory location by code.
        """
        location = inventory_location_repository.get_by_code(db, code=code)
        if not location:
            raise NotFoundException(detail="Inventory location not found")
        return location

    def get_all_locations(
            self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[InventoryLocation]:
        """
        Get all inventory locations.
        """
        return inventory_location_repository.get_multi(db, skip=skip, limit=limit)

    def create_location(
            self, db: Session, location_in: InventoryLocationCreate
    ) -> InventoryLocation:
        """
        Create a new inventory location.
        """
        try:
            return inventory_location_repository.create_with_code_check(db, obj_in=location_in)
        except ValueError as e:
            raise BadRequestException(detail=str(e))

    def update_location(
            self, db: Session, location_id: uuid.UUID, location_in: InventoryLocationUpdate
    ) -> InventoryLocation:
        """
        Update an inventory location.
        """
        location = inventory_location_repository.get(db, id=location_id)
        if not location:
            raise NotFoundException(detail="Inventory location not found")

        # Check code uniqueness if it's being changed
        if location_in.code and location_in.code != location.code:
            existing_location = inventory_location_repository.get_by_code(db, code=location_in.code)
            if existing_location and existing_location.id != location_id:
                raise BadRequestException(detail=f"Location with code '{location_in.code}' already exists")

        return inventory_location_repository.update(db, db_obj=location, obj_in=location_in)

    def delete_location(self, db: Session, location_id: uuid.UUID) -> None:
        """
        Delete an inventory location.
        """
        location = inventory_location_repository.get_with_inventory(db, id=location_id)
        if not location:
            raise NotFoundException(detail="Inventory location not found")

        # Check if location has inventory items
        if location.inventory_items:
            raise BadRequestException(detail="Cannot delete location with inventory items")

        inventory_location_repository.remove(db, id=location_id)

    def get_inventory_by_location(
            self, db: Session, location_id: uuid.UUID, page: int = 1, size: int = 20
    ) -> Tuple[List[Inventory], int]:
        """
        Get inventory items at a specific location.
        """
        location = inventory_location_repository.get(db, id=location_id)
        if not location:
            raise NotFoundException(detail="Inventory location not found")

        skip = (page - 1) * size
        return inventory_repository.get_by_location(
            db, location_id=location_id, skip=skip, limit=size
        )


inventory_service = InventoryService()
