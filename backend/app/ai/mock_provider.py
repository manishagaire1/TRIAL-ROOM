"""
Section 50: never pretend a mock AI response is a real AI result. This
provider does real image processing (loads the person's actual photo,
draws a garment-colored overlay, resizes it) so the full upload -> job ->
result pipeline is genuinely exercised end to end — but it visibly
watermarks every image as a mock result so it can never be mistaken for
a real generation, in a screenshot or otherwise.
"""

import io
import time

from PIL import Image, ImageDraw, ImageFont

from app.ai.base import GeneratedTryOnImage, VirtualTryOnProvider
from app.models.clothing import Clothing

MAX_DIMENSION = 800

# Presentation-only color lookup for the mock overlay — the real catalog
# stores color as a plain name (see frontend/src/lib/colorSwatches.ts for
# the frontend's equivalent, independently maintained since one is
# Python and the other TypeScript).
_COLOR_HEX = {
    "black": (24, 24, 27),
    "white": (245, 245, 244),
    "gray": (113, 113, 122),
    "navy": (30, 58, 95),
    "blue": (37, 99, 235),
    "green": (22, 101, 52),
    "red": (185, 28, 28),
    "pink": (219, 39, 119),
    "purple": (126, 34, 206),
    "brown": (120, 53, 15),
    "beige": (214, 199, 161),
    "charcoal": (63, 63, 70),
    "indigo": (44, 62, 107),
    "olive": (75, 83, 32),
}
_FALLBACK_COLOR = (163, 163, 163)


class MockTryOnProvider(VirtualTryOnProvider):
    name = "mock"

    def generate_try_on(
        self, person_image_bytes: bytes, clothing: Clothing, selected_color: str
    ) -> GeneratedTryOnImage:
        # A short delay makes the pending -> processing -> completed
        # states in the UI genuinely observable instead of instant.
        time.sleep(2)

        image = Image.open(io.BytesIO(person_image_bytes)).convert("RGB")
        image.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
        width, height = image.size

        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        band_color = _COLOR_HEX.get(selected_color.lower(), _FALLBACK_COLOR)
        band_top, band_bottom = int(height * 0.25), int(height * 0.75)
        draw.rectangle([0, band_top, width, band_bottom], fill=(*band_color, 110))

        font = ImageFont.load_default(size=max(14, width // 28))
        label = f"{clothing.name} ({selected_color})"
        draw.text((12, band_top + 8), label, fill=(255, 255, 255, 230), font=font)

        watermark_font = ImageFont.load_default(size=max(12, width // 34))
        draw.text(
            (12, height - 28),
            "MOCK AI RESULT - not a real try-on",
            fill=(255, 255, 255, 220),
            font=watermark_font,
        )

        composited = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")

        buffer = io.BytesIO()
        composited.save(buffer, format="JPEG", quality=88)

        return GeneratedTryOnImage(
            image_bytes=buffer.getvalue(),
            provider_name=self.name,
            metadata={"note": "mock provider — no real AI generation occurred"},
        )
