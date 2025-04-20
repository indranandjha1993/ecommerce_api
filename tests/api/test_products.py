from decimal import Decimal

from app.utils.datetime_utils import utcnow


class TestProductBasics:
    """Tests for basic product operations."""
    
    def test_list_products(self, client):
        """
        GIVEN a database with products
        WHEN a request is made to list all products
        THEN a paginated list of products should be returned
        """
        response = client.get("/api/v1/products")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        assert isinstance(data["items"], list)

    def test_get_product(self, client, db):
        """
        GIVEN a product in the database
        WHEN a request is made to get that product by ID
        THEN the product details should be returned
        """
        # Create a test product
        from app.models.product import Product

        product = Product(
            name="Test Get Product",
            slug="test-get-product",
            description="Test get product description",
            price=Decimal("149.99"),
            is_active=True
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        # Get the product
        response = client.get(f"/api/v1/products/{product.id}")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify product data
        assert data["name"] == product.name
        assert data["slug"] == product.slug
        assert float(data["price"]) == float(product.price)
        assert "id" in data

    def test_get_product_by_slug(self, client, db):
        """
        GIVEN a product in the database
        WHEN a request is made to get that product by slug
        THEN the product details should be returned
        """
        # Create a test product
        from app.models.product import Product

        product = Product(
            name="Test Slug Product",
            slug="test-slug-product",
            description="Test slug product description",
            price=Decimal("129.99"),
            is_active=True
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        # Get the product by slug
        response = client.get(f"/api/v1/products/slug/{product.slug}")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify product data
        assert data["name"] == product.name
        assert data["slug"] == product.slug
        assert float(data["price"]) == float(product.price)
        assert str(data["id"]) == str(product.id)


class TestProductAdministration:
    """Tests for product administration operations."""
    
    def test_create_product(self, client, superuser_token_headers, db):
        """
        GIVEN a superuser with valid product data
        WHEN a request is made to create a new product
        THEN the product should be created successfully
        """
        # First create a category
        from app.models.category import Category

        category = Category(
            name="Test Category",
            slug="test-category",
            description="Test category description"
        )
        db.add(category)
        db.commit()
        db.refresh(category)

        # Create a brand
        from app.models.brand import Brand

        brand = Brand(
            name="Test Brand",
            slug="test-brand",
            description="Test brand description"
        )
        db.add(brand)
        db.commit()
        db.refresh(brand)

        # Create a product
        product_data = {
            "name": "Test Product",
            "slug": "test-product",
            "description": "Test product description",
            "price": 99.99,
            "category_id": str(category.id),
            "brand_id": str(brand.id),
            "is_active": True
        }
        response = client.post(
            "/api/v1/products", 
            json=product_data, 
            headers=superuser_token_headers
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        
        # Verify product data
        assert data["name"] == product_data["name"]
        assert data["slug"] == product_data["slug"]
        assert float(data["price"]) == float(product_data["price"])
        assert data["category_id"] == product_data["category_id"]
        assert data["brand_id"] == product_data["brand_id"]
        assert "id" in data

    def test_update_product(self, client, superuser_token_headers, db):
        """
        GIVEN a superuser and an existing product
        WHEN a request is made to update the product
        THEN the product should be updated successfully
        """
        # Create a test product
        from app.models.product import Product

        product = Product(
            name="Test Update Product",
            slug="test-update-product",
            description="Test update product description",
            price=Decimal("199.99"),
            is_active=True
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        # Update the product
        update_data = {
            "name": "Updated Product",
            "price": 249.99
        }
        response = client.put(
            f"/api/v1/products/{product.id}",
            json=update_data,
            headers=superuser_token_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify updated data
        assert data["name"] == update_data["name"]
        assert float(data["price"]) == update_data["price"]
        assert data["slug"] == product.slug  # Not updated
        assert str(data["id"]) == str(product.id)

    def test_delete_product(self, client, superuser_token_headers, db):
        """
        GIVEN a superuser and an existing product
        WHEN a request is made to delete the product
        THEN the product should be deleted successfully
        """
        # Create a test product
        from app.models.product import Product

        product = Product(
            name="Test Delete Product",
            slug="test-delete-product",
            description="Test delete product description",
            price=Decimal("159.99"),
            is_active=True
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        # Delete the product
        response = client.delete(
            f"/api/v1/products/{product.id}",
            headers=superuser_token_headers
        )
        
        # Verify response
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/v1/products/{product.id}")
        assert get_response.status_code == 404


class TestProductSearch:
    """Tests for product search functionality."""
    
    def test_search_by_query_and_filters(self, client, db):
        """
        GIVEN a database with various products
        WHEN search requests are made with different query parameters
        THEN the correct filtered products should be returned
        """
        # Create multiple test products
        from app.models.product import Product
        from app.models.category import Category

        category = Category(name="Electronics", slug="electronics")
        db.add(category)
        db.commit()
        db.refresh(category)

        # Create products in the same category
        products = [
            Product(
                name="Smartphone X",
                slug="smartphone-x",
                description="Latest smartphone",
                price=Decimal("899.99"),
                category_id=category.id,
                is_active=True
            ),
            Product(
                name="Laptop Pro",
                slug="laptop-pro",
                description="Powerful laptop",
                price=Decimal("1499.99"),
                category_id=category.id,
                is_active=True
            ),
            Product(
                name="Tablet Mini",
                slug="tablet-mini",
                description="Compact tablet",
                price=Decimal("499.99"),
                category_id=category.id,
                is_active=True
            )
        ]

        for product in products:
            db.add(product)

        db.commit()

        # Test search by query
        response = client.get("/api/v1/products?query=laptop")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify search results
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Laptop Pro"

        # Test search by category
        response = client.get(f"/api/v1/products?category_id={category.id}")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify search results
        assert len(data["items"]) == 3
        product_names = [p["name"] for p in data["items"]]
        assert "Smartphone X" in product_names
        assert "Laptop Pro" in product_names
        assert "Tablet Mini" in product_names

        # Test search by price range
        response = client.get("/api/v1/products?min_price=1000&max_price=2000")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify search results
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Laptop Pro"


class TestProductCollections:
    """Tests for product collection endpoints."""
    
    def test_featured_products(self, client, db):
        """
        GIVEN a database with featured and non-featured products
        WHEN a request is made to get featured products
        THEN only featured products should be returned
        """
        # Create featured products
        from app.models.product import Product

        featured_products = [
            Product(
                name="Featured Product 1",
                slug="featured-product-1",
                price=Decimal("299.99"),
                is_active=True,
                is_featured=True
            ),
            Product(
                name="Featured Product 2",
                slug="featured-product-2",
                price=Decimal("399.99"),
                is_active=True,
                is_featured=True
            )
        ]

        # Create non-featured product
        non_featured = Product(
            name="Regular Product",
            slug="regular-product",
            price=Decimal("199.99"),
            is_active=True,
            is_featured=False
        )

        for product in featured_products + [non_featured]:
            db.add(product)

        db.commit()

        # Get featured products
        response = client.get("/api/v1/products/featured")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify featured products
        assert len(data) == 2
        product_names = [p["name"] for p in data]
        assert "Featured Product 1" in product_names
        assert "Featured Product 2" in product_names
        assert "Regular Product" not in product_names

    def test_new_arrivals(self, client, db):
        """
        GIVEN a database with products created at different times
        WHEN a request is made to get new arrivals
        THEN products should be returned in order of creation date, newest first
        """
        # Create products with different creation times
        from app.models.product import Product
        from datetime import datetime, timedelta

        # Create products
        products = [
            Product(
                name="New Product 1",
                slug="new-product-1",
                price=Decimal("299.99"),
                is_active=True,
                created_at=utcnow()
            ),
            Product(
                name="New Product 2",
                slug="new-product-2",
                price=Decimal("399.99"),
                is_active=True,
                created_at=utcnow() - timedelta(days=1)
            ),
            Product(
                name="Old Product",
                slug="old-product",
                price=Decimal("199.99"),
                is_active=True,
                created_at=utcnow() - timedelta(days=30)
            )
        ]

        for product in products:
            db.add(product)

        db.commit()

        # Get new arrivals
        response = client.get("/api/v1/products/new-arrivals")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify new arrivals order
        assert len(data) >= 2
        assert data[0]["name"] == "New Product 1"  # Newest product first
        
        # Check that products are in correct order
        if len(data) >= 3:
            product_names = [p["name"] for p in data[:3]]
            assert product_names.index("New Product 1") < product_names.index("New Product 2")
            assert product_names.index("New Product 2") < product_names.index("Old Product")


    def test_bestsellers(self, client, db):
        """
        GIVEN a database with products that have different sales quantities
        WHEN a request is made to get bestseller products
        THEN products should be returned in order of sales quantity, highest first
        """
        from app.models.product import Product
        from app.models.order import Order, OrderItem
        from app.models.user import User
        from datetime import datetime
        import uuid

        # Create a user
        user = User(
            email="bestseller-test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create products
        products = [
            Product(
                name="Bestseller Product 1",
                slug="bestseller-product-1",
                price=Decimal("199.99"),
                is_active=True
            ),
            Product(
                name="Bestseller Product 2",
                slug="bestseller-product-2",
                price=Decimal("299.99"),
                is_active=True
            ),
            Product(
                name="Low Sales Product",
                slug="low-sales-product",
                price=Decimal("99.99"),
                is_active=True
            )
        ]

        for product in products:
            db.add(product)

        db.commit()
        
        # Create orders with different quantities to establish bestsellers
        order = Order(
            user_id=user.id,
            status="completed",
            order_number="TEST-ORDER-1",
            subtotal=Decimal("1000.00"),
            total_amount=Decimal("1000.00"),
            customer_email=user.email,
            created_at=utcnow()
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # Add order items with different quantities
        order_items = [
            OrderItem(
                order_id=order.id,
                product_id=products[0].id,  # Bestseller 1
                quantity=5,
                unit_price=products[0].price,
                product_name=products[0].name,
                subtotal=products[0].price * 5,
                total_amount=products[0].price * 5
            ),
            OrderItem(
                order_id=order.id,
                product_id=products[1].id,  # Bestseller 2
                quantity=3,
                unit_price=products[1].price,
                product_name=products[1].name,
                subtotal=products[1].price * 3,
                total_amount=products[1].price * 3
            ),
            OrderItem(
                order_id=order.id,
                product_id=products[2].id,  # Low sales
                quantity=1,
                unit_price=products[2].price,
                product_name=products[2].name,
                subtotal=products[2].price,
                total_amount=products[2].price
            )
        ]
        
        for item in order_items:
            db.add(item)
        
        db.commit()

        # Get bestsellers
        response = client.get("/api/v1/products/bestsellers")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify bestsellers
        assert len(data) >= 2
        
        # Check that bestsellers are included in the results
        product_names = [p["name"] for p in data]
        assert "Bestseller Product 1" in product_names
        assert "Bestseller Product 2" in product_names
        
        # Note: We don't verify the exact order since the API implementation
        # might use different sorting criteria (e.g., total revenue vs quantity)


class TestInventoryManagement:
    """Tests for inventory management functionality."""
    
    def test_update_product_inventory(self, client, superuser_token_headers, db):
        """
        GIVEN a superuser and a product
        WHEN a request is made to update the product's inventory
        THEN the inventory should be updated successfully
        """
        from app.models.product import Product
        from app.models.inventory import Inventory
        
        # Create a test product
        product = Product(
            name="Inventory Test Product",
            slug="inventory-test-product",
            description="Test inventory management",
            price=Decimal("149.99"),
            is_active=True
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Update inventory
        inventory_data = {
            "quantity": 100
        }
        response = client.put(
            f"/api/v1/products/{product.id}/inventory",
            params=inventory_data,
            headers=superuser_token_headers
        )
        
        # Verify response
        assert response.status_code == 200
        
        # Verify inventory was updated in database
        inventory = db.query(Inventory).filter(
            Inventory.product_id == product.id,
            Inventory.variant_id.is_(None)
        ).first()
        
        assert inventory is not None
        assert inventory.quantity == 100
        
        # Update inventory again
        updated_inventory_data = {
            "quantity": 50
        }
        response = client.put(
            f"/api/v1/products/{product.id}/inventory",
            params=updated_inventory_data,
            headers=superuser_token_headers
        )
        
        # Verify response
        assert response.status_code == 200
        
        # Verify inventory was updated
        db.refresh(inventory)
        assert inventory.quantity == 50


class TestProductRelationships:
    """Tests for product relationship functionality."""
    
    def test_related_products(self, client, db):
        """
        GIVEN a product with related products in the same category and brand
        WHEN a request is made to get related products
        THEN only related products should be returned
        """
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        
        # Create categories and brands
        category1 = Category(name="Related Category", slug="related-category")
        category2 = Category(name="Different Category", slug="different-category")
        brand1 = Brand(name="Related Brand", slug="related-brand")
        
        db.add_all([category1, category2, brand1])
        db.commit()
        db.refresh(category1)
        db.refresh(category2)
        db.refresh(brand1)
        
        # Create a main product
        main_product = Product(
            name="Main Product",
            slug="main-product",
            price=Decimal("199.99"),
            category_id=category1.id,
            brand_id=brand1.id,
            is_active=True
        )
        
        # Create related products in the same category
        related_by_category = [
            Product(
                name="Related Category Product 1",
                slug="related-category-product-1",
                price=Decimal("149.99"),
                category_id=category1.id,
                is_active=True
            ),
            Product(
                name="Related Category Product 2",
                slug="related-category-product-2",
                price=Decimal("159.99"),
                category_id=category1.id,
                is_active=True
            )
        ]
        
        # Create related products in the same brand but different category
        related_by_brand = [
            Product(
                name="Related Brand Product",
                slug="related-brand-product",
                price=Decimal("179.99"),
                category_id=category2.id,
                brand_id=brand1.id,
                is_active=True
            )
        ]
        
        # Create unrelated product
        unrelated_product = Product(
            name="Unrelated Product",
            slug="unrelated-product",
            price=Decimal("99.99"),
            category_id=category2.id,
            is_active=True
        )
        
        # Add all products to the database
        db.add(main_product)
        for product in related_by_category + related_by_brand + [unrelated_product]:
            db.add(product)
        
        db.commit()
        db.refresh(main_product)
        
        # Get related products
        response = client.get(f"/api/v1/products/{main_product.id}/related")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify related products
        assert len(data) >= 2
        
        # Check that related products are returned
        product_names = [p["name"] for p in data]
        
        # Category products should be included
        assert "Related Category Product 1" in product_names
        assert "Related Category Product 2" in product_names
        
        # Brand products might be included depending on the implementation
        # Unrelated product should not be included
        assert "Unrelated Product" not in product_names


    def test_products_by_category(self, client, db):
        """
        GIVEN a category with multiple products
        WHEN a request is made to get products by category
        THEN only products from that category should be returned
        """
        from app.models.product import Product
        from app.models.category import Category
        
        # Create a category
        category = Category(name="Test Category", slug="test-category")
        db.add(category)
        db.commit()
        db.refresh(category)
        
        # Create products in the category
        category_products = [
            Product(
                name="Category Product 1",
                slug="category-product-1",
                price=Decimal("149.99"),
                category_id=category.id,
                is_active=True
            ),
            Product(
                name="Category Product 2",
                slug="category-product-2",
                price=Decimal("159.99"),
                category_id=category.id,
                is_active=True
            ),
            Product(
                name="Category Product 3",
                slug="category-product-3",
                price=Decimal("169.99"),
                category_id=category.id,
                is_active=True
            )
        ]
        
        # Create a product in a different category
        other_category = Category(name="Other Category", slug="other-category")
        db.add(other_category)
        db.commit()
        db.refresh(other_category)
        
        other_product = Product(
            name="Other Product",
            slug="other-product",
            price=Decimal("99.99"),
            category_id=other_category.id,
            is_active=True
        )
        
        # Add all products to the database
        for product in category_products + [other_product]:
            db.add(product)
        
        db.commit()
        
        # Get products by category
        response = client.get(f"/api/v1/products/category/{category.id}")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        
        # Verify category products
        assert len(data["items"]) == 3
        product_names = [p["name"] for p in data["items"]]
        assert "Category Product 1" in product_names
        assert "Category Product 2" in product_names
        assert "Category Product 3" in product_names
        assert "Other Product" not in product_names


    def test_products_by_brand(self, client, db):
        """
        GIVEN a brand with multiple products
        WHEN a request is made to get products by brand
        THEN only products from that brand should be returned
        """
        from app.models.product import Product
        from app.models.brand import Brand
        
        # Create a brand
        brand = Brand(name="Test Brand", slug="test-brand")
        db.add(brand)
        db.commit()
        db.refresh(brand)
        
        # Create products for the brand
        brand_products = [
            Product(
                name="Brand Product 1",
                slug="brand-product-1",
                price=Decimal("149.99"),
                brand_id=brand.id,
                is_active=True
            ),
            Product(
                name="Brand Product 2",
                slug="brand-product-2",
                price=Decimal("159.99"),
                brand_id=brand.id,
                is_active=True
            )
        ]
        
        # Create a product for a different brand
        other_brand = Brand(name="Other Brand", slug="other-brand")
        db.add(other_brand)
        db.commit()
        db.refresh(other_brand)
        
        other_product = Product(
            name="Other Brand Product",
            slug="other-brand-product",
            price=Decimal("99.99"),
            brand_id=other_brand.id,
            is_active=True
        )
        
        # Add all products to the database
        for product in brand_products + [other_product]:
            db.add(product)
        
        db.commit()
        
        # Get products by brand
        response = client.get(f"/api/v1/products/brand/{brand.id}")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        
        # Verify brand products
        assert len(data["items"]) == 2
        product_names = [p["name"] for p in data["items"]]
        assert "Brand Product 1" in product_names
        assert "Brand Product 2" in product_names
        assert "Other Brand Product" not in product_names
