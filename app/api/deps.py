from fastapi import Cookie, Depends, Header, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import LANGUAGE_COOKIE_NAME, resolve_language, translate
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories import user_repository

bearer_scheme = HTTPBearer()


async def get_language(
    lang: str | None = Query(default=None, description="Language code: en, nl, or de"),
    accept_language: str | None = Header(default=None),
    lang_cookie: str | None = Cookie(default=None, alias=LANGUAGE_COOKIE_NAME),
) -> str:
    preferred = lang or (accept_language.split(",")[0] if accept_language else None) or lang_cookie
    return resolve_language(preferred)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
    language: str = Depends(get_language),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=translate(language, "auth.credentials_error"),
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = int(decode_access_token(credentials.credentials))
    except ValueError:
        raise credentials_error

    user = await user_repository.get_by_id(db, user_id)
    if user is None:
        raise credentials_error

    return user
