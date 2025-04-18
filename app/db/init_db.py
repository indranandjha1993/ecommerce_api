import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import Base, engine
from app.models.user import User

logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """
    Initialize the database with required initial data.
    """
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Create a superuser if it doesn't exist
    create_superuser(db)


def create_superuser(db: Session) -> None:
    """
    Create a superuser if it doesn't exist.
    """
    admin_email = settings.ADMIN_EMAIL
    user = db.query(User).filter(User.email == admin_email).first()

    if not user:
        logger.info(f"Creating superuser with email: {admin_email}")
        user = User(
            email=admin_email,
            password_hash=get_password_hash("admin"),  # Default password - change immediately
            first_name="Admin",
            last_name="User",
            is_active=True,
            is_superuser=True,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        logger.info(f"Superuser created with email: {admin_email}")
    else:
        logger.info(f"Superuser already exists with email: {admin_email}")


def create_initial_data(db: Session) -> None:
    """
    Create initial data for the application.
    This function can be extended to create additional data needed for the application.
    """
    # Create initial categories
    create_categories(db)

    # Create initial brands
    create_brands(db)

    # Create initial products
    create_products(db)


def create_categories(db: Session) -> None:
    """
    Create initial categories for the application.
    """
    from app.models.category import Category

    # Define initial categories - modify as needed
    categories = [
        {"name": "Electronics", "slug": "electronics", "description": "Electronic devices and accessories"},
        {"name": "Clothing", "slug": "clothing", "description": "Apparel and fashion items"},
        {"name": "Home & Garden", "slug": "home-garden", "description": "Home decor and garden supplies"},
        {"name": "Books", "slug": "books", "description": "Books and literature"},
        {"name": "Sports & Outdoors", "slug": "sports-outdoors", "description": "Sports equipment and outdoor gear"},
    ]

    # Create categories if they don't exist
    for category_data in categories:
        category = db.query(Category).filter(Category.slug == category_data["slug"]).first()
        if not category:
            category = Category(**category_data)
            db.add(category)

    db.commit()
    logger.info("Initial categories created")


def create_brands(db: Session) -> None:
    """
    Create initial brands for the application.
    """
    from app.models.brand import Brand

    # Define initial brands - modify as needed
    brands = [
        {"name": "Acme", "slug": "acme", "description": "Quality products since 1950"},
        {"name": "TechGear", "slug": "techgear", "description": "Cutting-edge technology products"},
        {"name": "FashionX", "slug": "fashionx", "description": "Latest fashion trends"},
        {"name": "HomeStyle", "slug": "homestyle", "description": "Beautiful home decor"},
        {"name": "SportsPro", "slug": "sportspro", "description": "Professional sports equipment"},
    ]

    # Create brands if they don't exist
    for brand_data in brands:
        brand = db.query(Brand).filter(Brand.slug == brand_data["slug"]).first()
        if not brand:
            brand = Brand(**brand_data)
            db.add(brand)

    db.commit()
    logger.info("Initial brands created")


def create_products(db: Session) -> None:
    """
    Create initial products for the application.
    """
    from app.models.product import Product
    from app.models.category import Category
    from app.models.brand import Brand

    # Get references to categories and brands
    electronics = db.query(Category).filter(Category.slug == "electronics").first()
    clothing = db.query(Category).filter(Category.slug == "clothing").first()

    techgear = db.query(Brand).filter(Brand.slug == "techgear").first()
    fashionx = db.query(Brand).filter(Brand.slug == "fashionx").first()

    # Define initial products - modify as needed
    products = [
        {
            "name": "Smartphone X",
            "slug": "smartphone-x",
            "description": "Latest smartphone with advanced features",
            "price": 799.99,
            "category_id": electronics.id if electronics else None,
            "brand_id": techgear.id if techgear else None,
            "sku": "SM-X-001",
        },
        {
            "name": "T-Shirt Classic",
            "slug": "t-shirt-classic",
            "description": "Classic cotton t-shirt in various colors",
            "price": 24.99,
            "category_id": clothing.id if clothing else None,
            "brand_id": fashionx.id if fashionx else None,
            "sku": "TS-CL-001",
        },
    ]

    # Create products if they don't exist
    for product_data in products:
        product = db.query(Product).filter(Product.slug == product_data["slug"]).first()
        if not product:
            product = Product(**product_data)
            db.add(product)

    db.commit()
    logger.info("Initial products created")
