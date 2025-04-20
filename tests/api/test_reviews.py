import pytest
from fastapi.testclient import TestClient


class TestReviewCreation:
    """Tests for review creation functionality."""
    
    def test_create_review(self, client, normal_user_token_headers, db):
        """
        GIVEN an authenticated user and a product
        WHEN the user submits a review for the product
        THEN the review should be created successfully
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        import uuid
        
        # Create test category
        category = Category(
            id=uuid.uuid4(),
            name="Review Category",
            slug="review-category",
            description="Test category for review tests",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=uuid.uuid4(),
            name="Review Brand",
            slug="review-brand",
            description="Test brand for review tests",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=uuid.uuid4(),
            name="Review Product",
            slug="review-product",
            description="Test product for review tests",
            price=99.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True
        )
        db.add(product)
        db.commit()
        
        # Create a review
        review_data = {
            "product_id": str(product.id),
            "rating": 5,
            "content": "This is an excellent product!"
        }
        response = client.post(
            "/api/v1/reviews",
            json=review_data,
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        
        # Verify review data
        assert data["product_id"] == str(product.id)
        assert data["rating"] == 5
        assert data["content"] == review_data["content"]
        assert "id" in data
        assert "user_id" in data


    def test_create_review_invalid_rating(self, client, normal_user_token_headers, db):
        """
        GIVEN an authenticated user and a product
        WHEN the user submits a review with an invalid rating
        THEN a validation error should be returned
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        import uuid
        
        # Create test category
        category = Category(
            id=uuid.uuid4(),
            name="Invalid Rating Category",
            slug="invalid-rating-category",
            description="Test category for invalid rating",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=uuid.uuid4(),
            name="Invalid Rating Brand",
            slug="invalid-rating-brand",
            description="Test brand for invalid rating",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=uuid.uuid4(),
            name="Invalid Rating Product",
            slug="invalid-rating-product",
            description="Test product for invalid rating",
            price=49.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True
        )
        db.add(product)
        db.commit()
        
        # Try to create a review with an invalid rating
        review_data = {
            "product_id": str(product.id),
            "rating": 6,  # Invalid: should be 1-5
            "content": "This is an invalid rating test."
        }
        response = client.post(
            "/api/v1/reviews",
            json=review_data,
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 422  # Validation error


    def test_create_review_nonexistent_product(self, client, normal_user_token_headers):
        """
        GIVEN an authenticated user
        WHEN the user tries to submit a review for a non-existent product
        THEN a 404 Not Found response should be returned
        """
        import uuid
        # Use a valid UUID format that doesn't exist in the database
        nonexistent_uuid = str(uuid.uuid4())
        review_data = {
            "product_id": nonexistent_uuid,
            "rating": 3,
            "content": "This product doesn't exist."
        }
        response = client.post(
            "/api/v1/reviews",
            json=review_data,
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]
        
        # Test case: Invalid UUID format
        review_data["product_id"] = "invalid-uuid"
        response = client.post(
            "/api/v1/reviews",
            json=review_data,
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 422  # Validation error


class TestReviewRetrieval:
    """Tests for review retrieval functionality."""
    
    def test_get_product_reviews(self, client, normal_user_token_headers, db):
        """
        GIVEN a product with approved reviews
        WHEN a request is made to get all reviews for the product
        THEN the reviews should be returned
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        import uuid
        
        # Create test category
        category = Category(
            id=uuid.uuid4(),
            name="Get Reviews Category",
            slug="get-reviews-category",
            description="Test category for getting reviews",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=uuid.uuid4(),
            name="Get Reviews Brand",
            slug="get-reviews-brand",
            description="Test brand for getting reviews",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=uuid.uuid4(),
            name="Get Reviews Product",
            slug="get-reviews-product",
            description="Test product for getting reviews",
            price=29.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True
        )
        db.add(product)
        db.commit()
        
        # Create a review
        review_data = {
            "product_id": str(product.id),
            "rating": 4,
            "content": "This is a good product."
        }
        create_response = client.post(
            "/api/v1/reviews",
            json=review_data,
            headers=normal_user_token_headers
        )
        
        # Manually approve the review in the database
        from app.models.review import Review
        review_id = create_response.json()["id"]
        review = db.query(Review).filter(Review.id == review_id).first()
        review.is_approved = True
        review.moderation_status = "approved"
        db.add(review)
        db.commit()
        
        # Get all reviews for the product
        response = client.get(f"/api/v1/reviews/product/{product.id}")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "items" in data
        assert len(data["items"]) >= 1
        
        # Verify review data
        assert data["items"][0]["product_id"] == str(product.id)
        assert data["items"][0]["rating"] == 4
        assert data["items"][0]["content"] == review_data["content"]


class TestReviewUpdate:
    """Tests for review update functionality."""
    
    def test_update_review(self, client, normal_user_token_headers, db):
        """
        GIVEN an authenticated user with an existing review
        WHEN the user updates their review
        THEN the review should be updated successfully
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        import uuid
        
        # Create test category
        category = Category(
            id=uuid.uuid4(),
            name="Update Review Category",
            slug="update-review-category",
            description="Test category for updating review",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=uuid.uuid4(),
            name="Update Review Brand",
            slug="update-review-brand",
            description="Test brand for updating review",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=uuid.uuid4(),
            name="Update Review Product",
            slug="update-review-product",
            description="Test product for updating review",
            price=19.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True
        )
        db.add(product)
        db.commit()
        
        # Create a review
        review_data = {
            "product_id": str(product.id),
            "rating": 3,
            "content": "This is an average product."
        }
        create_response = client.post(
            "/api/v1/reviews",
            json=review_data,
            headers=normal_user_token_headers
        )
        review_id = create_response.json()["id"]
        
        # Update the review
        update_data = {
            "rating": 5,
            "content": "After using it more, I really love this product!"
        }
        response = client.put(
            f"/api/v1/reviews/{review_id}",
            json=update_data,
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify updated data
        assert data["id"] == review_id
        assert data["rating"] == 5
        assert data["content"] == update_data["content"]
        assert data["product_id"] == str(product.id)


    def test_update_other_user_review(self, client, normal_user_token_headers, superuser_token_headers, db):
        """
        GIVEN an authenticated user and a review created by another user
        WHEN the user tries to update the other user's review
        THEN a 403 Forbidden response should be returned
        """
        # First create a product
        from app.models.product import Product
        from app.models.category import Category
        from app.models.brand import Brand
        from app.models.review import Review
        from app.models.user import User
        import uuid
        
        # Get the superuser
        superuser_response = client.get("/api/v1/users/me", headers=superuser_token_headers)
        superuser_id = superuser_response.json()["id"]
        
        # Create test category
        category = Category(
            id=uuid.uuid4(),
            name="Other User Review Category",
            slug="other-user-review-category",
            description="Test category for other user review",
            is_active=True
        )
        db.add(category)
        
        # Create test brand
        brand = Brand(
            id=uuid.uuid4(),
            name="Other User Review Brand",
            slug="other-user-review-brand",
            description="Test brand for other user review",
            is_active=True
        )
        db.add(brand)
        
        # Create test product
        product = Product(
            id=uuid.uuid4(),
            name="Other User Review Product",
            slug="other-user-review-product",
            description="Test product for other user review",
            price=9.99,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True
        )
        db.add(product)
        
        # Create a review by the superuser directly in the database
        review = Review(
            id=uuid.uuid4(),
            user_id=superuser_id,
            product_id=product.id,
            rating=2,
            content="This is a review by another user."
        )
        db.add(review)
        db.commit()
        
        # Try to update the review as a normal user
        update_data = {
            "rating": 5,
            "content": "Trying to change another user's review."
        }
        response = client.put(
            f"/api/v1/reviews/{review.id}",
            json=update_data,
            headers=normal_user_token_headers
        )
        
        # Verify response
        assert response.status_code == 403
        assert "You can only update your own reviews" in response.json()["detail"]


def test_delete_review(client, normal_user_token_headers, db):
    """Test deleting a review."""
    # First create a product
    from app.models.product import Product
    from app.models.category import Category
    from app.models.brand import Brand
    import uuid
    
    # Create test category
    category = Category(
        id=uuid.uuid4(),
        name="Delete Review Category",
        slug="delete-review-category",
        description="Test category for deleting review",
        is_active=True
    )
    db.add(category)
    
    # Create test brand
    brand = Brand(
        id=uuid.uuid4(),
        name="Delete Review Brand",
        slug="delete-review-brand",
        description="Test brand for deleting review",
        is_active=True
    )
    db.add(brand)
    
    # Create test product
    product = Product(
        id=uuid.uuid4(),
        name="Delete Review Product",
        slug="delete-review-product",
        description="Test product for deleting review",
        price=14.99,
        category_id=category.id,
        brand_id=brand.id,
        is_active=True
    )
    db.add(product)
    db.commit()
    
    # Create a review
    review_data = {
        "product_id": str(product.id),
        "rating": 1,
        "content": "This product is terrible."
    }
    create_response = client.post(
        "/api/v1/reviews",
        json=review_data,
        headers=normal_user_token_headers
    )
    
    # Manually approve the review in the database
    from app.models.review import Review
    review_id = create_response.json()["id"]
    review = db.query(Review).filter(Review.id == review_id).first()
    review.is_approved = True
    review.moderation_status = "approved"
    db.add(review)
    db.commit()
    
    # Delete the review
    response = client.delete(
        f"/api/v1/reviews/{review_id}",
        headers=normal_user_token_headers
    )
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/v1/reviews/product/{product.id}")
    reviews_data = get_response.json()
    if isinstance(reviews_data, dict) and "items" in reviews_data:
        # If the response is paginated
        reviews = reviews_data["items"]
    else:
        # If the response is a direct list
        reviews = reviews_data
    review_ids = [review["id"] for review in reviews]
    assert review_id not in review_ids


def test_review_cache_headers(client, db):
    """Test that review endpoints return appropriate cache headers."""
    # First create a product for testing
    from app.models.product import Product
    from app.models.category import Category
    from app.models.brand import Brand
    import uuid
    
    # Create test category
    category = Category(
        id=uuid.uuid4(),
        name="Cache Test Category",
        slug="cache-test-category",
        description="Test category for cache headers",
        is_active=True
    )
    db.add(category)
    
    # Create test brand
    brand = Brand(
        id=uuid.uuid4(),
        name="Cache Test Brand",
        slug="cache-test-brand",
        description="Test brand for cache headers",
        is_active=True
    )
    db.add(brand)
    
    # Create test product
    product = Product(
        id=uuid.uuid4(),
        name="Cache Test Product",
        slug="cache-test-product",
        description="Test product for cache headers",
        price=24.99,
        category_id=category.id,
        brand_id=brand.id,
        is_active=True
    )
    db.add(product)
    db.commit()
    
    # Test product reviews endpoint
    response = client.get(f"/api/v1/reviews/product/{product.id}")
    assert response.status_code == 200
    assert "Cache-Control" in response.headers
    assert "public" in response.headers["Cache-Control"]
    
    # Test review by ID endpoint (using a UUID that likely doesn't exist)
    # Even though it returns 404, it should still have cache headers
    response = client.get("/api/v1/reviews/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert "Cache-Control" in response.headers
    assert "public" in response.headers["Cache-Control"]