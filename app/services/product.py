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
            self, db: Session, *, category_id: uuid.UUID, page: int = 1, size: int = 20,
            include_subcategories: bool = True, sort_by: str = "created_at", sort_order: str = "desc"
    ) -> Tuple[List[Product], int]:
        """
        Get products by category with pagination.
        
        Args:
            db: Database session
            category_id: Category ID to filter by
            page: Page number for pagination
            size: Number of items per page
            include_subcategories: Whether to include products from subcategories
            sort_by: Field to sort by
            sort_order: Sort direction ("asc" or "desc")
            
        Returns:
            Tuple of (products list, total count)
        """
        skip = (page - 1) * size
        return product_repository.get_products_by_category(
            db, 
            category_id=category_id, 
            skip=skip, 
            limit=size,
            include_subcategories=include_subcategories,
            sort_by=sort_by,
            sort_order=sort_order
        )

    def get_by_brand(
            self, db: Session, *, brand_id: uuid.UUID, page: int = 1, size: int = 20,
            category_id: Optional[uuid.UUID] = None, sort_by: str = "created_at", sort_order: str = "desc"
    ) -> Tuple[List[Product], int]:
        """
        Get products by brand with pagination.
        
        Args:
            db: Database session
            brand_id: Brand ID to filter by
            page: Page number for pagination
            size: Number of items per page
            category_id: Optional category ID to further filter results
            sort_by: Field to sort by
            sort_order: Sort direction ("asc" or "desc")
            
        Returns:
            Tuple of (products list, total count)
        """
        skip = (page - 1) * size
        return product_repository.get_products_by_brand(
            db, 
            brand_id=brand_id, 
            skip=skip, 
            limit=size,
            category_id=category_id,
            sort_by=sort_by,
            sort_order=sort_order
        )

    def get_featured_products(self, db: Session, *, limit: int = 10) -> List[Product]:
        """
        Get featured products.
        """
        return product_repository.get_featured_products(db, limit=limit)

    def get_new_arrivals(self, db: Session, *, limit: int = 10, days: int = 30) -> List[Product]:
        """
        Get new arrivals (recently added products).
        
        Args:
            db: Database session
            limit: Maximum number of products to return
            days: Consider products added within this many days
            
        Returns:
            List of recently added products
        """
        return product_repository.get_new_arrivals(db, limit=limit, days=days)

    def get_bestsellers(self, db: Session, *, limit: int = 10, period: str = "month") -> List[Product]:
        """
        Get bestsellers based on order items.
        
        Args:
            db: Database session
            limit: Maximum number of products to return
            period: Time period for bestsellers calculation ("week", "month", "year", "all")
            
        Returns:
            List of bestselling products
        """
        return product_repository.get_bestsellers(db, limit=limit, period=period)

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

    def delete(self, db: Session, *, product_id: uuid.UUID, force: bool = False) -> None:
        """
        Delete a product.
        
        Args:
            db: Database session
            product_id: ID of the product to delete
            force: If True, delete even if product has dependencies
            
        Raises:
            NotFoundException: If product not found
            ValueError: If product has dependencies and force is False
        """
        product = product_repository.get(db, id=product_id)
        if not product:
            raise NotFoundException(detail="Product not found")
            
        # Check for dependencies if not forcing deletion
        if not force:
            # Check if product has order items
            from app.models.order import OrderItem
            order_items = db.query(OrderItem).filter(OrderItem.product_id == product_id).count()
            if order_items > 0:
                raise ValueError(f"Cannot delete product with {order_items} order items. Use force=True to override.")

        # Delete the product (cascades to related entities)
        product_repository.remove(db, id=product_id)

    def update_inventory(
            self, db: Session, *, product_id: uuid.UUID, variant_id: Optional[uuid.UUID], 
            quantity: int, adjustment_type: str = "set"
    ) -> int:
        """
        Update product inventory.
        
        Args:
            db: Database session
            product_id: ID of the product to update
            variant_id: Optional variant ID if updating a specific variant
            quantity: Quantity value for the update
            adjustment_type: Type of adjustment ("set", "add", "subtract")
            
        Returns:
            The updated inventory quantity
            
        Raises:
            NotFoundException: If product or variant not found
            ValueError: If invalid adjustment type or negative quantity would result
        """
        from app.models.inventory import Inventory

        # Check if the product exists
        product = product_repository.get(db, id=product_id)
        if not product:
            raise NotFoundException(detail="Product not found")

        # Validate adjustment type
        if adjustment_type not in ["set", "add", "subtract"]:
            raise ValueError("Invalid adjustment type. Must be 'set', 'add', or 'subtract'")

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
            if adjustment_type != "set":
                # Can't add or subtract from non-existent inventory
                raise ValueError(f"Cannot {adjustment_type} inventory that doesn't exist. Use 'set' instead.")
                
            inventory = Inventory(
                product_id=product_id,
                variant_id=variant_id,
                quantity=quantity
            )
            db.add(inventory)
        else:
            # Update existing inventory based on adjustment type
            if adjustment_type == "set":
                inventory.quantity = quantity
            elif adjustment_type == "add":
                inventory.quantity += quantity
            elif adjustment_type == "subtract":
                if inventory.quantity < quantity:
                    raise ValueError(f"Cannot subtract {quantity} from inventory with only {inventory.quantity} items")
                inventory.quantity -= quantity
                
            db.add(inventory)

        db.commit()
        db.refresh(inventory)
        
        return inventory.quantity

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
    ) -> Tuple[List[Product], int]:
        """
        Search for products by name or description.
        
        Args:
            db: Database session
            query: Search query string
            limit: Maximum number of products to return
            
        Returns:
            Tuple of (products list, total count)
        """
        from sqlalchemy import or_
        from sqlalchemy.orm import joinedload
        
        search_term = f"%{query}%"
        
        # Build the query
        product_query = (
            db.query(Product)
            .filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.sku.ilike(search_term)
                ),
                Product.is_active == True
            )
        )
        
        # Get total count
        total = product_query.count()
        
        # Get products with relations
        products = (
            product_query
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
        
        return products, total

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
        # Check if product exists
        product = product_repository.get(db, id=product_id)
        if not product:
            raise NotFoundException(detail="Product not found")
            
        # Use the repository method to get related products
        return product_repository.get_related_products(
            db, 
            product_id=product_id, 
            limit=limit,
            relation_type=relation_type
        )


product_service = ProductService()
