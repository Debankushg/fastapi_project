from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.cart import CartItemAddRequest, CartItemUpdateRequest, CartResponse
from app.services import cart_service

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CartResponse:
    return await cart_service.get_cart(db, current_user.id)


@router.post("/items", response_model=CartResponse)
async def add_item(
    payload: CartItemAddRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CartResponse:
    return await cart_service.add_item(db, current_user.id, payload)


@router.put("/items/{product_id}", response_model=CartResponse)
async def update_item(
    product_id: int,
    payload: CartItemUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CartResponse:
    return await cart_service.update_item(db, current_user.id, product_id, payload)


@router.delete("/items/{product_id}", response_model=CartResponse)
async def remove_item(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CartResponse:
    return await cart_service.remove_item(db, current_user.id, product_id)


@router.delete("", response_model=CartResponse)
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CartResponse:
    return await cart_service.clear_cart(db, current_user.id)
