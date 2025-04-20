import uuid
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.models.product import Product, ProductImage
from app.models.product_variant import ProductVariant
from app.repositories.product import product_repository
from app.schemas.product import ProductCreate, ProductUpdate, ProductSearchQuery


class ProductService:
    """
    Product service for business logic.
    """

    def get_by_id(self, db: Session, product_id: uuid.UUID) -> Product:
        """
        Get a product by ID.
        """
        product = product_repository.get_with_relations(db, id=product_id)
        if not product:
            raise NotFoundException(detail="Product not found")
        return product

    def get_by_slug(self, db: Session, slug: str) -> Product:
        """
        Get a product by slug.
        """
        product = product_repository.get_by_slug_with_relations(db, slug=slug)
        if not product:
            raise NotFoundException(detail="Product not found")
        return product

    def get_all(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Product], int]:
        """
        Get all products with pagination.
        """
        products = product_repository.get_multi_with_relations(db, skip=skip, limit=limit)
        total = product_repository.get_count(db)
        return products, total

    def search(
            self, db: Session, *, search_query: ProductSearchQuery
    ) -> Tuple[List[Product], int]:
        """
        Search products with various filters.
        """
        return product_repository.search_products(
            db,
            query=search_query.query,
            category_id=search_query.category_id,
            brand_id=search_query.brand_id,
            min_price=search_query.min_price,
            max_price=search_query.max_price,
            in_stock=search_query.in_stock,
            attributes=search_query.attributes,
            sort_by=search_query.sort_by,
            sort_order=search_query.sort_order,
            skip=(search_query.page - 1) * search_query.size,
            limit=search_query.size
        )

    def get_by_category(
            self, db: Session, *, category_id: uuid.UUID, page: int = 1, size: int = 20
    ) -> Tuple[List[Product], int]:
        """
        Get products by category with pagination.
        """
        skip = (page - 1) * size
        return product_repository.get_products_by_category(
            db, category_id=category_id, skip=skip, limit=size
        )

    def get_by_brand(
            self, db: Session, *, brand_id: uuid.UUID, page: int = 1, size: int = 20
    ) -> Tuple[List[Product], int]:
        """
        Get products by brand with pagination.
        """
        skip = (page - 1) * size
        return product_repository.get_products_by_brand(
            db, brand_id=brand_id, skip=skip, limit=size
        )

    def get_featured_products(self, db: Session, *, limit: int = 10) -> List[Product]:
        """
        Get featured products.
        """
        return product_repository.get_featured_products(db, limit=limit)

    def get_new_arrivals(self, db: Session, *, limit: int = 10) -> List[Product]:
        """
        Get new arrivals (recently added products).
        """
        return product_repository.get_new_arrivals(db, limit=limit)

    def get_bestsellers(self, db: Session, *, limit: int = 10) -> List[Product]:
        """
        Get bestsellers based on order items.
        """
        return product_repository.get_bestsellers(db, limit=limit)

    def create(self, db: Session, *, product_in: ProductCreate) -> Product:
        """
        Create a new product with related entities.
        """
        # Check if a product with this slug already exists
        existing_product = product_repository.get_by_slug(db, slug=product_in.slug)
        if existing_product:
            raise BadRequestException(detail="A product with this slug already exists")

        # Create the product with relations
        return product_repository.create_product_with_relations(db, obj_in=product_in)

    def update(self, db: Session, *, product_id: uuid.UUID, product_in: ProductUpdate) -> Product:
        """
        Update a product.
        """
        product = product_repository.get(db, id=product_id)
        if not product:
            raise NotFoundException(detail="Product not found")

        # Check if slug is being changed and if it's already in use
        if product_in.slug and product_in.slug != product.slug:
            existing_product = product_repository.get_by_slug(db, slug=product_in.slug)
            if existing_product and existing_product.id != product_id:
                raise BadRequestException(detail="A product with this slug already exists")

        # Update the product
        return product_repository.update_product_with_relations(db, db_obj=product, obj_in=product_in)

    def delete(self, db: Session, *, product_id: uuid.UUID) -> None:
        """
        Delete a product.
        """
        product = product_repository.get(db, id=product_id)
        if not product:
            raise NotFoundException(detail="Product not found")

        # Delete the product (cascades to related entities)
        product_repository.remove(db, id=product_id)

    def update_inventory(
            self, db: Session, *, product_id: uuid.UUID, variant_id: Optional[uuid.UUID], quantity: int
    ) -> None:
        """
        Update product inventory.
        """
        from app.models.inventory import Inventory

        # Check if the product exists
        product = product_repository.get(db, id=product_id)
        if not product:
            raise NotFoundException(detail="Product not found")

        # Update inventory
        if variant_id:
            # Check if the variant exists
            variant = db.query(ProductVariant).filter(
                ProductVariant.id == variant_id,
                ProductVariant.product_id == product_id
            ).first()
            if not variant:
                raise NotFoundException(detail="Product variant not found")

            inventory = db.query(Inventory).filter(
                Inventory.product_id == product_id,
                Inventory.variant_id == variant_id
            ).first()
        else:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == product_id,
                Inventory.variant_id.is_(None)
            ).first()

        if not inventory:
            # Create inventory record if it doesn't exist
            inventory = Inventory(
                product_id=product_id,
                variant_id=variant_id,
                quantity=quantity
            )
            db.add(inventory)
        else:
            # Update existing inventory
            inventory.quantity = quantity
            db.add(inventory)

        db.commit()

    def add_product_image(
            self, db: Session, *, product_id: uuid.UUID, image_url: str, alt_text: Optional[str] = None,
            is_primary: bool = False
    ) -> ProductImage:
        """
        Add an image to a product.
        """
        # Check if the product exists
        product = product_repository.get(db, id=product_id)
        if not product:
            raise NotFoundException(detail="Product not found")

        # If this is set as primary, unset other primary images
        if is_primary:
            db.query(ProductImage).filter(
                ProductImage.product_id == product_id,
                ProductImage.is_primary == True
            ).update({"is_primary": False})

        # Create the image
        image = ProductImage(
            product_id=product_id,
            image_url=image_url,
            alt_text=alt_text,
            is_primary=is_primary
        )
        db.add(image)
        db.commit()
        db.refresh(image)

        return image

    def search_by_text(
            self, db: Session, *, query: str, limit: int = 10
    ) -> List[Product]:
        """
        Search for products by name or description.
        """
        from sqlalchemy import or_
        from sqlalchemy.orm import joinedload
        
        search_term = f"%{query}%"
        products = (
            db.query(Product)
            .filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                ),
                Product.is_active == True
            )
            .options(
                joinedload(Product.category),
                joinedload(Product.brand),
                joinedload(Product.images),
                joinedload(Product.inventory),
                joinedload(Product.reviews),
            )
            .limit(limit)
            .all()
        )
        
        return products

    def get_related_products(
            self, db: Session, *, product_id: uuid.UUID, limit: int = 5
    ) -> List[Product]:
        """
        Get related products based on category.
        """
        product = product_repository.get(db, id=product_id)
        if not product:
            raise NotFoundException(detail="Product not found")

        # Get products in the same category
        related_products = (
            db.query(Product)
            .filter(
                Product.category_id == product.category_id,
                Product.id != product_id,
                Product.is_active == True
            )
            .limit(limit)
            .all()
        )

        # If not enough products in the same category, add products from the same brand
        if len(related_products) < limit and product.brand_id:
            brand_products = (
                db.query(Product)
                .filter(
                    Product.brand_id == product.brand_id,
                    Product.id != product_id,
                    Product.id.notin_([p.id for p in related_products]),
                    Product.is_active == True
                )
                .limit(limit - len(related_products))
                .all()
            )
            related_products.extend(brand_products)

        return related_products


product_service = ProductService()
