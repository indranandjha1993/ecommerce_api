from typing import Any, List

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_active_superuser,
)
from app.api.dependencies.pagination import PaginationParams, get_pagination
from app.db.session import get_db
from app.models.user import User
from app.schemas.brand import (
    Brand,
    BrandCreate,
    BrandUpdate,
    BrandList,
)
from app.schemas.product import ProductList
from app.services.brand import brand_service
from app.services.product import product_service

router = APIRouter()


@router.get("", response_model=BrandList)
def read_brands(
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
) -> Any:
    """
    Get all brands with pagination.
    """
    brands, total = brand_service.get_all(db, skip=pagination.skip, limit=pagination.size)

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": brands,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }


@router.get("/featured", response_model=List[Brand])
def read_featured_brands(
        db: Session = Depends(get_db),
        limit: int = Query(10, description="Number of brands to return"),
) -> Any:
    """
    Get featured brands.
    """
    return brand_service.get_featured_brands(db, limit=limit)


@router.get("/{brand_id}", response_model=Brand)
def read_brand(
        *,
        db: Session = Depends(get_db),
        brand_id: str = Path(..., description="The brand ID"),
) -> Any:
    """
    Get a specific brand by ID.
    """
    return brand_service.get_by_id(db, brand_id=brand_id)


@router.get("/slug/{slug}", response_model=Brand)
def read_brand_by_slug(
        *,
        db: Session = Depends(get_db),
        slug: str = Path(..., description="The brand slug"),
) -> Any:
    """
    Get a specific brand by slug.
    """
    return brand_service.get_by_slug(db, slug=slug)


@router.get("/{brand_id}/products", response_model=ProductList)
def read_brand_products(
        *,
        db: Session = Depends(get_db),
        brand_id: str = Path(..., description="The brand ID"),
        pagination: PaginationParams = Depends(get_pagination),
) -> Any:
    """
    Get products for a specific brand.
    """
    products, total = product_service.get_by_brand(
        db, brand_id=brand_id, page=pagination.page, size=pagination.size
    )

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": products,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }


@router.post("", response_model=Brand, status_code=status.HTTP_201_CREATED)
def create_brand(
        *,
        db: Session = Depends(get_db),
        brand_in: BrandCreate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create a new brand. Only for superusers.
    """
    return brand_service.create(db, brand_in=brand_in)


@router.put("/{brand_id}", response_model=Brand)
def update_brand(
        *,
        db: Session = Depends(get_db),
        brand_id: str = Path(..., description="The brand ID"),
        brand_in: BrandUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a brand. Only for superusers.
    """
    return brand_service.update(db, brand_id=brand_id, brand_in=brand_in)


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(
        *,
        db: Session = Depends(get_db),
        brand_id: str = Path(..., description="The brand ID"),
        current_user: User = Depends(get_current_active_superuser),
) -> None:
    """
    Delete a brand. Only for superusers.
    """
    brand_service.delete(db, brand_id=brand_id)
