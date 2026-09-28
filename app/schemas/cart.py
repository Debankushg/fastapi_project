from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.product import ProductResponse


class CartItemAddRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, default=1)


class CartItemUpdateRequest(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    id: int
    product: ProductResponse
    quantity: int

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse]
    total: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
