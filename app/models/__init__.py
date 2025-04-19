def load_models():
    """
    Load all models and configure their relationships.
    This is a centralized function to import all models in the correct order.
    """
    # First import the Base
    from app.db.session import Base

    # Import all models - order doesn't matter for table definitions
    from app.models.user import User
    from app.models.address import Address
    from app.models.brand import Brand
    from app.models.category import Category
    from app.models.product import Product, ProductImage, ProductAttribute, ProductAttributeValue
    from app.models.product_variant import ProductVariant, ProductVariantAttribute
    from app.models.cart import Cart, CartItem
    from app.models.order import Order, OrderItem
    from app.models.payment import Payment
    from app.models.shipping import Shipping, ShipmentPackage, ShipmentItem
    from app.models.coupon import Coupon, CouponUsage
    from app.models.review import Review, ReviewReply
    from app.models.inventory import Inventory, InventoryLocation, StockMovement

    # Configure relationships after all models are imported
    from app.models.relationships import configure_relationships
    configure_relationships()

    return Base
