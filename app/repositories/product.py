import uuid
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.category import Category
from app.models.inventory import Inventory
from app.models.product import Product, ProductImage, ProductAttributeValue
from app.models.product_variant import ProductVariant, ProductVariantAttribute
from app.repositories.base import BaseRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository(BaseRepository[Product, ProductCreate, ProductUpdate]):
    """
    Product repository for data access operations.
    """

    def get_with_relations(self, db: Session, id: Any) -> Optional[Product]:
        """
        Get a product by ID with related entities.
        """
        return (
            db.query(Product)
            .filter(Product.id == id)
            .options(
                joinedload(Product.category),
                joinedload(Product.brand),
                joinedload(Product.images),
                joinedload(Product.variants).joinedload(ProductVariant.variant_attributes).joinedload(
                    ProductVariantAttribute.attribute),
                joinedload(Product.variants).joinedload(ProductVariant.variant_attributes).joinedload(
                    ProductVariantAttribute.attribute_value),
                joinedload(Product.variants).joinedload(ProductVariant.inventory),
                joinedload(Product.attribute_values).joinedload(ProductAttributeValue.attribute),
                joinedload(Product.reviews),
                joinedload(Product.inventory),
            )
            .first()
        )

    def get_by_slug(self, db: Session, slug: str) -> Optional[Product]:
        """
        Get a product by slug.
        """
        return db.query(Product).filter(Product.slug == slug).first()

    def get_by_slug_with_relations(self, db: Session, slug: str) -> Optional[Product]:
        """
        Get a product by slug with related entities.
        """
        return (
            db.query(Product)
            .filter(Product.slug == slug)
            .options(
                joinedload(Product.category),
                joinedload(Product.brand),
                joinedload(Product.images),
                joinedload(Product.variants).joinedload(ProductVariant.variant_attributes).joinedload(
                    ProductVariantAttribute.attribute),
                joinedload(Product.variants).joinedload(ProductVariant.variant_attributes).joinedload(
                    ProductVariantAttribute.attribute_value),
                joinedload(Product.variants).joinedload(ProductVariant.inventory),
                joinedload(Product.attribute_values).joinedload(ProductAttributeValue.attribute),
                joinedload(Product.reviews),
                joinedload(Product.inventory),
            )
            .first()
        )

    def get_multi_with_relations(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """
        Get multiple products with related entities.
        """
        return (
            db.query(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.brand),
                joinedload(Product.images),
                joinedload(Product.inventory),
                joinedload(Product.reviews),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_products(
            self,
            db: Session,
            *,
            query: Optional[str] = None,
            category_id: Optional[uuid.UUID] = None,
            brand_id: Optional[uuid.UUID] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            in_stock: Optional[bool] = None,
            attributes: Optional[Dict[str, List[str]]] = None,
            sort_by: str = "created_at",
            sort_order: str = "desc",
            skip: int = 0,
            limit: int = 20
    ) -> Tuple[List[Product], int]:
        """
        Search products with various filters.
        """
        # Start with base query
        product_query = db.query(Product).filter(Product.is_active == True)

        # Apply text search if provided
        if query:
            search_term = f"%{query}%"
            product_query = product_query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.sku.ilike(search_term),
                )
            )

        # Apply category filter
        if category_id:
            # Include subcategories
            category_ids = [category_id]
            categories = db.query(Category).filter(Category.parent_id == category_id).all()
            category_ids.extend([cat.id for cat in categories])

            product_query = product_query.filter(Product.category_id.in_(category_ids))

        # Apply brand filter
        if brand_id:
            product_query = product_query.filter(Product.brand_id == brand_id)

        # Apply price filters
        if min_price is not None:
            product_query = product_query.filter(Product.price >= min_price)
        if max_price is not None:
            product_query = product_query.filter(Product.price <= max_price)

        # Apply stock filter
        if in_stock is not None and in_stock:
            product_query = product_query.join(Inventory).filter(Inventory.quantity > 0)

        # Apply attribute filters
        if attributes:
            for attr_id, values in attributes.items():
                if values:  # Only apply filter if values are specified
                    product_query = product_query.join(
                        ProductAttributeValue,
                        Product.id == ProductAttributeValue.product_id
                    ).filter(
                        ProductAttributeValue.attribute_id == attr_id,
                        ProductAttributeValue.value.in_(values)
                    )

        # Get total count before applying pagination
        total = product_query.count()

        # Apply sorting
        if sort_order.lower() == "asc":
            product_query = product_query.order_by(getattr(Product, sort_by).asc())
        else:
            product_query = product_query.order_by(getattr(Product, sort_by).desc())

        # Apply pagination
        products = product_query.options(
            joinedload(Product.category),
            joinedload(Product.brand),
            joinedload(Product.images),
            joinedload(Product.inventory),
            joinedload(Product.reviews),
        ).offset(skip).limit(limit).all()

        return products, total

    def get_products_by_category(
            self, db: Session, *, category_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Product], int]:
        """
        Get products by category with pagination.
        """
        # Include subcategories
        category_ids = [category_id]
        categories = db.query(Category).filter(Category.parent_id == category_id).all()
        category_ids.extend([cat.id for cat in categories])

        query = db.query(Product).filter(
            Product.category_id.in_(category_ids),
            Product.is_active == True
        )

        total = query.count()

        products = query.options(
            joinedload(Product.category),
            joinedload(Product.brand),
            joinedload(Product.images),
            joinedload(Product.inventory),
            joinedload(Product.reviews),
        ).offset(skip).limit(limit).all()

        return products, total

    def get_products_by_brand(
            self, db: Session, *, brand_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Product], int]:
        """
        Get products by brand with pagination.
        """
        query = db.query(Product).filter(
            Product.brand_id == brand_id,
            Product.is_active == True
        )

        total = query.count()

        products = query.options(
            joinedload(Product.category),
            joinedload(Product.brand),
            joinedload(Product.images),
            joinedload(Product.inventory),
            joinedload(Product.reviews),
        ).offset(skip).limit(limit).all()

        return products, total

    def get_featured_products(
            self, db: Session, *, limit: int = 10
    ) -> List[Product]:
        """
        Get featured products.
        """
        return (
            db.query(Product)
            .filter(Product.is_featured == True, Product.is_active == True)
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

    def get_new_arrivals(
            self, db: Session, *, limit: int = 10
    ) -> List[Product]:
        """
        Get new arrivals (recently added products).
        """
        return (
            db.query(Product)
            .filter(Product.is_active == True)
            .options(
                joinedload(Product.category),
                joinedload(Product.brand),
                joinedload(Product.images),
                joinedload(Product.inventory),
                joinedload(Product.reviews),
            )
            .order_by(Product.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_bestsellers(
            self, db: Session, *, limit: int = 10
    ) -> List[Product]:
        """
        Get bestsellers based on order items.
        """
        from app.models.order import OrderItem, Order
        from app.models.order import OrderStatus

        # Subquery to count completed orders for each product
        bestsellers = (
            db.query(
                OrderItem.product_id,
                func.sum(OrderItem.quantity).label("total_sold")
            )
            .join(Order)
            .filter(Order.status == OrderStatus.COMPLETED)
            .group_by(OrderItem.product_id)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
            .subquery()
        )

        # Query products in bestseller order
        return (
            db.query(Product)
            .join(bestsellers, Product.id == bestsellers.c.product_id)
            .filter(Product.is_active == True)
            .options(
                joinedload(Product.category),
                joinedload(Product.brand),
                joinedload(Product.images),
                joinedload(Product.inventory),
                joinedload(Product.reviews),
            )
            .all()
        )

    def create_product_with_relations(
            self, db: Session, *, obj_in: ProductCreate
    ) -> Product:
        """
        Create a product with related entities.
        """
        # Create the product
        product_data = obj_in.dict(
            exclude={"attributes", "variants", "images"}
        )
        db_product = Product(**product_data)
        db.add(db_product)
        db.flush()  # Flush to get the product ID

        # Add product attributes
        if obj_in.attributes:
            for attr in obj_in.attributes:
                db_attr_value = ProductAttributeValue(
                    product_id=db_product.id,
                    attribute_id=attr.attribute_id,
                    value=attr.value
                )
                db.add(db_attr_value)

        # Add product images
        if obj_in.images:
            for idx, image in enumerate(obj_in.images):
                is_primary = idx == 0  # First image is primary by default
                db_image = ProductImage(
                    product_id=db_product.id,
                    image_url=image.image_url,
                    alt_text=image.alt_text,
                    is_primary=image.is_primary if image.is_primary is not None else is_primary,
                    display_order=image.display_order or idx
                )
                db.add(db_image)

        # Add product variants
        if obj_in.variants:
            for variant in obj_in.variants:
                variant_data = variant.dict(exclude={"attributes"})
                db_variant = ProductVariant(
                    product_id=db_product.id,
                    **variant_data
                )
                db.add(db_variant)
                db.flush()  # Flush to get the variant ID

                # Add variant attributes
                for attr in variant.attributes:
                    db_variant_attr = ProductVariantAttribute(
                        variant_id=db_variant.id,
                        attribute_id=attr.attribute_id,
                        attribute_value_id=attr.attribute_value_id
                    )
                    db.add(db_variant_attr)

                # Create inventory record for the variant
                db_inventory = Inventory(
                    product_id=db_product.id,
                    variant_id=db_variant.id,
                    quantity=0  # Default to 0 quantity
                )
                db.add(db_inventory)
        else:
            # Create inventory record for the product
            db_inventory = Inventory(
                product_id=db_product.id,
                quantity=0  # Default to 0 quantity
            )
            db.add(db_inventory)

        db.commit()
        db.refresh(db_product)
        return db_product

    def update_product_with_relations(
            self, db: Session, *, db_obj: Product, obj_in: ProductUpdate
    ) -> Product:
        """
        Update a product with related entities.
        """
        # Update the product
        update_data = obj_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


product_repository = ProductRepository(Product)
