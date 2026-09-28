from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart, CartItem


async def get_by_user_id(db: AsyncSession, user_id: int) -> Cart | None:
    result = await db.execute(select(Cart).where(Cart.user_id == user_id))
    return result.scalar_one_or_none()


async def create_for_user(db: AsyncSession, user_id: int) -> Cart:
    cart = Cart(user_id=user_id)
    db.add(cart)
    await db.commit()
    await db.refresh(cart)
    return cart


async def get_or_create_for_user(db: AsyncSession, user_id: int) -> Cart:
    cart = await get_by_user_id(db, user_id)
    if cart is None:
        cart = await create_for_user(db, user_id)
    return cart


async def get_item(db: AsyncSession, cart_id: int, product_id: int) -> CartItem | None:
    result = await db.execute(
        select(CartItem).where(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
    )
    return result.scalar_one_or_none()


async def add_item(db: AsyncSession, cart_id: int, product_id: int, quantity: int) -> CartItem:
    item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def update_item_quantity(db: AsyncSession, item: CartItem, quantity: int) -> CartItem:
    item.quantity = quantity
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def remove_item(db: AsyncSession, item: CartItem) -> None:
    await db.delete(item)
    await db.commit()


async def clear_items(db: AsyncSession, cart: Cart) -> None:
    for item in list(cart.items):
        await db.delete(item)
    await db.commit()
