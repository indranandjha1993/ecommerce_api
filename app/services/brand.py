import uuid
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.models.brand import Brand
from app.repositories.brand import brand_repository
from app.schemas.brand import BrandCreate, BrandUpdate


class BrandService:
    """
    Brand service for business logic.
    """

    def get_by_id(self, db: Session, brand_id: uuid.UUID) -> Brand:
        """
        Get a brand by ID.
        """
        brand = brand_repository.get_with_product_count(db, id=brand_id)
        if not brand:
            raise NotFoundException(detail="Brand not found")
        return brand

    def get_by_slug(self, db: Session, slug: str) -> Brand:
        """
        Get a brand by slug.
        """
        brand = brand_repository.get_by_slug(db, slug=slug)
        if not brand:
            raise NotFoundException(detail="Brand not found")

        # Add product count
        brand.product_count = len(brand.products)

        return brand

    def get_all(
            self, db: Session, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Brand], int]:
        """
        Get all brands with pagination.
        """
        return brand_repository.get_multi_with_product_count(db, skip=skip, limit=limit)

    def get_featured_brands(self, db: Session, limit: int = 10) -> List[Brand]:
        """
        Get featured brands.
        """
        return brand_repository.get_featured_brands(db, limit=limit)

    def create(self, db: Session, brand_in: BrandCreate) -> Brand:
        """
        Create a new brand.
        """
        try:
            return brand_repository.create_with_slug_check(db, obj_in=brand_in)
        except ValueError as e:
            raise BadRequestException(detail=str(e))

    def update(self, db: Session, brand_id: uuid.UUID, brand_in: BrandUpdate) -> Brand:
        """
        Update a brand.
        """
        brand = brand_repository.get(db, id=brand_id)
        if not brand:
            raise NotFoundException(detail="Brand not found")

        try:
            return brand_repository.update_with_slug_check(db, db_obj=brand, obj_in=brand_in)
        except ValueError as e:
            raise BadRequestException(detail=str(e))

    def delete(self, db: Session, brand_id: uuid.UUID) -> None:
        """
        Delete a brand.
        """
        brand = brand_repository.get(db, id=brand_id)
        if not brand:
            raise NotFoundException(detail="Brand not found")

        # Check if brand has products
        if brand.products:
            raise BadRequestException(detail="Cannot delete brand with products")

        brand_repository.remove(db, id=brand_id)


brand_service = BrandService()
