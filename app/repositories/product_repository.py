from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


async def get_by_id(db: AsyncSession, product_id: int) -> Product | None:
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


async def list_all(db: AsyncSession, *, skip: int = 0, limit: int = 20) -> list[Product]:
    result = await db.execute(select(Product).order_by(Product.id).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create(db: AsyncSession, *, name: str, description: str | None, price, stock: int) -> Product:
    product = Product(name=name, description=description, price=price, stock=stock)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def update(db: AsyncSession, product: Product, **fields) -> Product:
    for key, value in fields.items():
        if value is not None:
            setattr(product, key, value)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def delete(db: AsyncSession, product: Product) -> None:
    await db.delete(product)
    await db.commit()
