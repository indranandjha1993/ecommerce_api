from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status, Response, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_active_superuser,
)
from app.api.dependencies.pagination import PaginationParams, get_pagination
from app.core.exceptions import NotFoundException, BadRequestException
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
        response: Response,
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
) -> Any:
    """
    Get all categories with pagination.
    
    Returns a paginated list of all categories in the system.
    Categories are fundamental for organizing products and navigation.
    """
    # Set cache control headers - categories change infrequently
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
        categories = category_service.get_all(db, skip=pagination.skip, limit=pagination.size)
        total = len(categories)  # For simplicity, not using count query

        return {
            "items": categories,
            "total": total,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/tree", response_model=CategoryTree)
def read_category_tree(
        response: Response,
        db: Session = Depends(get_db),
) -> Any:
    """
    Get the complete category tree.
    
    Returns a hierarchical tree of all categories, showing parent-child relationships.
    This is useful for building navigation menus and category browsers.
    """
    # Set cache control headers - category tree changes infrequently
    response.headers["Cache-Control"] = "public, max-age=600"
    
    try:
        categories = category_service.get_category_tree(db)
        return {
            "items": categories,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/root", response_model=List[Category])
def read_root_categories(
        response: Response,
        db: Session = Depends(get_db),
) -> Any:
    """
    Get all root categories (with no parent).
    
    Returns a list of top-level categories that don't have a parent category.
    These are typically the main departments or sections in an e-commerce store.
    """
    # Set cache control headers - root categories change infrequently
    response.headers["Cache-Control"] = "public, max-age=600"
    
    try:
        return category_service.get_root_categories(db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{category_id}", response_model=CategoryWithParent)
def read_category(
        *,
        response: Response,
        db: Session = Depends(get_db),
        category_id: UUID = Path(..., description="The category ID"),
) -> Any:
    """
    Get a specific category by ID.
    
    Returns detailed information about a specific category, including its parent category if it has one.
    """
    # Set cache control headers - category details change infrequently
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
        return category_service.get_by_id(db, category_id=str(category_id))
    except NotFoundException as e:
        # Keep the cache headers but raise the exception
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e),
            headers={"Cache-Control": "public, max-age=60"}  # Shorter cache time for errors
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/slug/{slug}", response_model=CategoryWithParent)
def read_category_by_slug(
        *,
        response: Response,
        db: Session = Depends(get_db),
        slug: str = Path(..., min_length=3, max_length=100, description="The category slug"),
) -> Any:
    """
    Get a specific category by slug.
    
    Returns detailed information about a specific category using its URL-friendly slug.
    This is useful for building SEO-friendly category pages.
    """
    # Set cache control headers - category details change infrequently
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
        return category_service.get_by_slug(db, slug=slug)
    except NotFoundException as e:
        # Keep the cache headers but raise the exception
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e),
            headers={"Cache-Control": "public, max-age=60"}  # Shorter cache time for errors
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{category_id}/children", response_model=List[Category])
def read_category_children(
        *,
        response: Response,
        db: Session = Depends(get_db),
        category_id: UUID = Path(..., description="The category ID"),
) -> Any:
    """
    Get children of a specific category.
    
    Returns a list of all direct child categories for a given parent category.
    This is useful for building category navigation and drill-down interfaces.
    """
    # Set cache control headers - category relationships change infrequently
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
        category = category_service.get_with_children(db, category_id=str(category_id))
        return category.children
    except NotFoundException as e:
        # Keep the cache headers but raise the exception
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e),
            headers={"Cache-Control": "public, max-age=60"}  # Shorter cache time for errors
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/slug/{slug}/children", response_model=List[Category])
def read_category_children_by_slug(
        *,
        response: Response,
        db: Session = Depends(get_db),
        slug: str = Path(..., min_length=3, max_length=100, description="The category slug"),
) -> Any:
    """
    Get children of a specific category by slug.
    
    Returns a list of all direct child categories for a given parent category, identified by slug.
    This is useful for building SEO-friendly category navigation.
    """
    # Set cache control headers - category relationships change infrequently
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
        category = category_service.get_by_slug_with_children(db, slug=slug)
        return category.children
    except NotFoundException as e:
        # Keep the cache headers but raise the exception
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e),
            headers={"Cache-Control": "public, max-age=60"}  # Shorter cache time for errors
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{category_id}/products", response_model=ProductList)
def read_category_products(
        *,
        response: Response,
        db: Session = Depends(get_db),
        category_id: UUID = Path(..., description="The category ID"),
        pagination: PaginationParams = Depends(get_pagination),
) -> Any:
    """
    Get products in a specific category.
    
    Returns a paginated list of products that belong to the specified category.
    This endpoint is essential for displaying category product listings.
    """
    # Set cache control headers - product listings change more frequently
    response.headers["Cache-Control"] = "public, max-age=120"
    
    try:
        products, total = product_service.get_by_category(
            db, category_id=str(category_id), page=pagination.page, size=pagination.size
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
    except NotFoundException as e:
        # Keep the cache headers but raise the exception
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e),
            headers={"Cache-Control": "public, max-age=60"}  # Shorter cache time for errors
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
        *,
        db: Session = Depends(get_db),
        category_in: CategoryCreate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create a new category. Only for superusers.
    
    Creates a new product category with the provided details.
    Categories can be nested by specifying a parent_id.
    """
    try:
        return category_service.create(db, category_in=category_in)
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{category_id}", response_model=Category)
def update_category(
        *,
        db: Session = Depends(get_db),
        category_id: UUID = Path(..., description="The category ID"),
        category_in: CategoryUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a category. Only for superusers.
    
    Updates an existing category with new information.
    This can be used to rename categories, change their descriptions, or move them in the hierarchy.
    """
    try:
        return category_service.update(db, category_id=str(category_id), category_in=category_in)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
        *,
        db: Session = Depends(get_db),
        category_id: UUID = Path(..., description="The category ID"),
        current_user: User = Depends(get_current_active_superuser),
) -> None:
    """
    Delete a category. Only for superusers.
    
    Permanently removes a category from the system.
    Note: This may fail if there are products still assigned to this category
    or if it has child categories.
    """
    try:
        category_service.delete(db, category_id=str(category_id))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
