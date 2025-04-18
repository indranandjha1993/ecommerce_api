from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    products,
    categories,
    brands,
    carts,
    orders,
    reviews,
    inventory,
    coupons,
)

api_router = APIRouter()

# Include all API route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(brands.router, prefix="/brands", tags=["Brands"])
api_router.include_router(carts.router, prefix="/carts", tags=["Carts"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(coupons.router, prefix="/coupons", tags=["Coupons"])
