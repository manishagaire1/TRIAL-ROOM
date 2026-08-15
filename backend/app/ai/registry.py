from app.ai.base import VirtualTryOnProvider
from app.ai.gemini_provider import GeminiTryOnProvider
from app.ai.mock_provider import MockTryOnProvider
from app.core.config import settings

# Section 13: adding a real provider later means writing one new class
# implementing VirtualTryOnProvider and adding one line here — nothing
# in tryon_service.py or app/api/tryon.py changes.
_PROVIDERS: dict[str, type[VirtualTryOnProvider]] = {
    "mock": MockTryOnProvider,
    "gemini": GeminiTryOnProvider,
}


def get_provider() -> VirtualTryOnProvider:
    provider_cls = _PROVIDERS.get(settings.ai_provider)
    if provider_cls is None:
        raise NotImplementedError(
            f"AI_PROVIDER={settings.ai_provider!r} has no implementation yet. "
            f"Available: {list(_PROVIDERS)}"
        )
    return provider_cls()
