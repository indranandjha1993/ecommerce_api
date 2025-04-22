def load_models():
    """
    Load all models.
    This is a centralized function to import all models.
    """
    # First import the BaseModel
    from app.models.base import BaseModel

    # Import all models
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

    # No need to return anything, models are registered with Base when imported
    return None
