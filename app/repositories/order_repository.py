from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem


async def create(db: AsyncSession, *, user_id: int, total_amount, items: list[dict]) -> Order:
    order = Order(user_id=user_id, total_amount=total_amount)
    order.items = [
        OrderItem(product_id=item["product_id"], quantity=item["quantity"], unit_price=item["unit_price"])
        for item in items
    ]
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def get_by_id(db: AsyncSession, order_id: int) -> Order | None:
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()


async def list_for_user(db: AsyncSession, user_id: int, *, skip: int = 0, limit: int = 20) -> list[Order]:
    result = await db.execute(
        select(Order).where(Order.user_id == user_id).order_by(Order.id.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())
