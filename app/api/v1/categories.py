from typing import Any, List

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_active_superuser,
)
from app.api.dependencies.pagination import PaginationParams, get_pagination
from app.db.session import get_db
from app.models.user import User
from app.schemas.category import (
    Category,
    CategoryCreate,
    CategoryUpdate,
    CategoryList,
    CategoryTree,
    CategoryWithParent,
)
from app.schemas.product import ProductList
from app.services.category import category_service
from app.services.product import product_service

router = APIRouter()


@router.get("", response_model=CategoryList)
def read_categories(
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
) -> Any:
    """
    Get all categories with pagination.
    """
    categories = category_service.get_all(db, skip=pagination.skip, limit=pagination.size)
    total = len(categories)  # For simplicity, not using count query

    return {
        "items": categories,
        "total": total,
    }


@router.get("/tree", response_model=CategoryTree)
def read_category_tree(
        db: Session = Depends(get_db),
) -> Any:
    """
    Get the complete category tree.
    """
    categories = category_service.get_category_tree(db)

    return {
        "items": categories,
    }


@router.get("/root", response_model=List[Category])
def read_root_categories(
        db: Session = Depends(get_db),
) -> Any:
    """
    Get all root categories (with no parent).
    """
    return category_service.get_root_categories(db)


@router.get("/{category_id}", response_model=CategoryWithParent)
def read_category(
        *,
        db: Session = Depends(get_db),
        category_id: str = Path(..., description="The category ID"),
) -> Any:
    """
    Get a specific category by ID.
    """
    return category_service.get_by_id(db, category_id=category_id)


@router.get("/slug/{slug}", response_model=CategoryWithParent)
def read_category_by_slug(
        *,
        db: Session = Depends(get_db),
        slug: str = Path(..., description="The category slug"),
) -> Any:
    """
    Get a specific category by slug.
    """
    return category_service.get_by_slug(db, slug=slug)


@router.get("/{category_id}/children", response_model=List[Category])
def read_category_children(
        *,
        db: Session = Depends(get_db),
        category_id: str = Path(..., description="The category ID"),
) -> Any:
    """
    Get children of a specific category.
    """
    category = category_service.get_with_children(db, category_id=category_id)
    return category.children


@router.get("/slug/{slug}/children", response_model=List[Category])
def read_category_children_by_slug(
        *,
        db: Session = Depends(get_db),
        slug: str = Path(..., description="The category slug"),
) -> Any:
    """
    Get children of a specific category by slug.
    """
    category = category_service.get_by_slug_with_children(db, slug=slug)
    return category.children


@router.get("/{category_id}/products", response_model=ProductList)
def read_category_products(
        *,
        db: Session = Depends(get_db),
        category_id: str = Path(..., description="The category ID"),
        pagination: PaginationParams = Depends(get_pagination),
) -> Any:
    """
    Get products in a specific category.
    """
    products, total = product_service.get_by_category(
        db, category_id=category_id, page=pagination.page, size=pagination.size
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


@router.post("", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
        *,
        db: Session = Depends(get_db),
        category_in: CategoryCreate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create a new category. Only for superusers.
    """
    return category_service.create(db, category_in=category_in)


@router.put("/{category_id}", response_model=Category)
def update_category(
        *,
        db: Session = Depends(get_db),
        category_id: str = Path(..., description="The category ID"),
        category_in: CategoryUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a category. Only for superusers.
    """
    return category_service.update(db, category_id=category_id, category_in=category_in)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
        *,
        db: Session = Depends(get_db),
        category_id: str = Path(..., description="The category ID"),
        current_user: User = Depends(get_current_active_superuser),
) -> None:
    """
    Delete a category. Only for superusers.
    """
    category_service.delete(db, category_id=category_id)
