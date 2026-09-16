import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import DEFAULT_LANGUAGE, translate
from app.models.user import User
from app.repositories import user_repository
from app.schemas.user import UserUpdateRequest

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024

UPLOAD_DIR = Path("uploads/profile_images")


async def update_profile(db: AsyncSession, user: User, payload: UserUpdateRequest) -> User:
    fields = payload.model_dump(exclude_unset=True, exclude_none=True)
    return await user_repository.update(db, user, **fields)


async def update_profile_image(
    db: AsyncSession, user: User, image: UploadFile, language: str = DEFAULT_LANGUAGE
) -> User:
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate(language, "profile.image_invalid_type"),
        )

    contents = await image.read()
    if len(contents) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate(language, "profile.image_too_large"),
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    extension = Path(image.filename or "").suffix or ".jpg"
    filename = f"{user.id}_{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / filename
    file_path.write_bytes(contents)

    return await user_repository.update(db, user, profile_image=f"/static/profile_images/{filename}")
