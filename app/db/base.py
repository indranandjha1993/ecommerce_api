from app.models.address import Address  # noqa
from app.models.cart import Cart, CartItem  # noqa
from app.models.category import Category  # noqa
from app.models.coupon import Coupon  # noqa
from app.models.inventory import Inventory  # noqa
from app.models.order import Order, OrderItem  # noqa
from app.models.payment import Payment  # noqa
from app.models.product import Product, ProductImage, ProductAttribute, ProductAttributeValue  # noqa
from app.models.product_variant import ProductVariant, ProductVariantAttribute  # noqa
from app.models.review import Review  # noqa
from app.models.shipping import Shipping  # noqa
# Import all models here to ensure they are registered with SQLAlchemy
from app.models.user import User  # noqa

from app.db.session import Base  # noqa
