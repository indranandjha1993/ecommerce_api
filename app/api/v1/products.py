from typing import Any, List, Optional, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, Response, HTTPException, Path
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_active_superuser,
)
from app.api.dependencies.pagination import PaginationParams, get_pagination
from app.core.exceptions import NotFoundException
from app.db.session import get_db
from app.models.user import User
from app.schemas.product import (
    Product,
    ProductCreate,
    ProductUpdate,
    ProductList,
    ProductListItem,
    ProductSearchQuery,
    ProductWithRelations,
)
from app.services.product import product_service

router = APIRouter()


@router.get("", response_model=ProductList)
def read_products(
        response: Response,
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
        brand_id: Optional[UUID] = Query(None, description="Filter by brand ID"),
        query: Optional[str] = Query(None, description="Search query"),
        min_price: Optional[float] = Query(None, description="Minimum price"),
        max_price: Optional[float] = Query(None, description="Maximum price"),
        in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
        sort_by: Literal["created_at", "name", "price", "updated_at"] = Query(
            "created_at", 
            description="Sort field"
        ),
        sort_order: Literal["asc", "desc"] = Query("desc", description="Sort order (asc or desc)"),
) -> Any:
    """
    Get all products with pagination and filtering.
    
    This endpoint returns a paginated list of products with various filtering options:
    - Filter by category or brand
    - Search by text query
    - Filter by price range
    - Filter by stock availability
    - Sort by different fields in ascending or descending order
    
    The response includes pagination metadata (total items, current page, etc.)
    """
    # Set cache control headers for read-only data
    response.headers["Cache-Control"] = "public, max-age=60"
    search_query = ProductSearchQuery(
        query=query,
        category_id=category_id,
        brand_id=brand_id,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        sort_by=sort_by,
        sort_order=sort_order,
        page=pagination.page,
        size=pagination.size,
    )

    products, total = product_service.search(db, search_query=search_query)

    # Calculate total pages
    pages = (total + pagination.size - 1) // pagination.size

    return {
        "items": products,
        "total": total,
        "page": pagination.page,
        "size": pagination.size,
        "pages": pages,
    }


@router.get("/featured", response_model=List[ProductListItem])
def read_featured_products(
        response: Response,
        db: Session = Depends(get_db),
        limit: int = Query(10, ge=1, le=50, description="Number of products to return"),
) -> Any:
    """
    Get featured products.
    
    Returns a list of products that have been marked as featured.
    These are typically products that the store wants to highlight,
    such as seasonal items, promotions, or best-selling products.
    
    The number of products returned can be controlled with the limit parameter.
    """
    # Set cache control headers - featured products change less frequently
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
        products = product_service.get_featured_products(db, limit=limit)
        return products
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/new-arrivals", response_model=List[ProductListItem])
def read_new_arrivals(
        response: Response,
        db: Session = Depends(get_db),
        limit: int = Query(10, ge=1, le=50, description="Number of products to return"),
        days: int = Query(30, ge=1, le=90, description="Consider products added within this many days"),
) -> Any:
    """
    Get new arrivals (recently added products).
    
    Returns a list of products that have been recently added to the store.
    Products are sorted by creation date, with the newest products first.
    
    You can control how many products to return with the limit parameter,
    and how recent the products should be with the days parameter.
    """
    # Set cache control headers - new arrivals change more frequently
    response.headers["Cache-Control"] = "public, max-age=120"
    
    try:
        products = product_service.get_new_arrivals(db, limit=limit, days=days)
        return products
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/bestsellers", response_model=List[ProductListItem])
def read_bestsellers(
        response: Response,
        db: Session = Depends(get_db),
        limit: int = Query(10, ge=1, le=50, description="Number of products to return"),
        period: Literal["week", "month", "year", "all"] = Query("month", description="Time period for bestsellers calculation"),
) -> Any:
    """
    Get bestselling products.
    
    Returns a list of products that have sold the most units over a specified time period.
    Products are sorted by the number of units sold, with the highest-selling products first.
    
    You can control how many products to return with the limit parameter,
    and the time period to consider with the period parameter.
    """
    # Set cache control headers - bestsellers change periodically
    response.headers["Cache-Control"] = "public, max-age=600"
    
    try:
        products = product_service.get_bestsellers(db, limit=limit, period=period)
        return products
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/category/{category_id}", response_model=ProductList)
def read_products_by_category(
        *,
        response: Response,
        db: Session = Depends(get_db),
        category_id: UUID = Path(..., description="The ID of the category to filter by"),
        pagination: PaginationParams = Depends(get_pagination),
        include_subcategories: bool = Query(True, description="Include products from subcategories"),
        sort_by: Literal["created_at", "name", "price", "updated_at"] = Query(
            "created_at", 
            description="Sort field"
        ),
        sort_order: Literal["asc", "desc"] = Query("desc", description="Sort order (asc or desc)"),
) -> Any:
    """
    Get products by category.
    
    Returns a paginated list of products that belong to the specified category.
    By default, products from subcategories are also included, but this can be disabled.
    
    Results can be sorted by different fields in ascending or descending order.
    """
    # Set cache control headers
    response.headers["Cache-Control"] = "public, max-age=180"
    
    try:
        products, total = product_service.get_by_category(
            db, 
            category_id=category_id, 
            page=pagination.page, 
            size=pagination.size,
            include_subcategories=include_subcategories,
            sort_by=sort_by,
            sort_order=sort_order
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/brand/{brand_id}", response_model=ProductList)
def read_products_by_brand(
        *,
        response: Response,
        db: Session = Depends(get_db),
        brand_id: UUID = Path(..., description="The ID of the brand to filter by"),
        pagination: PaginationParams = Depends(get_pagination),
        category_id: Optional[UUID] = Query(None, description="Optional category filter"),
        sort_by: Literal["created_at", "name", "price", "updated_at"] = Query(
            "created_at", 
            description="Sort field"
        ),
        sort_order: Literal["asc", "desc"] = Query("desc", description="Sort order (asc or desc)"),
) -> Any:
    """
    Get products by brand.
    
    Returns a paginated list of products from the specified brand.
    Results can be further filtered by category and sorted by different fields.
    
    This endpoint is useful for brand-specific product listings and can be
    combined with category filtering for more specific results.
    """
    # Set cache control headers
    response.headers["Cache-Control"] = "public, max-age=180"
    
    try:
        products, total = product_service.get_by_brand(
            db, 
            brand_id=brand_id, 
            page=pagination.page, 
            size=pagination.size,
            category_id=category_id,
            sort_by=sort_by,
            sort_order=sort_order
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/search", response_model=List[ProductListItem])
def search_products(
        *,
        response: Response,
        db: Session = Depends(get_db),
        q: str = Query(..., min_length=2, description="Search query"),
        limit: int = Query(10, ge=1, le=50, description="Number of products to return"),
) -> Any:
    """
    Search for products by name or description.
    
    This endpoint provides a simple search functionality for product names, descriptions, and SKUs.
    Results are limited to the specified number of products.
    
    For more advanced search with filtering and pagination, use the main products endpoint
    with the query parameter.
    
    Example: /api/v1/products/search?q=smartphone&limit=20
    """
    # Set cache control headers - shorter cache time for search results
    response.headers["Cache-Control"] = "public, max-age=60"
    
    try:
        products, _ = product_service.search_by_text(db, query=q, limit=limit)
        return products
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/slug/{slug}", response_model=ProductWithRelations)
def read_product_by_slug(
        *,
        response: Response,
        db: Session = Depends(get_db),
        slug: str = Path(..., min_length=3, max_length=100, description="The slug of the product to retrieve"),
) -> Any:
    """
    Get a specific product by slug.
    
    Returns detailed information about a product identified by its URL-friendly slug.
    This endpoint is typically used for product detail pages and includes all related
    information such as variants, attributes, images, and inventory status.
    
    The slug is a URL-friendly version of the product name and is more SEO-friendly
    than using the product ID in URLs.
    """
    # Set cache control headers - product details can be cached longer
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
        return product_service.get_by_slug(db, slug=slug)
    except NotFoundException as e:
        # For 404 errors, we still want to cache the response but for a shorter time
        response.headers["Cache-Control"] = "public, max-age=60"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{product_id}", response_model=ProductWithRelations)
def read_product(
        *,
        response: Response,
        db: Session = Depends(get_db),
        product_id: UUID = Path(..., description="The ID of the product to retrieve"),
) -> Any:
    """
    Get a specific product by ID.
    
    Returns detailed information about a product identified by its unique ID.
    This endpoint includes all related information such as variants, attributes,
    images, and inventory status.
    
    While this endpoint works well for internal use, consider using the slug-based
    endpoint for customer-facing applications for better SEO.
    """
    # Set cache control headers - product details can be cached longer
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
        return product_service.get_by_id(db, product_id=product_id)
    except NotFoundException as e:
        # For 404 errors, we still want to cache the response but for a shorter time
        response.headers["Cache-Control"] = "public, max-age=60"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{product_id}/related", response_model=List[ProductListItem])
def read_related_products(
        *,
        response: Response,
        db: Session = Depends(get_db),
        product_id: UUID = Path(..., description="The ID of the product to find related items for"),
        limit: int = Query(5, ge=1, le=20, description="Number of related products to return"),
        relation_type: Literal["category", "brand", "tags", "purchased_together", "all"] = Query(
            "all", 
            description="Type of relation to consider"
        ),
) -> Any:
    """
    Get related products for a specific product.
    
    Returns a list of products that are related to the specified product.
    The relation can be based on different criteria:
    
    - category: Products in the same category
    - brand: Products from the same brand
    - tags: Products sharing similar tags
    - purchased_together: Products frequently purchased together
    - all: Consider all relation types (default)
    
    This endpoint is useful for "You might also like" or "Related products" sections
    on product detail pages.
    """
    # Set cache control headers - related products can be cached
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
        return product_service.get_related_products(
            db, 
            product_id=product_id, 
            limit=limit,
            relation_type=relation_type
        )
    except NotFoundException as e:
        # For 404 errors, we still want to cache the response but for a shorter time
        response.headers["Cache-Control"] = "public, max-age=60"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(
        *,
        response: Response,
        db: Session = Depends(get_db),
        product_in: ProductCreate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create a new product. Only for superusers.
    
    Creates a new product with the provided details. This endpoint is restricted
    to superusers only.
    
    The request body should contain all required product information, including:
    - Basic product details (name, description, price)
    - Category and brand associations
    - Attributes and variants (if applicable)
    - Images and other media
    
    Upon successful creation, the complete product object is returned with its
    generated ID and other system fields.
    """
    # Set cache control headers - creation should not be cached
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    
    try:
        return product_service.create(db, product_in=product_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{product_id}", response_model=Product)
def update_product(
        *,
        response: Response,
        db: Session = Depends(get_db),
        product_id: UUID = Path(..., description="The ID of the product to update"),
        product_in: ProductUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a product. Only for superusers.
    
    Updates an existing product with the provided details. This endpoint is restricted
    to superusers only.
    
    The request body should contain the fields to be updated. Fields that are not included
    will retain their current values. This allows for partial updates.
    
    Upon successful update, the complete updated product object is returned.
    """
    # Set cache control headers - updates should not be cached
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    
    try:
        return product_service.update(db, product_id=product_id, product_in=product_in)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
        *,
        response: Response,
        db: Session = Depends(get_db),
        product_id: UUID = Path(..., description="The ID of the product to delete"),
        force: bool = Query(False, description="Force deletion even if product has dependencies"),
        current_user: User = Depends(get_current_active_superuser),
) -> None:
    """
    Delete a product. Only for superusers.
    
    Permanently removes a product from the system. This endpoint is restricted
    to superusers only.
    
    By default, deletion will fail if the product has dependencies (such as order items).
    Use the force parameter to override this behavior and delete the product anyway.
    
    Note: Deleting a product is a permanent action and cannot be undone. Consider
    using the update endpoint to mark a product as inactive instead.
    """
    # Set cache control headers - deletion should not be cached
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    
    try:
        product_service.delete(db, product_id=product_id, force=force)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{product_id}/inventory", status_code=status.HTTP_200_OK)
def update_product_inventory(
        *,
        response: Response,
        db: Session = Depends(get_db),
        product_id: UUID = Path(..., description="The ID of the product to update inventory for"),
        variant_id: Optional[UUID] = Query(None, description="Optional variant ID if updating a specific variant"),
        quantity: int = Query(..., ge=0, le=1000000, description="New inventory quantity"),
        adjustment_type: Literal["set", "add", "subtract"] = Query("set", description="Type of inventory adjustment"),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update product inventory. Only for superusers.
    
    Updates the inventory quantity for a product or a specific variant of a product.
    This endpoint is restricted to superusers only.
    
    The inventory can be updated in three ways:
    - set: Set the inventory to the exact quantity provided
    - add: Add the provided quantity to the current inventory
    - subtract: Subtract the provided quantity from the current inventory
    
    If a variant_id is provided, the inventory for that specific variant will be updated.
    Otherwise, the main product inventory will be updated.
    """
    # Set cache control headers - inventory updates should not be cached
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    
    try:
        updated_quantity = product_service.update_inventory(
            db, 
            product_id=product_id, 
            variant_id=variant_id, 
            quantity=quantity,
            adjustment_type=adjustment_type
        )
        return {
            "message": "Inventory updated successfully",
            "product_id": str(product_id),
            "variant_id": str(variant_id) if variant_id else None,
            "quantity": updated_quantity
        }
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
