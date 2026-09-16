import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.i18n import DEFAULT_LANGUAGE, translate
from app.core.mail import send_otp_email
from app.core.security import create_access_token, verify_password
from app.repositories import otp_repository, user_repository
from app.schemas.auth import LoginRequest, VerifyOTPRequest


def _generate_otp_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


async def login(db: AsyncSession, payload: LoginRequest, language: str = DEFAULT_LANGUAGE) -> None:
    user = await user_repository.get_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=translate(language, "auth.invalid_credentials"),
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translate(language, "auth.inactive_account"),
        )

    otp_code = _generate_otp_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    await otp_repository.create(db, user_id=user.id, otp_code=otp_code, expires_at=expires_at)

    send_otp_email(
        to=user.email,
        otp_code=otp_code,
        expire_minutes=settings.OTP_EXPIRE_MINUTES,
        language=language,
    )


async def verify_otp(db: AsyncSession, payload: VerifyOTPRequest, language: str = DEFAULT_LANGUAGE) -> str:
    user = await user_repository.get_by_email(db, payload.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=translate(language, "auth.invalid_otp"),
        )

    otp = await otp_repository.get_latest_active(db, user_id=user.id)
    if otp is None or otp.otp_code != payload.otp_code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=translate(language, "auth.invalid_otp"),
        )

    if otp.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=translate(language, "auth.otp_expired"),
        )

    await otp_repository.mark_used(db, otp)

    return create_access_token(subject=str(user.id))
