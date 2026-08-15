"""
Real virtual try-on generation via Gemini 2.5 Flash Image ("nano
banana"), Google's image-editing model. No garment reference photo
exists in the catalog (see docs/50 — never fake real product photos),
so unlike a model such as IDM-VTON this provider works from the
person's photo plus a text description of the garment (name, category,
color) rather than compositing a real garment image.
"""

import base64
import io

import httpx
from PIL import Image

from app.ai.base import GeneratedTryOnImage, VirtualTryOnProvider
from app.core.config import settings
from app.core.exceptions import TryOnGenerationError
from app.models.clothing import Clothing

_MODEL = "gemini-2.5-flash-image"
_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{_MODEL}:generateContent"
_TIMEOUT_SECONDS = 60


class GeminiTryOnProvider(VirtualTryOnProvider):
    name = "gemini"

    def generate_try_on(
        self, person_image_bytes: bytes, clothing: Clothing, selected_color: str
    ) -> GeneratedTryOnImage:
        if not settings.ai_provider_api_key:
            raise TryOnGenerationError("AI provider is not configured (missing API key).")

        prompt = (
            f"Edit this photo so the person is wearing a {selected_color.lower()} "
            f"{clothing.category.lower()} ({clothing.name}). Keep the person's face, "
            "body proportions, pose, and background exactly as they are — only change "
            "the clothing. Make the garment look realistic and naturally fitted, with "
            "correct lighting, shadows, and fabric drape for the pose."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": base64.b64encode(person_image_bytes).decode("ascii"),
                            }
                        },
                    ]
                }
            ],
        }

        try:
            response = httpx.post(
                _ENDPOINT,
                params={"key": settings.ai_provider_api_key},
                json=payload,
                timeout=_TIMEOUT_SECONDS,
            )
        except httpx.HTTPError as exc:
            raise TryOnGenerationError(
                "Couldn't reach the AI provider. Please try again."
            ) from exc

        if response.status_code != 200:
            raise TryOnGenerationError(
                "The AI provider couldn't generate this try-on. Please try again."
            )

        image_bytes = _extract_image(response.json())
        if image_bytes is None:
            raise TryOnGenerationError(
                "The AI provider didn't return an image — it may have declined this "
                "request. Try a different photo or item."
            )

        # Re-encode through Pillow so the stored result is always a
        # consistent JPEG, whatever format the model returned.
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=90)

        return GeneratedTryOnImage(
            image_bytes=buffer.getvalue(),
            provider_name=self.name,
            metadata={"model": _MODEL},
        )


def _extract_image(data: dict) -> bytes | None:
    candidates = data.get("candidates") or []
    for candidate in candidates:
        parts = (candidate.get("content") or {}).get("parts") or []
        for part in parts:
            inline_data = part.get("inline_data") or part.get("inlineData")
            if inline_data and inline_data.get("data"):
                return base64.b64decode(inline_data["data"])
    return None
