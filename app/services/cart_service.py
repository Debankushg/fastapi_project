from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart
from app.repositories import cart_repository, product_repository
from app.schemas.cart import CartItemAddRequest, CartItemUpdateRequest, CartResponse


def _to_response(cart: Cart) -> CartResponse:
    total = sum((item.product.price * item.quantity for item in cart.items), Decimal(0))
    return CartResponse(
        id=cart.id,
        items=cart.items,
        total=total,
        created_at=cart.created_at,
        updated_at=cart.updated_at,
    )


async def get_cart(db: AsyncSession, user_id: int) -> CartResponse:
    cart = await cart_repository.get_or_create_for_user(db, user_id)
    return _to_response(cart)


async def add_item(db: AsyncSession, user_id: int, payload: CartItemAddRequest) -> CartResponse:
    product = await product_repository.get_by_id(db, payload.product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    cart = await cart_repository.get_or_create_for_user(db, user_id)
    existing_item = await cart_repository.get_item(db, cart.id, payload.product_id)

    new_quantity = payload.quantity + (existing_item.quantity if existing_item else 0)
    if new_quantity > product.stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock available")

    if existing_item:
        await cart_repository.update_item_quantity(db, existing_item, new_quantity)
    else:
        await cart_repository.add_item(db, cart.id, payload.product_id, payload.quantity)

    await db.refresh(cart, attribute_names=["items"])
    return _to_response(cart)


async def update_item(db: AsyncSession, user_id: int, product_id: int, payload: CartItemUpdateRequest) -> CartResponse:
    cart = await cart_repository.get_or_create_for_user(db, user_id)
    item = await cart_repository.get_item(db, cart.id, product_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in cart")

    if payload.quantity > item.product.stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock available")

    await cart_repository.update_item_quantity(db, item, payload.quantity)
    await db.refresh(cart, attribute_names=["items"])
    return _to_response(cart)


async def remove_item(db: AsyncSession, user_id: int, product_id: int) -> CartResponse:
    cart = await cart_repository.get_or_create_for_user(db, user_id)
    item = await cart_repository.get_item(db, cart.id, product_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in cart")

    await cart_repository.remove_item(db, item)
    await db.refresh(cart, attribute_names=["items"])
    return _to_response(cart)


async def clear_cart(db: AsyncSession, user_id: int) -> CartResponse:
    cart = await cart_repository.get_or_create_for_user(db, user_id)
    await cart_repository.clear_items(db, cart)
    await db.refresh(cart, attribute_names=["items"])
    return _to_response(cart)
