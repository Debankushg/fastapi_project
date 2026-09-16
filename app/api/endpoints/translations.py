from fastapi import APIRouter, HTTPException, status

from app.core.i18n import SUPPORTED_LANGUAGES, load_content_translations
from app.schemas.translation import TranslationsResponse

router = APIRouter(prefix="/Translations", tags=["translations"])


@router.get("/{code}", response_model=TranslationsResponse)
async def get_translations(code: str) -> TranslationsResponse:
    normalized = code.strip().lower()
    if normalized not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language code '{code}'. Supported: {sorted(SUPPORTED_LANGUAGES)}",
        )

    return TranslationsResponse(load_content_translations(normalized))
