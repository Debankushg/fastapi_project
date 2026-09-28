from fastapi import APIRouter

from app.api.endpoints import (
    auth,
    cart,
    orders,
    products,
    profile,
    registration,
    translations,
)

api_router = APIRouter()
api_router.include_router(registration.router)
api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(translations.router)
api_router.include_router(products.router)
api_router.include_router(cart.router)
api_router.include_router(orders.router)
