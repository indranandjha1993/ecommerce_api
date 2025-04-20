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
        response: Response,
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
) -> Any:
    """
    Get all brands with pagination.
    
    Returns a paginated list of all brands in the system.
    Brands are used to categorize products by manufacturer or company.
    """
    # Set cache control headers - brands change infrequently
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
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
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/featured", response_model=List[Brand])
def read_featured_brands(
        response: Response,
        db: Session = Depends(get_db),
        limit: int = Query(10, ge=1, le=50, description="Number of brands to return"),
) -> Any:
    """
    Get featured brands.
    
    Returns a list of brands that are marked as featured.
    Featured brands are typically highlighted in the UI, such as on the homepage.
    """
    # Set cache control headers - featured brands change infrequently
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
        return brand_service.get_featured_brands(db, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{brand_id}", response_model=Brand)
def read_brand(
        *,
        response: Response,
        db: Session = Depends(get_db),
        brand_id: UUID = Path(..., description="The brand ID"),
) -> Any:
    """
    Get a specific brand by ID.
    
    Returns detailed information about a specific brand identified by its unique ID.
    """
    # Set cache control headers - brand details change infrequently
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
        return brand_service.get_by_id(db, brand_id=str(brand_id))
    except NotFoundException as e:
        # Keep the cache headers but raise the exception
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e),
            headers={"Cache-Control": "public, max-age=60"}  # Shorter cache time for errors
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/slug/{slug}", response_model=Brand)
def read_brand_by_slug(
        *,
        response: Response,
        db: Session = Depends(get_db),
        slug: str = Path(..., min_length=3, max_length=100, description="The brand slug"),
) -> Any:
    """
    Get a specific brand by slug.
    
    Returns detailed information about a specific brand using its URL-friendly slug.
    This is useful for building SEO-friendly brand pages.
    """
    # Set cache control headers - brand details change infrequently
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
        return brand_service.get_by_slug(db, slug=slug)
    except NotFoundException as e:
        # Keep the cache headers but raise the exception
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e),
            headers={"Cache-Control": "public, max-age=60"}  # Shorter cache time for errors
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{brand_id}/products", response_model=ProductList)
def read_brand_products(
        *,
        response: Response,
        db: Session = Depends(get_db),
        brand_id: UUID = Path(..., description="The brand ID"),
        pagination: PaginationParams = Depends(get_pagination),
) -> Any:
    """
    Get products for a specific brand.
    
    Returns a paginated list of products that belong to the specified brand.
    This endpoint is essential for displaying brand product listings.
    """
    # Set cache control headers - product listings change more frequently
    response.headers["Cache-Control"] = "public, max-age=120"
    
    try:
        products, total = product_service.get_by_brand(
            db, brand_id=str(brand_id), page=pagination.page, size=pagination.size
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


@router.post("", response_model=Brand, status_code=status.HTTP_201_CREATED)
def create_brand(
        *,
        db: Session = Depends(get_db),
        brand_in: BrandCreate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create a new brand. Only for superusers.
    
    Creates a new product brand with the provided details.
    Brands are used to group products by manufacturer or company.
    """
    try:
        return brand_service.create(db, brand_in=brand_in)
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{brand_id}", response_model=Brand)
def update_brand(
        *,
        db: Session = Depends(get_db),
        brand_id: UUID = Path(..., description="The brand ID"),
        brand_in: BrandUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a brand. Only for superusers.
    
    Updates an existing brand with new information.
    This can be used to rename brands, change their descriptions, or update their website.
    """
    try:
        return brand_service.update(db, brand_id=str(brand_id), brand_in=brand_in)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(
        *,
        db: Session = Depends(get_db),
        brand_id: UUID = Path(..., description="The brand ID"),
        current_user: User = Depends(get_current_active_superuser),
) -> None:
    """
    Delete a brand. Only for superusers.
    
    Permanently removes a brand from the system.
    Note: This may fail if there are products still assigned to this brand.
    """
    try:
        brand_service.delete(db, brand_id=str(brand_id))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
