import pytest
from fastapi.testclient import TestClient


def test_create_review(client, normal_user_token_headers, db):
    """Test creating a product review."""
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
    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == str(product.id)
    assert data["rating"] == 5
    assert data["content"] == review_data["content"]
    assert "id" in data
    assert "user_id" in data


def test_create_review_invalid_rating(client, normal_user_token_headers, db):
    """Test creating a review with an invalid rating."""
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
    assert response.status_code == 422  # Validation error


def test_create_review_nonexistent_product(client, normal_user_token_headers):
    """Test creating a review for a non-existent product."""
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
    assert response.status_code == 404
    assert "Product not found" in response.json()["detail"]


def test_get_product_reviews(client, normal_user_token_headers, db):
    """Test getting all reviews for a product."""
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
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "items" in data
    assert len(data["items"]) >= 1
    assert data["items"][0]["product_id"] == str(product.id)
    assert data["items"][0]["rating"] == 4
    assert data["items"][0]["content"] == review_data["content"]


def test_update_review(client, normal_user_token_headers, db):
    """Test updating a review."""
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
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == review_id
    assert data["rating"] == 5
    assert data["content"] == update_data["content"]
    assert data["product_id"] == str(product.id)


def test_update_other_user_review(client, normal_user_token_headers, superuser_token_headers, db):
    """Test updating another user's review."""
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