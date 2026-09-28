from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.repositories import product_repository
from app.schemas.product import ProductCreateRequest, ProductUpdateRequest


async def list_products(db: AsyncSession, *, skip: int = 0, limit: int = 20) -> list[Product]:
    return await product_repository.list_all(db, skip=skip, limit=limit)


async def get_product(db: AsyncSession, product_id: int) -> Product:
    product = await product_repository.get_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


async def create_product(db: AsyncSession, payload: ProductCreateRequest) -> Product:
    return await product_repository.create(
        db, name=payload.name, description=payload.description, price=payload.price, stock=payload.stock
    )


async def update_product(db: AsyncSession, product_id: int, payload: ProductUpdateRequest) -> Product:
    product = await get_product(db, product_id)
    return await product_repository.update(
        db,
        product,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        stock=payload.stock,
    )


async def delete_product(db: AsyncSession, product_id: int) -> None:
    product = await get_product(db, product_id)
    await product_repository.delete(db, product)
