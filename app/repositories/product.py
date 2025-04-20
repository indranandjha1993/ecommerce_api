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
            self, db: Session, *, category_id: uuid.UUID, skip: int = 0, limit: int = 100,
            include_subcategories: bool = True, sort_by: str = "created_at", sort_order: str = "desc"
    ) -> Tuple[List[Product], int]:
        """
        Get products by category with pagination.
        
        Args:
            db: Database session
            category_id: Category ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_subcategories: Whether to include products from subcategories
            sort_by: Field to sort by
            sort_order: Sort direction ("asc" or "desc")
            
        Returns:
            Tuple of (products list, total count)
        """
        # Start with base query
        query = db.query(Product).filter(Product.is_active == True)
        
        if include_subcategories:
            # Include subcategories
            category_ids = [category_id]
            categories = db.query(Category).filter(Category.parent_id == category_id).all()
            category_ids.extend([cat.id for cat in categories])
            query = query.filter(Product.category_id.in_(category_ids))
        else:
            # Only the specified category
            query = query.filter(Product.category_id == category_id)

        # Get total count
        total = query.count()

        # Apply sorting
        if sort_by == "name":
            sort_field = Product.name
        elif sort_by == "price":
            sort_field = Product.price
        elif sort_by == "updated_at":
            sort_field = Product.updated_at
        else:  # default to created_at
            sort_field = Product.created_at
            
        if sort_order == "asc":
            query = query.order_by(sort_field.asc())
        else:
            query = query.order_by(sort_field.desc())

        # Get products with relations
        products = query.options(
            joinedload(Product.category),
            joinedload(Product.brand),
            joinedload(Product.images),
            joinedload(Product.inventory),
            joinedload(Product.reviews),
        ).offset(skip).limit(limit).all()

        return products, total

    def get_products_by_brand(
            self, db: Session, *, brand_id: uuid.UUID, skip: int = 0, limit: int = 100,
            category_id: Optional[uuid.UUID] = None, sort_by: str = "created_at", sort_order: str = "desc"
    ) -> Tuple[List[Product], int]:
        """
        Get products by brand with pagination.
        
        Args:
            db: Database session
            brand_id: Brand ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            category_id: Optional category ID to further filter results
            sort_by: Field to sort by
            sort_order: Sort direction ("asc" or "desc")
            
        Returns:
            Tuple of (products list, total count)
        """
        # Start with base query
        query = db.query(Product).filter(
            Product.brand_id == brand_id,
            Product.is_active == True
        )
        
        # Apply category filter if provided
        if category_id:
            query = query.filter(Product.category_id == category_id)

        # Get total count
        total = query.count()
        
        # Apply sorting
        if sort_by == "name":
            sort_field = Product.name
        elif sort_by == "price":
            sort_field = Product.price
        elif sort_by == "updated_at":
            sort_field = Product.updated_at
        else:  # default to created_at
            sort_field = Product.created_at
            
        if sort_order == "asc":
            query = query.order_by(sort_field.asc())
        else:
            query = query.order_by(sort_field.desc())

        # Get products with relations
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
            self, db: Session, *, limit: int = 10, days: int = 30
    ) -> List[Product]:
        """
        Get new arrivals (recently added products).
        
        Args:
            db: Database session
            limit: Maximum number of products to return
            days: Consider products added within this many days
            
        Returns:
            List of recently added products
        """
        import datetime
        
        # Calculate the date threshold
        date_threshold = datetime.datetime.now() - datetime.timedelta(days=days)
        
        return (
            db.query(Product)
            .filter(
                Product.is_active == True,
                Product.created_at >= date_threshold
            )
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
            self, db: Session, *, limit: int = 10, period: str = "month"
    ) -> List[Product]:
        """
        Get bestsellers based on order items.
        
        Args:
            db: Database session
            limit: Maximum number of products to return
            period: Time period for bestsellers calculation ("week", "month", "year", "all")
            
        Returns:
            List of bestselling products
        """
        from app.models.order import OrderItem, Order
        from app.models.order import OrderStatus
        import datetime

        # Base query
        query = db.query(
            OrderItem.product_id,
            func.sum(OrderItem.quantity).label("total_sold")
        ).join(Order).filter(Order.status == OrderStatus.COMPLETED)
        
        # Apply time period filter
        if period != "all":
            now = datetime.datetime.now()
            if period == "week":
                date_threshold = now - datetime.timedelta(days=7)
            elif period == "month":
                date_threshold = now - datetime.timedelta(days=30)
            elif period == "year":
                date_threshold = now - datetime.timedelta(days=365)
            else:
                # Default to month if invalid period
                date_threshold = now - datetime.timedelta(days=30)
                
            query = query.filter(Order.created_at >= date_threshold)

        # Complete the query
        bestsellers = (
            query
            .group_by(OrderItem.product_id)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
            .subquery()
        )

        # Query products in bestseller order
        products = (
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
        
        # If we don't have enough bestsellers, supplement with featured products
        if len(products) < limit:
            featured_count = limit - len(products)
            existing_ids = [p.id for p in products]
            
            featured_products = (
                db.query(Product)
                .filter(
                    Product.is_active == True,
                    Product.is_featured == True,
                    ~Product.id.in_(existing_ids)
                )
                .options(
                    joinedload(Product.category),
                    joinedload(Product.brand),
                    joinedload(Product.images),
                    joinedload(Product.inventory),
                    joinedload(Product.reviews),
                )
                .limit(featured_count)
                .all()
            )
            
            products.extend(featured_products)
            
        return products

    def create_product_with_relations(
            self, db: Session, *, obj_in: ProductCreate
    ) -> Product:
        """
        Create a product with related entities.
        """
        # Create the product
        product_data = obj_in.model_dump(
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
                variant_data = variant.model_dump(exclude={"attributes"})
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
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def get_related_products(
            self, db: Session, *, product_id: uuid.UUID, limit: int = 5, relation_type: str = "all"
    ) -> List[Product]:
        """
        Get related products based on specified relation type.
        
        Args:
            db: Database session
            product_id: ID of the product to find related items for
            limit: Maximum number of products to return
            relation_type: Type of relation to consider ("category", "brand", "tags", "purchased_together", "all")
            
        Returns:
            List of related products
        """
        from app.models.order import OrderItem, Order
        
        product = self.get(db, id=product_id)
        if not product:
            return []
            
        related_products = []
        
        # Get products based on relation type
        if relation_type in ["category", "all"]:
            # Get products in the same category
            category_products = (
                db.query(Product)
                .filter(
                    Product.category_id == product.category_id,
                    Product.id != product_id,
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
            related_products.extend(category_products)
            
        if relation_type in ["brand", "all"] and product.brand_id and len(related_products) < limit:
            # Get products from the same brand
            remaining = limit - len(related_products)
            existing_ids = [p.id for p in related_products] + [product_id]
            
            brand_products = (
                db.query(Product)
                .filter(
                    Product.brand_id == product.brand_id,
                    ~Product.id.in_(existing_ids),
                    Product.is_active == True
                )
                .options(
                    joinedload(Product.category),
                    joinedload(Product.brand),
                    joinedload(Product.images),
                    joinedload(Product.inventory),
                    joinedload(Product.reviews),
                )
                .limit(remaining)
                .all()
            )
            related_products.extend(brand_products)
            
        if relation_type in ["purchased_together", "all"] and len(related_products) < limit:
            # Get products frequently purchased together
            remaining = limit - len(related_products)
            existing_ids = [p.id for p in related_products] + [product_id]
            
            # Find orders containing this product
            orders_with_product = (
                db.query(OrderItem.order_id)
                .filter(OrderItem.product_id == product_id)
                .subquery()
            )
            
            # Find other products in those orders
            purchased_together = (
                db.query(Product)
                .join(OrderItem, OrderItem.product_id == Product.id)
                .filter(
                    OrderItem.order_id.in_(db.query(orders_with_product.c.order_id)),
                    ~Product.id.in_(existing_ids),
                    Product.is_active == True
                )
                .options(
                    joinedload(Product.category),
                    joinedload(Product.brand),
                    joinedload(Product.images),
                    joinedload(Product.inventory),
                    joinedload(Product.reviews),
                )
                .limit(remaining)
                .all()
            )
            related_products.extend(purchased_together)
            
        # If we still don't have enough products, add some featured products
        if len(related_products) < limit:
            remaining = limit - len(related_products)
            existing_ids = [p.id for p in related_products] + [product_id]
            
            featured_products = (
                db.query(Product)
                .filter(
                    Product.is_featured == True,
                    ~Product.id.in_(existing_ids),
                    Product.is_active == True
                )
                .options(
                    joinedload(Product.category),
                    joinedload(Product.brand),
                    joinedload(Product.images),
                    joinedload(Product.inventory),
                    joinedload(Product.reviews),
                )
                .limit(remaining)
                .all()
            )
            related_products.extend(featured_products)
            
        return related_products[:limit]


product_repository = ProductRepository(Product)
