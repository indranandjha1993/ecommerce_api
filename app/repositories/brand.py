import uuid
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.brand import Brand
from app.repositories.base import BaseRepository
from app.schemas.brand import BrandCreate, BrandUpdate


class BrandRepository(BaseRepository[Brand, BrandCreate, BrandUpdate]):
    """
    Brand repository for data access operations.
    """

    def get_by_slug(self, db: Session, slug: str) -> Optional[Brand]:
        """
        Get a brand by slug.
        """
        return db.query(Brand).filter(Brand.slug == slug).first()

    def get_with_product_count(self, db: Session, id: uuid.UUID) -> Optional[Brand]:
        """
        Get a brand with product count.
        """
        brand = db.query(Brand).filter(Brand.id == id).first()
        if brand:
            brand.product_count = len(brand.products)
        return brand

    def get_multi_with_product_count(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Brand], int]:
        """
        Get multiple brands with product count.
        """
        query = db.query(Brand)
        total = query.count()

        brands = query.offset(skip).limit(limit).all()

        # Populate product count for each brand
        for brand in brands:
            brand.product_count = len(brand.products)

        return brands, total

    def get_featured_brands(self, db: Session, limit: int = 10) -> List[Brand]:
        """
        Get featured brands.
        """
        brands = (
            db.query(Brand)
            .filter(Brand.is_featured == True, Brand.is_active == True)
            .order_by(Brand.name)
            .limit(limit)
            .all()
        )

        # Populate product count for each brand
        for brand in brands:
            brand.product_count = len(brand.products)

        return brands

    def create_with_slug_check(self, db: Session, obj_in: BrandCreate) -> Brand:
        """
        Create a brand with slug uniqueness check.
        """
        # Check if a brand with this slug already exists
        existing_brand = self.get_by_slug(db, slug=obj_in.slug)
        if existing_brand:
            raise ValueError(f"A brand with slug '{obj_in.slug}' already exists")

        # Create brand
        return self.create(db, obj_in=obj_in)

    def update_with_slug_check(
            self, db: Session, *, db_obj: Brand, obj_in: BrandUpdate
    ) -> Brand:
        """
        Update a brand with slug uniqueness check.
        """
        # Check if slug is being changed and if it's already in use
        if obj_in.slug and obj_in.slug != db_obj.slug:
            existing_brand = self.get_by_slug(db, slug=obj_in.slug)
            if existing_brand and existing_brand.id != db_obj.id:
                raise ValueError(f"A brand with slug '{obj_in.slug}' already exists")

        # Update brand
        return self.update(db, db_obj=db_obj, obj_in=obj_in)


brand_repository = BrandRepository(Brand)
