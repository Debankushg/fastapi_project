from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.order import OrderStatus
from app.schemas.product import ProductResponse


class OrderItemResponse(BaseModel):
    id: int
    product: ProductResponse
    quantity: int
    unit_price: Decimal

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    status: OrderStatus
    total_amount: Decimal
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
