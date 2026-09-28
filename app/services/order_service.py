from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.repositories import cart_repository, order_repository, product_repository


async def checkout(db: AsyncSession, user_id: int) -> Order:
    cart = await cart_repository.get_or_create_for_user(db, user_id)
    if not cart.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    order_items = []
    total_amount = Decimal(0)
    for cart_item in cart.items:
        product = await product_repository.get_by_id(db, cart_item.product_id)
        if product is None or cart_item.quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for product '{cart_item.product.name}'",
            )
        order_items.append(
            {"product_id": product.id, "quantity": cart_item.quantity, "unit_price": product.price}
        )
        total_amount += product.price * cart_item.quantity

    for cart_item in cart.items:
        product = await product_repository.get_by_id(db, cart_item.product_id)
        await product_repository.update(db, product, stock=product.stock - cart_item.quantity)

    order = await order_repository.create(db, user_id=user_id, total_amount=total_amount, items=order_items)
    await cart_repository.clear_items(db, cart)
    return order


async def get_order(db: AsyncSession, user_id: int, order_id: int) -> Order:
    order = await order_repository.get_by_id(db, order_id)
    if order is None or order.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


async def list_orders(db: AsyncSession, user_id: int, *, skip: int = 0, limit: int = 20) -> list[Order]:
    return await order_repository.list_for_user(db, user_id, skip=skip, limit=limit)
