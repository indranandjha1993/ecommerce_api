from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_active_superuser,
)
from app.api.dependencies.pagination import PaginationParams, get_pagination
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
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        category_id: Optional[str] = Query(None, description="Filter by category ID"),
        brand_id: Optional[str] = Query(None, description="Filter by brand ID"),
        query: Optional[str] = Query(None, description="Search query"),
        min_price: Optional[float] = Query(None, description="Minimum price"),
        max_price: Optional[float] = Query(None, description="Maximum price"),
        in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
        sort_by: str = Query("created_at", description="Sort field"),
        sort_order: str = Query("desc", description="Sort order (asc or desc)"),
) -> Any:
    """
    Get all products with pagination and filtering.
    """
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
        db: Session = Depends(get_db),
        limit: int = Query(10, description="Number of products to return"),
) -> Any:
    """
    Get featured products.
    """
    products = product_service.get_featured_products(db, limit=limit)
    return products


@router.get("/new-arrivals", response_model=List[ProductListItem])
def read_new_arrivals(
        db: Session = Depends(get_db),
        limit: int = Query(10, description="Number of products to return"),
) -> Any:
    """
    Get new arrivals (recently added products).
    """
    products = product_service.get_new_arrivals(db, limit=limit)
    return products


@router.get("/bestsellers", response_model=List[ProductListItem])
def read_bestsellers(
        db: Session = Depends(get_db),
        limit: int = Query(10, description="Number of products to return"),
) -> Any:
    """
    Get bestselling products.
    """
    products = product_service.get_bestsellers(db, limit=limit)
    return products


@router.get("/category/{category_id}", response_model=ProductList)
def read_products_by_category(
        *,
        db: Session = Depends(get_db),
        category_id: str,
        pagination: PaginationParams = Depends(get_pagination),
) -> Any:
    """
    Get products by category.
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


@router.get("/brand/{brand_id}", response_model=ProductList)
def read_products_by_brand(
        *,
        db: Session = Depends(get_db),
        brand_id: str,
        pagination: PaginationParams = Depends(get_pagination),
) -> Any:
    """
    Get products by brand.
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


@router.get("/{product_id}", response_model=ProductWithRelations)
def read_product(
        *,
        db: Session = Depends(get_db),
        product_id: str,
) -> Any:
    """
    Get a specific product by ID.
    """
    return product_service.get_by_id(db, product_id=product_id)


@router.get("/slug/{slug}", response_model=ProductWithRelations)
def read_product_by_slug(
        *,
        db: Session = Depends(get_db),
        slug: str,
) -> Any:
    """
    Get a specific product by slug.
    """
    return product_service.get_by_slug(db, slug=slug)


@router.get("/products/search", response_model=List[Product])
def search_products(
        *,
        db: Session = Depends(get_db),
        q: str = Query(..., description="Search query"),
        limit: int = Query(10, description="Number of products to return"),
) -> Any:
    """
    Search for products by name or description.
    """
    products = product_service.search_by_text(db, query=q, limit=limit)
    return products


@router.get("/{product_id}/related", response_model=List[ProductListItem])
def read_related_products(
        *,
        db: Session = Depends(get_db),
        product_id: str,
        limit: int = Query(5, description="Number of related products to return"),
) -> Any:
    """
    Get related products for a specific product.
    """
    return product_service.get_related_products(db, product_id=product_id, limit=limit)


@router.post("", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(
        *,
        db: Session = Depends(get_db),
        product_in: ProductCreate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create a new product. Only for superusers.
    """
    return product_service.create(db, product_in=product_in)


@router.put("/{product_id}", response_model=Product)
def update_product(
        *,
        db: Session = Depends(get_db),
        product_id: str,
        product_in: ProductUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a product. Only for superusers.
    """
    return product_service.update(db, product_id=product_id, product_in=product_in)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
        *,
        db: Session = Depends(get_db),
        product_id: str,
        current_user: User = Depends(get_current_active_superuser),
) -> None:
    """
    Delete a product. Only for superusers.
    """
    product_service.delete(db, product_id=product_id)


@router.put("/{product_id}/inventory", status_code=status.HTTP_200_OK)
def update_product_inventory(
        *,
        db: Session = Depends(get_db),
        product_id: str,
        variant_id: Optional[str] = None,
        quantity: int = Query(..., ge=0, description="New inventory quantity"),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update product inventory. Only for superusers.
    """
    product_service.update_inventory(
        db, product_id=product_id, variant_id=variant_id, quantity=quantity
    )
    return {"message": "Inventory updated successfully"}
