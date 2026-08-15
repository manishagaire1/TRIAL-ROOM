import base64
import io

import httpx
import pytest
from PIL import Image

from app.ai.gemini_provider import GeminiTryOnProvider
from app.core.config import settings
from app.core.exceptions import TryOnGenerationError


class _FakeClothing:
    name = "Classic Oxford Shirt"
    category = "Shirt"


def _person_jpeg_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (400, 600), color=(120, 120, 120)).save(buffer, format="JPEG")
    return buffer.getvalue()


def _fake_image_response(image_format="PNG"):
    buffer = io.BytesIO()
    Image.new("RGB", (400, 600), color=(10, 20, 30)).save(buffer, format=image_format)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return {
        "candidates": [
            {"content": {"parts": [{"inline_data": {"mime_type": "image/png", "data": encoded}}]}}
        ]
    }


@pytest.fixture(autouse=True)
def _api_key(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider_api_key", "test-key")


def test_raises_without_api_key(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider_api_key", "")
    provider = GeminiTryOnProvider()
    with pytest.raises(TryOnGenerationError, match="not configured"):
        provider.generate_try_on(_person_jpeg_bytes(), _FakeClothing(), "navy")


def test_returns_generated_image_on_success(monkeypatch):
    def fake_post(url, params, json, timeout):
        return httpx.Response(200, json=_fake_image_response())

    monkeypatch.setattr("app.ai.gemini_provider.httpx.post", fake_post)
    provider = GeminiTryOnProvider()
    result = provider.generate_try_on(_person_jpeg_bytes(), _FakeClothing(), "navy")

    assert result.provider_name == "gemini"
    reopened = Image.open(io.BytesIO(result.image_bytes))
    assert reopened.format == "JPEG"


def test_raises_on_non_200_response(monkeypatch):
    def fake_post(url, params, json, timeout):
        return httpx.Response(400, json={"error": "bad request"})

    monkeypatch.setattr("app.ai.gemini_provider.httpx.post", fake_post)
    provider = GeminiTryOnProvider()
    with pytest.raises(TryOnGenerationError):
        provider.generate_try_on(_person_jpeg_bytes(), _FakeClothing(), "navy")


def test_raises_on_transport_error(monkeypatch):
    def fake_post(url, params, json, timeout):
        raise httpx.ConnectError("boom")

    monkeypatch.setattr("app.ai.gemini_provider.httpx.post", fake_post)
    provider = GeminiTryOnProvider()
    with pytest.raises(TryOnGenerationError, match="Couldn't reach"):
        provider.generate_try_on(_person_jpeg_bytes(), _FakeClothing(), "navy")


def test_raises_when_no_image_in_response(monkeypatch):
    def fake_post(url, params, json, timeout):
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "declined"}]}}]})

    monkeypatch.setattr("app.ai.gemini_provider.httpx.post", fake_post)
    provider = GeminiTryOnProvider()
    with pytest.raises(TryOnGenerationError, match="didn't return an image"):
        provider.generate_try_on(_person_jpeg_bytes(), _FakeClothing(), "navy")
