from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_language
from app.core.i18n import translate
from app.db.session import get_db
from app.schemas.auth import LoginRequest, LoginResponse, TokenResponse, VerifyOTPRequest
from app.services import auth_service

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
    language: str = Depends(get_language),
) -> LoginResponse:
    await auth_service.login(db, payload, language)
    return LoginResponse(message=translate(language, "auth.otp_sent"))


@router.post("/login/verify-otp", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def verify_otp(
    payload: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db),
    language: str = Depends(get_language),
) -> TokenResponse:
    access_token = await auth_service.verify_otp(db, payload, language)
    return TokenResponse(access_token=access_token)
