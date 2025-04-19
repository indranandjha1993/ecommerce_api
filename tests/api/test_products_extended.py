import pytest
from fastapi.testclient import TestClient


def test_create_product(client, superuser_token_headers, db):
    """Test creating a new product."""
    # First create a category and brand
    from app.models.category import Category
    from app.models.brand import Brand
    import uuid
    
    # Create test category
    category = Category(
        id=str(uuid.uuid4()),
        name="Create Product Category",
        slug="create-product-category",
        description="Test category for creating product",
        is_active=True
    )
    db.add(category)
    
    # Create test brand
    brand = Brand(
        id=str(uuid.uuid4()),
        name="Create Product Brand",
        slug="create-product-brand",
        description="Test brand for creating product",
        is_active=True
    )
    db.add(brand)
    db.commit()
    
    # Create a product
    product_data = {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 99.99,
        "category_id": category.id,
        "brand_id": brand.id,
        "is_active": True
    }
    response = client.post(
        "/api/v1/products",
        json=product_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["description"] == product_data["description"]
    assert data["price"] == product_data["price"]
    assert data["category_id"] == category.id
    assert data["brand_id"] == brand.id
    assert "id" in data


def test_create_product_invalid_category(client, superuser_token_headers, db):
    """Test creating a product with an invalid category."""
    # First create a brand
    from app.models.brand import Brand
    import uuid
    
    # Create test brand
    brand = Brand(
        id=str(uuid.uuid4()),
        name="Invalid Category Brand",
        slug="invalid-category-brand",
        description="Test brand for invalid category",
        is_active=True
    )
    db.add(brand)
    db.commit()
    
    # Try to create a product with an invalid category
    product_data = {
        "name": "Invalid Category Product",
        "description": "This product has an invalid category",
        "price": 49.99,
        "category_id": "999999",
        "brand_id": brand.id,
        "is_active": True
    }
    response = client.post(
        "/api/v1/products",
        json=product_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 404
    assert "Category not found" in response.json()["detail"]


def test_create_product_invalid_brand(client, superuser_token_headers, db):
    """Test creating a product with an invalid brand."""
    # First create a category
    from app.models.category import Category
    import uuid
    
    # Create test category
    category = Category(
        id=str(uuid.uuid4()),
        name="Invalid Brand Category",
        slug="invalid-brand-category",
        description="Test category for invalid brand",
        is_active=True
    )
    db.add(category)
    db.commit()
    
    # Try to create a product with an invalid brand
    product_data = {
        "name": "Invalid Brand Product",
        "description": "This product has an invalid brand",
        "price": 29.99,
        "category_id": category.id,
        "brand_id": "999999",
        "is_active": True
    }
    response = client.post(
        "/api/v1/products",
        json=product_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 404
    assert "Brand not found" in response.json()["detail"]


def test_create_product_negative_price(client, superuser_token_headers, db):
    """Test creating a product with a negative price."""
    # First create a category and brand
    from app.models.category import Category
    from app.models.brand import Brand
    import uuid
    
    # Create test category
    category = Category(
        id=str(uuid.uuid4()),
        name="Negative Price Category",
        slug="negative-price-category",
        description="Test category for negative price",
        is_active=True
    )
    db.add(category)
    
    # Create test brand
    brand = Brand(
        id=str(uuid.uuid4()),
        name="Negative Price Brand",
        slug="negative-price-brand",
        description="Test brand for negative price",
        is_active=True
    )
    db.add(brand)
    db.commit()
    
    # Try to create a product with a negative price
    product_data = {
        "name": "Negative Price Product",
        "description": "This product has a negative price",
        "price": -10.00,
        "category_id": category.id,
        "brand_id": brand.id,
        "is_active": True
    }
    response = client.post(
        "/api/v1/products",
        json=product_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 422  # Validation error


def test_get_products_with_filters(client, db):
    """Test getting products with filters."""
    # First create some products with different categories and brands
    from app.models.product import Product
    from app.models.category import Category
    from app.models.brand import Brand
    import uuid
    
    # Create test categories
    category1 = Category(
        id=str(uuid.uuid4()),
        name="Filter Category 1",
        slug="filter-category-1",
        description="Test category 1 for filtering",
        is_active=True
    )
    db.add(category1)
    
    category2 = Category(
        id=str(uuid.uuid4()),
        name="Filter Category 2",
        slug="filter-category-2",
        description="Test category 2 for filtering",
        is_active=True
    )
    db.add(category2)
    
    # Create test brands
    brand1 = Brand(
        id=str(uuid.uuid4()),
        name="Filter Brand 1",
        slug="filter-brand-1",
        description="Test brand 1 for filtering",
        is_active=True
    )
    db.add(brand1)
    
    brand2 = Brand(
        id=str(uuid.uuid4()),
        name="Filter Brand 2",
        slug="filter-brand-2",
        description="Test brand 2 for filtering",
        is_active=True
    )
    db.add(brand2)
    
    # Create test products
    product1 = Product(
        id=str(uuid.uuid4()),
        name="Filter Product 1",
        description="Test product 1 for filtering",
        price=19.99,
        category_id=category1.id,
        brand_id=brand1.id,
        is_active=True
    )
    db.add(product1)
    
    product2 = Product(
        id=str(uuid.uuid4()),
        name="Filter Product 2",
        description="Test product 2 for filtering",
        price=29.99,
        category_id=category1.id,
        brand_id=brand2.id,
        is_active=True
    )
    db.add(product2)
    
    product3 = Product(
        id=str(uuid.uuid4()),
        name="Filter Product 3",
        description="Test product 3 for filtering",
        price=39.99,
        category_id=category2.id,
        brand_id=brand1.id,
        is_active=True
    )
    db.add(product3)
    
    product4 = Product(
        id=str(uuid.uuid4()),
        name="Filter Product 4",
        description="Test product 4 for filtering",
        price=49.99,
        category_id=category2.id,
        brand_id=brand2.id,
        is_active=False  # Inactive product
    )
    db.add(product4)
    db.commit()
    
    # Test filtering by category
    response = client.get(f"/api/v1/products?category_id={category1.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    product_names = [p["name"] for p in data]
    assert "Filter Product 1" in product_names
    assert "Filter Product 2" in product_names
    
    # Test filtering by brand
    response = client.get(f"/api/v1/products?brand_id={brand1.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    product_names = [p["name"] for p in data]
    assert "Filter Product 1" in product_names
    assert "Filter Product 3" in product_names
    
    # Test filtering by min_price
    response = client.get("/api/v1/products?min_price=30")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    product_names = [p["name"] for p in data]
    assert "Filter Product 3" in product_names
    assert "Filter Product 1" not in product_names
    assert "Filter Product 2" not in product_names
    
    # Test filtering by max_price
    response = client.get("/api/v1/products?max_price=30")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    product_names = [p["name"] for p in data]
    assert "Filter Product 1" in product_names
    assert "Filter Product 2" in product_names
    assert "Filter Product 3" not in product_names
    
    # Test filtering by is_active
    response = client.get("/api/v1/products?is_active=false")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    product_names = [p["name"] for p in data]
    assert "Filter Product 4" in product_names
    
    # Test combined filters
    response = client.get(f"/api/v1/products?category_id={category1.id}&brand_id={brand1.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Filter Product 1"


def test_search_products(client, db):
    """Test searching for products by name or description."""
    # First create some products with searchable names and descriptions
    from app.models.product import Product
    from app.models.category import Category
    from app.models.brand import Brand
    import uuid
    
    # Create test category and brand
    category = Category(
        id=str(uuid.uuid4()),
        name="Search Category",
        slug="search-category",
        description="Test category for searching",
        is_active=True
    )
    db.add(category)
    
    brand = Brand(
        id=str(uuid.uuid4()),
        name="Search Brand",
        slug="search-brand",
        description="Test brand for searching",
        is_active=True
    )
    db.add(brand)
    
    # Create test products
    product1 = Product(
        id=str(uuid.uuid4()),
        name="Smartphone XYZ",
        description="A high-end smartphone with great camera",
        price=999.99,
        category_id=category.id,
        brand_id=brand.id,
        is_active=True
    )
    db.add(product1)
    
    product2 = Product(
        id=str(uuid.uuid4()),
        name="Laptop ABC",
        description="Powerful laptop for professionals",
        price=1499.99,
        category_id=category.id,
        brand_id=brand.id,
        is_active=True
    )
    db.add(product2)
    
    product3 = Product(
        id=str(uuid.uuid4()),
        name="Tablet 123",
        description="Portable tablet with smartphone capabilities",
        price=599.99,
        category_id=category.id,
        brand_id=brand.id,
        is_active=True
    )
    db.add(product3)
    db.commit()
    
    # Test searching by name
    response = client.get("/api/v1/products/search?q=smartphone")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    product_names = [p["name"] for p in data]
    assert "Smartphone XYZ" in product_names
    assert "Tablet 123" in product_names  # Should match description
    assert "Laptop ABC" not in product_names
    
    # Test searching by description
    response = client.get("/api/v1/products/search?q=powerful")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    product_names = [p["name"] for p in data]
    assert "Laptop ABC" in product_names
    assert "Smartphone XYZ" not in product_names
    assert "Tablet 123" not in product_names


def test_update_product(client, superuser_token_headers, db):
    """Test updating a product."""
    # First create a product
    from app.models.product import Product
    from app.models.category import Category
    from app.models.brand import Brand
    import uuid
    
    # Create test category and brand
    category = Category(
        id=str(uuid.uuid4()),
        name="Update Product Category",
        slug="update-product-category",
        description="Test category for updating product",
        is_active=True
    )
    db.add(category)
    
    brand = Brand(
        id=str(uuid.uuid4()),
        name="Update Product Brand",
        slug="update-product-brand",
        description="Test brand for updating product",
        is_active=True
    )
    db.add(brand)
    
    # Create test product
    product = Product(
        id=str(uuid.uuid4()),
        name="Update Product",
        description="Test product for updating",
        price=199.99,
        category_id=category.id,
        brand_id=brand.id,
        is_active=True
    )
    db.add(product)
    db.commit()
    
    # Update the product
    update_data = {
        "name": "Updated Product Name",
        "description": "This is an updated description",
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
    assert data["description"] == update_data["description"]
    assert data["price"] == update_data["price"]
    assert data["id"] == product.id
    assert data["category_id"] == category.id
    assert data["brand_id"] == brand.id


def test_deactivate_product(client, superuser_token_headers, db):
    """Test deactivating a product."""
    # First create a product
    from app.models.product import Product
    from app.models.category import Category
    from app.models.brand import Brand
    import uuid
    
    # Create test category and brand
    category = Category(
        id=str(uuid.uuid4()),
        name="Deactivate Product Category",
        slug="deactivate-product-category",
        description="Test category for deactivating product",
        is_active=True
    )
    db.add(category)
    
    brand = Brand(
        id=str(uuid.uuid4()),
        name="Deactivate Product Brand",
        slug="deactivate-product-brand",
        description="Test brand for deactivating product",
        is_active=True
    )
    db.add(brand)
    
    # Create test product
    product = Product(
        id=str(uuid.uuid4()),
        name="Deactivate Product",
        description="Test product for deactivating",
        price=149.99,
        category_id=category.id,
        brand_id=brand.id,
        is_active=True
    )
    db.add(product)
    db.commit()
    
    # Deactivate the product
    update_data = {
        "is_active": False
    }
    response = client.put(
        f"/api/v1/products/{product.id}",
        json=update_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False
    assert data["id"] == product.id
    
    # Verify it's deactivated but still retrievable
    response = client.get(f"/api/v1/products/{product.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False