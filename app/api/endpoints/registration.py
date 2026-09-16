from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_language
from app.db.session import get_db
from app.schemas.user import UserRegisterRequest, UserResponse
from app.services import user_service

router = APIRouter(tags=["registration"])


@router.post("/registration", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
    language: str = Depends(get_language),
) -> UserResponse:
    user = await user_service.register_user(db, payload, language)
    return UserResponse.model_validate(user)
