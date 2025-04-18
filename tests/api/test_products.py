from decimal import Decimal


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
    assert data["price"] == product_data["price"]
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
            created_at=datetime.utcnow()
        ),
        Product(
            name="New Product 2",
            slug="new-product-2",
            price=Decimal("399.99"),
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=1)
        ),
        Product(
            name="Old Product",
            slug="old-product",
            price=Decimal("199.99"),
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=30)
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
