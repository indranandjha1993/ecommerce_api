from typing import Any, Optional

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_active_superuser,
)
from app.api.dependencies.pagination import PaginationParams, get_pagination
from app.core.exceptions import NotFoundException, BadRequestException
from app.db.session import get_db
from app.models.inventory import StockMovementType
from app.models.user import User
from app.schemas.inventory import (
    Inventory,
    InventoryUpdate,
    InventoryList,
    InventoryLocation,
    InventoryLocationCreate,
    InventoryLocationUpdate,
    InventoryLocationList,
    StockMovement,
    StockMovementCreate,
    StockMovementList,
    InventoryAdjustment,
    InventoryReservation, InventoryCreate,
)
from app.services.inventory import inventory_service

router = APIRouter()


# Inventory endpoints
@router.post("", response_model=Inventory, status_code=status.HTTP_201_CREATED)
def create_inventory(
        *,
        db: Session = Depends(get_db),
        inventory_in: InventoryCreate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create inventory for a product. Only for superusers.
    """
    # Check if product exists
    from app.models.product import Product
    product = db.query(Product).filter(Product.id == inventory_in.product_id).first()
    if not product:
        raise NotFoundException(detail="Product not found")
    
    # Check if inventory already exists for this product/variant
    # Use the repository directly to avoid the NotFoundException
    from app.repositories.inventory import inventory_repository
    existing_inventory = inventory_repository.get_by_product(
        db, product_id=inventory_in.product_id, variant_id=inventory_in.variant_id
    )
    
    if existing_inventory:
        raise BadRequestException(detail="Inventory already exists for this product/variant")
    
    # Create inventory
    from app.models.inventory import Inventory
    inventory = Inventory(**inventory_in.model_dump())
    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    
    # Get the inventory with relations for the response
    inventory_with_relations = inventory_service.get_by_id(db, inventory_id=inventory.id)
    
    return inventory_with_relations

@router.get("/product/{product_id}", response_model=Inventory)
def read_product_inventory(
        *,
        db: Session = Depends(get_db),
        product_id: str = Path(..., description="The product ID"),
        variant_id: Optional[str] = Query(None, description="The variant ID"),
) -> Any:
    """
    Get inventory for a specific product.
    """
    return inventory_service.get_by_product(
        db, product_id=product_id, variant_id=variant_id
    )


@router.get("/low-stock", response_model=InventoryList)
def read_low_stock_items(
        *,
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get inventory items with low stock. Only for superusers.
    """
    items, total = inventory_service.get_low_stock_items(
        db, page=pagination.page, size=pagination.size
    )

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": items,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }


@router.get("/out-of-stock", response_model=InventoryList)
def read_out_of_stock_items(
        *,
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get inventory items that are out of stock. Only for superusers.
    """
    items, total = inventory_service.get_out_of_stock_items(
        db, page=pagination.page, size=pagination.size
    )

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": items,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }


@router.get("/{inventory_id}", response_model=Inventory)
def read_inventory(
        *,
        db: Session = Depends(get_db),
        inventory_id: str = Path(..., description="The inventory ID"),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get a specific inventory record by ID. Only for superusers.
    """
    return inventory_service.get_by_id(db, inventory_id=inventory_id)


@router.put("/{inventory_id}", response_model=Inventory)
def update_inventory(
        *,
        db: Session = Depends(get_db),
        inventory_id: str = Path(..., description="The inventory ID"),
        inventory_in: InventoryUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update an inventory record. Only for superusers.
    """
    inventory = inventory_service.get_by_id(db, inventory_id=inventory_id)

    # If quantity is being updated, use the dedicated method
    if inventory_in.quantity is not None and inventory_in.quantity != inventory.quantity:
        return inventory_service.update_quantity(
            db,
            inventory_id=inventory_id,
            quantity=inventory_in.quantity,
            user_id=current_user.id,
            notes="Quantity updated via admin API"
        )

    # Otherwise, use the generic update method
    from app.repositories.inventory import inventory_repository
    return inventory_repository.update(db, db_obj=inventory, obj_in=inventory_in)


@router.post("/{inventory_id}/adjust", response_model=Inventory)
def adjust_inventory(
        *,
        db: Session = Depends(get_db),
        inventory_id: str = Path(..., description="The inventory ID"),
        adjustment: InventoryAdjustment,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Adjust inventory quantity. Only for superusers.
    """
    # Check if adjustment would result in negative quantity
    inventory = inventory_service.get_by_id(db, inventory_id=inventory_id)
    if inventory.quantity + adjustment.adjustment < 0:
        from app.core.exceptions import BadRequestException
        raise BadRequestException(detail="Cannot adjust inventory to a negative quantity")
    
    inventory, _ = inventory_service.adjust_quantity(
        db,
        inventory_id=inventory_id,
        change=adjustment.adjustment,
        movement_type=StockMovementType.ADJUSTMENT,
        notes=adjustment.reason,
        user_id=current_user.id
    )
    return inventory


@router.post("/{inventory_id}/reserve", response_model=Inventory)
def reserve_inventory(
        *,
        db: Session = Depends(get_db),
        inventory_id: str = Path(..., description="The inventory ID"),
        reservation: InventoryReservation,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Reserve inventory. Only for superusers.
    """
    return inventory_service.reserve_stock(
        db,
        inventory_id=inventory_id,
        quantity=reservation.quantity,
        order_id=reservation.order_id,
        notes=reservation.notes
    )


@router.post("/{inventory_id}/release", response_model=Inventory)
def release_inventory(
        *,
        db: Session = Depends(get_db),
        inventory_id: str = Path(..., description="The inventory ID"),
        reservation: InventoryReservation,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Release reserved inventory. Only for superusers.
    """
    return inventory_service.release_reserved_stock(
        db,
        inventory_id=inventory_id,
        quantity=reservation.quantity,
        order_id=reservation.order_id,
        notes=reservation.notes
    )


@router.get("/{inventory_id}/movements", response_model=StockMovementList)
def read_stock_movements(
        *,
        db: Session = Depends(get_db),
        inventory_id: str = Path(..., description="The inventory ID"),
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get stock movements for an inventory item. Only for superusers.
    """
    movements, total = inventory_service.get_stock_movements(
        db, inventory_id=inventory_id, page=pagination.page, size=pagination.size
    )

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": movements,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }


@router.post("/movements", response_model=StockMovement, status_code=status.HTTP_201_CREATED)
def create_stock_movement(
        *,
        db: Session = Depends(get_db),
        movement_in: StockMovementCreate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create a stock movement record. Only for superusers.
    """
    movement_data = movement_in.model_dump()

    # Add user ID if not provided
    if not movement_data.get("user_id"):
        movement_data["user_id"] = current_user.id

    return inventory_service.create_stock_movement(
        db, movement_in=StockMovementCreate(**movement_data)
    )


# Location endpoints
@router.get("/locations", response_model=InventoryLocationList)
def read_inventory_locations(
        *,
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get all inventory locations. Only for superusers.
    """
    locations = inventory_service.get_all_locations(db, skip=pagination.skip, limit=pagination.size)
    total = len(locations)  # Simple count for now

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": locations,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }


@router.post("/locations", response_model=InventoryLocation, status_code=status.HTTP_201_CREATED)
def create_inventory_location(
        *,
        db: Session = Depends(get_db),
        location_in: InventoryLocationCreate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create a new inventory location. Only for superusers.
    """
    return inventory_service.create_location(db, location_in=location_in)


@router.get("/locations/{location_id}", response_model=InventoryLocation)
def read_inventory_location(
        *,
        db: Session = Depends(get_db),
        location_id: str = Path(..., description="The location ID"),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get a specific inventory location by ID. Only for superusers.
    """
    return inventory_service.get_location_by_id(db, location_id=location_id)


@router.put("/locations/{location_id}", response_model=InventoryLocation)
def update_inventory_location(
        *,
        db: Session = Depends(get_db),
        location_id: str = Path(..., description="The location ID"),
        location_in: InventoryLocationUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update an inventory location. Only for superusers.
    """
    return inventory_service.update_location(
        db, location_id=location_id, location_in=location_in
    )


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_location(
        *,
        db: Session = Depends(get_db),
        location_id: str = Path(..., description="The location ID"),
        current_user: User = Depends(get_current_active_superuser),
) -> None:
    """
    Delete an inventory location. Only for superusers.
    """
    inventory_service.delete_location(db, location_id=location_id)


@router.get("/locations/{location_id}/inventory", response_model=InventoryList)
def read_location_inventory(
        *,
        db: Session = Depends(get_db),
        location_id: str = Path(..., description="The location ID"),
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get inventory items at a specific location. Only for superusers.
    """
    items, total = inventory_service.get_inventory_by_location(
        db, location_id=location_id, page=pagination.page, size=pagination.size
    )

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": items,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }
