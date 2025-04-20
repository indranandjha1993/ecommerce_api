import pytest
from fastapi.testclient import TestClient


class TestInventoryAdministration:
    """Tests for inventory administration operations."""
    
    def test_create_inventory(self, client, superuser_token_headers, db):
        """
        GIVEN a superuser and a product without inventory
        WHEN a request is made to create inventory for the product
        THEN the inventory should be created successfully
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        import uuid
        
        # Create test category
        category = Category(
            id=str(uuid.uuid4()),
            name="Inventory Category",
            slug="inventory-category",
            description="Test category for inventory",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=str(uuid.uuid4()),
            name="Inventory Brand",
            slug="inventory-brand",
            description="Test brand for inventory",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=str(uuid.uuid4()),
            name="Inventory Product",
            slug="inventory-product",
            description="Test product for inventory",
            price=99.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True,
            sku="INV-TEST-001"
        )
        db.add(product)
        db.commit()
        
        # Create inventory
        inventory_data = {
            "product_id": str(product.id),
            "quantity": 100
        }
        response = client.post(
            "/api/v1/inventory",
            json=inventory_data,
            headers=superuser_token_headers
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        
        # Verify inventory data
        assert data["product_id"] == str(product.id)
        assert data["quantity"] == 100
        assert "id" in data


    def test_create_inventory_duplicate_product(self, client, superuser_token_headers, db):
        """
        GIVEN a superuser and a product that already has inventory
        WHEN a request is made to create another inventory for the same product
        THEN a 400 Bad Request response should be returned
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        from app.models.inventory import Inventory
        import uuid
        
        # Create test category
        category = Category(
            id=str(uuid.uuid4()),
            name="Duplicate Inventory Category",
            slug="duplicate-inventory-category",
            description="Test category for duplicate inventory",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=str(uuid.uuid4()),
            name="Duplicate Inventory Brand",
            slug="duplicate-inventory-brand",
            description="Test brand for duplicate inventory",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=str(uuid.uuid4()),
            name="Duplicate Inventory Product",
            slug="duplicate-inventory-product",
            description="Test product for duplicate inventory",
            price=49.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True,
            sku="DUP-INV-001"
        )
        db.add(product)
        
        # Create inventory directly in the database
        inventory = Inventory(
            id=str(uuid.uuid4()),
            product_id=product.id,
            quantity=50
        )
        db.add(inventory)
        db.commit()
        
        # Try to create another inventory for the same product
        inventory_data = {
            "product_id": str(product.id),
            "quantity": 100
        }
        response = client.post(
            "/api/v1/inventory",
            json=inventory_data,
            headers=superuser_token_headers
        )
        
        # Verify response
        assert response.status_code == 400
        assert "Inventory already exists for this product" in response.json()["detail"]


    def test_create_inventory_nonexistent_product(self, client, superuser_token_headers):
        """
        GIVEN a superuser and a non-existent product ID
        WHEN a request is made to create inventory for that product
        THEN a 404 Not Found response should be returned
        """
        import uuid
        nonexistent_id = str(uuid.uuid4())
        inventory_data = {
            "product_id": nonexistent_id,
            "quantity": 100
        }
        response = client.post(
            "/api/v1/inventory",
            json=inventory_data,
            headers=superuser_token_headers
        )
        
        # Verify response
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]


class TestInventoryRetrieval:
    """Tests for inventory retrieval operations."""
    
    def test_get_product_inventory(self, client, superuser_token_headers, db):
        """
        GIVEN a product with inventory in the database
        WHEN a request is made to get that product's inventory
        THEN the inventory details should be returned
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        from app.models.inventory import Inventory
        import uuid
        
        # Create test category
        category = Category(
            id=str(uuid.uuid4()),
            name="Get Inventory Category",
            slug="get-inventory-category",
            description="Test category for getting inventory",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=str(uuid.uuid4()),
            name="Get Inventory Brand",
            slug="get-inventory-brand",
            description="Test brand for getting inventory",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=str(uuid.uuid4()),
            name="Get Inventory Product",
            slug="get-inventory-product",
            description="Test product for getting inventory",
            price=29.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True,
            sku="GET-INV-001"
        )
        db.add(product)
        
        # Create inventory
        inventory = Inventory(
            id=str(uuid.uuid4()),
            product_id=product.id,
            quantity=75
        )
        db.add(inventory)
        db.commit()
        
        # Get the inventory
        response = client.get(f"/api/v1/inventory/product/{product.id}")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify inventory data
        assert data["product_id"] == str(product.id)
        assert data["quantity"] == 75


    def test_get_inventory_nonexistent_product(self, client):
        """
        GIVEN a non-existent product ID
        WHEN a request is made to get inventory for that product
        THEN a 404 Not Found response should be returned
        """
        import uuid
        nonexistent_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/inventory/product/{nonexistent_id}")
        
        # Verify response
        assert response.status_code == 404
        assert "Inventory not found" in response.json()["detail"]


class TestInventoryUpdate:
    """Tests for inventory update operations."""
    
    def test_update_inventory(self, client, superuser_token_headers, db):
        """
        GIVEN a superuser and an existing inventory
        WHEN a request is made to update the inventory quantity
        THEN the inventory should be updated successfully
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        from app.models.inventory import Inventory
        import uuid
        
        # Create test category
        category = Category(
            id=str(uuid.uuid4()),
            name="Update Inventory Category",
            slug="update-inventory-category",
            description="Test category for updating inventory",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=str(uuid.uuid4()),
            name="Update Inventory Brand",
            slug="update-inventory-brand",
            description="Test brand for updating inventory",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=str(uuid.uuid4()),
            name="Update Inventory Product",
            slug="update-inventory-product",
            description="Test product for updating inventory",
            price=19.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True,
            sku="UPD-INV-001"
        )
        db.add(product)
        
        # Create inventory
        inventory = Inventory(
            id=str(uuid.uuid4()),
            product_id=product.id,
            quantity=25
        )
        db.add(inventory)
        db.commit()
        
        # Update the inventory
        update_data = {
            "quantity": 50
        }
        response = client.put(
            f"/api/v1/inventory/{inventory.id}",
            json=update_data,
            headers=superuser_token_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify updated data
        assert data["id"] == str(inventory.id)
        assert data["quantity"] == 50
        assert data["product_id"] == str(product.id)


    def test_update_inventory_not_found(self, client, superuser_token_headers):
        """
        GIVEN a superuser and a non-existent inventory ID
        WHEN a request is made to update the inventory
        THEN a 404 Not Found response should be returned
        """
        import uuid
        nonexistent_id = str(uuid.uuid4())
        update_data = {
            "quantity": 100
        }
        response = client.put(
            f"/api/v1/inventory/{nonexistent_id}",
            json=update_data,
            headers=superuser_token_headers
        )
        
        # Verify response
        assert response.status_code == 404
        assert "Inventory not found" in response.json()["detail"]


    def test_adjust_inventory(self, client, superuser_token_headers, db):
        """
        GIVEN a superuser and an existing inventory
        WHEN requests are made to adjust the inventory quantity
        THEN the inventory should be adjusted successfully
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        from app.models.inventory import Inventory
        import uuid
        
        # Create test category
        category = Category(
            id=str(uuid.uuid4()),
            name="Adjust Inventory Category",
            slug="adjust-inventory-category",
            description="Test category for adjusting inventory",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=str(uuid.uuid4()),
            name="Adjust Inventory Brand",
            slug="adjust-inventory-brand",
            description="Test brand for adjusting inventory",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=str(uuid.uuid4()),
            name="Adjust Inventory Product",
            slug="adjust-inventory-product",
            description="Test product for adjusting inventory",
            price=9.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True,
            sku="ADJ-INV-001"
        )
        db.add(product)
        
        # Create inventory
        inventory = Inventory(
            id=str(uuid.uuid4()),
            product_id=product.id,
            quantity=100
        )
        db.add(inventory)
        db.commit()
        
        # Test case 1: Adjust the inventory (increase)
        adjust_data = {
            "adjustment": 50,
            "reason": "Restocking"
        }
        response = client.post(
            f"/api/v1/inventory/{inventory.id}/adjust",
            json=adjust_data,
            headers=superuser_token_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 150  # 100 + 50
        
        # Test case 2: Adjust the inventory (decrease)
        adjust_data = {
            "adjustment": -30,
            "reason": "Damaged goods"
        }
        response = client.post(
            f"/api/v1/inventory/{inventory.id}/adjust",
            json=adjust_data,
            headers=superuser_token_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 120  # 150 - 30


    def test_adjust_inventory_negative_result(self, client, superuser_token_headers, db):
        """
        GIVEN a superuser and an existing inventory
        WHEN a request is made to adjust the inventory to a negative quantity
        THEN a 400 Bad Request response should be returned
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        from app.models.inventory import Inventory
        import uuid
        
        # Create test category
        category = Category(
            id=str(uuid.uuid4()),
            name="Negative Inventory Category",
            slug="negative-inventory-category",
            description="Test category for negative inventory",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=str(uuid.uuid4()),
            name="Negative Inventory Brand",
            slug="negative-inventory-brand",
            description="Test brand for negative inventory",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=str(uuid.uuid4()),
            name="Negative Inventory Product",
            slug="negative-inventory-product",
            description="Test product for negative inventory",
            price=5.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True,
            sku="NEG-INV-001"
        )
        db.add(product)
        
        # Create inventory
        inventory = Inventory(
            id=str(uuid.uuid4()),
            product_id=product.id,
            quantity=20
        )
        db.add(inventory)
        db.commit()
        
        # Try to adjust the inventory to a negative quantity
        adjust_data = {
            "adjustment": -30,
            "reason": "Excessive reduction"
        }
        response = client.post(
            f"/api/v1/inventory/{inventory.id}/adjust",
            json=adjust_data,
            headers=superuser_token_headers
        )
        
        # Verify response
        assert response.status_code == 400
        assert "Cannot adjust inventory to a negative quantity" in response.json()["detail"]


class TestInventoryPermissions:
    """Tests for inventory permission functionality."""
    
    def test_normal_user_cannot_manage_inventory(self, client, normal_user_token_headers, db):
        """
        GIVEN a normal user
        WHEN the user tries to create inventory
        THEN access should be denied with a 403 Forbidden response
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        import uuid
        
        # Create test category
        category = Category(
            id=str(uuid.uuid4()),
            name="Unauthorized Inventory Category",
            slug="unauthorized-inventory-category",
            description="Test category for unauthorized inventory",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=str(uuid.uuid4()),
            name="Unauthorized Inventory Brand",
            slug="unauthorized-inventory-brand",
            description="Test brand for unauthorized inventory",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=str(uuid.uuid4()),
            name="Unauthorized Inventory Product",
            slug="unauthorized-inventory-product",
            description="Test product for unauthorized inventory",
            price=14.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True,
            sku="UNAUTH-001"
        )
        db.add(product)
        db.commit()
        
        # Try to create inventory as a normal user
        inventory_data = {
            "product_id": str(product.id),
            "quantity": 100
        }
        response = client.post(
            "/api/v1/inventory",
            json=inventory_data,
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 403
        assert "The user doesn't have enough privileges" in response.json()["detail"]