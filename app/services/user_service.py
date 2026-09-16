from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import DEFAULT_LANGUAGE, translate
from app.core.security import hash_password
from app.models.user import User
from app.repositories import user_repository
from app.schemas.user import UserRegisterRequest


async def register_user(db: AsyncSession, payload: UserRegisterRequest, language: str = DEFAULT_LANGUAGE) -> User:
    existing_user = await user_repository.get_by_email(db, payload.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=translate(language, "registration.email_exists"),
        )

    return await user_repository.create(
        db,
        name=payload.name,
        email=payload.email,
        address=payload.address,
        hashed_password=hash_password(payload.password),
    )
