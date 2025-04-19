from decimal import Decimal

from app.utils.datetime_utils import utcnow


def test_list_products(client):
    """
    Test listing products.
    """
    response = client.get("/api/v1/products")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data
    assert isinstance(data["items"], list)


def test_create_product(client, superuser_token_headers, db):
    """
    Test creating a new product.
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
    response = client.post("/api/v1/products", json=product_data, headers=superuser_token_headers)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["slug"] == product_data["slug"]
    assert float(data["price"]) == float(product_data["price"])
    assert data["category_id"] == product_data["category_id"]
    assert data["brand_id"] == product_data["brand_id"]
    assert "id" in data


def test_get_product(client, superuser_token_headers, db):
    """
    Test getting a specific product.
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
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == product.name
    assert data["slug"] == product.slug
    assert float(data["price"]) == float(product.price)
    assert "id" in data


def test_get_product_by_slug(client, db):
    """
    Test getting a product by slug.
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
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == product.name
    assert data["slug"] == product.slug
    assert float(data["price"]) == float(product.price)
    assert str(data["id"]) == str(product.id)


def test_update_product(client, superuser_token_headers, db):
    """
    Test updating a product.
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
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == update_data["name"]
    assert float(data["price"]) == update_data["price"]
    assert data["slug"] == product.slug  # Not updated
    assert str(data["id"]) == str(product.id)


def test_delete_product(client, superuser_token_headers, db):
    """
    Test deleting a product.
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
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/v1/products/{product.id}")
    assert get_response.status_code == 404


def test_product_search(client, db):
    """
    Test searching for products.
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
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Laptop Pro"

    # Test search by category
    response = client.get(f"/api/v1/products?category_id={category.id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 3

    # Test search by price range
    response = client.get("/api/v1/products?min_price=1000&max_price=2000")
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Laptop Pro"


def test_featured_products(client, db):
    """
    Test getting featured products.
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
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    product_names = [p["name"] for p in data]
    assert "Featured Product 1" in product_names
    assert "Featured Product 2" in product_names
    assert "Regular Product" not in product_names


def test_new_arrivals(client, db):
    """
    Test getting new arrivals.
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

    # Get new arrivals (should be ordered by creation date, newest first)
    response = client.get("/api/v1/products/new-arrivals")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 2
    assert data[0]["name"] == "New Product 1"  # Newest product first


def test_bestsellers(client, db):
    """
    Test getting bestseller products.
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
        order_number="TEST-ORDER-1",  # Add required field
        subtotal=Decimal("1000.00"),  # Add required field
        total_amount=Decimal("1000.00"),
        customer_email=user.email,  # Add required field
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
            product_name=products[0].name,  # Add required field
            subtotal=products[0].price * 5,  # Add required field
            total_amount=products[0].price * 5  # Add required field
        ),
        OrderItem(
            order_id=order.id,
            product_id=products[1].id,  # Bestseller 2
            quantity=3,
            unit_price=products[1].price,
            product_name=products[1].name,  # Add required field
            subtotal=products[1].price * 3,  # Add required field
            total_amount=products[1].price * 3  # Add required field
        ),
        OrderItem(
            order_id=order.id,
            product_id=products[2].id,  # Low sales
            quantity=1,
            unit_price=products[2].price,
            product_name=products[2].name,  # Add required field
            subtotal=products[2].price,  # Add required field
            total_amount=products[2].price  # Add required field
        )
    ]
    
    for item in order_items:
        db.add(item)
    
    db.commit()

    # Get bestsellers
    response = client.get("/api/v1/products/bestsellers")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 2
    
    # Check that bestsellers are returned in correct order
    # This assumes the bestseller logic is based on quantity sold
    product_names = [p["name"] for p in data]
    assert "Bestseller Product 1" in product_names
    assert "Bestseller Product 2" in product_names


def test_update_product_inventory(client, superuser_token_headers, db):
    """
    Test updating product inventory.
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
    assert response.status_code == 200
    
    # Verify inventory was updated
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
    assert response.status_code == 200
    
    # Verify inventory was updated
    db.refresh(inventory)
    assert inventory.quantity == 50


def test_related_products(client, db):
    """
    Test getting related products.
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
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) >= 2
    
    # Check that related products are returned
    product_names = [p["name"] for p in data]
    
    # Category products should be included
    assert "Related Category Product 1" in product_names
    assert "Related Category Product 2" in product_names
    
    # Unrelated product should not be included
    assert "Unrelated Product" not in product_names


def test_products_by_category(client, db):
    """
    Test getting products by category.
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
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data
    
    # Check that only products from the specified category are returned
    assert len(data["items"]) == 3
    product_names = [p["name"] for p in data["items"]]
    assert "Category Product 1" in product_names
    assert "Category Product 2" in product_names
    assert "Category Product 3" in product_names
    assert "Other Product" not in product_names


def test_products_by_brand(client, db):
    """
    Test getting products by brand.
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
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data
    
    # Check that only products from the specified brand are returned
    assert len(data["items"]) == 2
    product_names = [p["name"] for p in data["items"]]
    assert "Brand Product 1" in product_names
    assert "Brand Product 2" in product_names
    assert "Other Brand Product" not in product_names
