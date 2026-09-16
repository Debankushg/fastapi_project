from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.otp import LoginOTP


async def create(db: AsyncSession, *, user_id: int, otp_code: str, expires_at: datetime) -> LoginOTP:
    otp = LoginOTP(user_id=user_id, otp_code=otp_code, expires_at=expires_at)
    db.add(otp)
    await db.commit()
    await db.refresh(otp)
    return otp


async def get_latest_active(db: AsyncSession, *, user_id: int) -> LoginOTP | None:
    result = await db.execute(
        select(LoginOTP)
        .where(LoginOTP.user_id == user_id, LoginOTP.is_used.is_(False))
        .order_by(LoginOTP.created_at.desc())
    )
    return result.scalars().first()


async def mark_used(db: AsyncSession, otp: LoginOTP) -> None:
    otp.is_used = True
    db.add(otp)
    await db.commit()
