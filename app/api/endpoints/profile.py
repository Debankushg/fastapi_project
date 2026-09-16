from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_language
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services import profile_service

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.put("", response_model=UserResponse)
async def edit_profile(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    user = await profile_service.update_profile(db, current_user, payload)
    return UserResponse.model_validate(user)


@router.post("/image", response_model=UserResponse)
async def upload_profile_image(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    language: str = Depends(get_language),
) -> UserResponse:
    user = await profile_service.update_profile_image(db, current_user, image, language)
    return UserResponse.model_validate(user)
