"""
docs/03-architecture.md: route handlers and the job-queue logic depend
only on this interface, never on a concrete provider. Swapping providers
is a one-line change in app/ai/registry.py — nothing in app/services or
app/api needs to change.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models.clothing import Clothing


@dataclass
class GeneratedTryOnImage:
    image_bytes: bytes
    provider_name: str
    metadata: dict


class VirtualTryOnProvider(ABC):
    name: str

    @abstractmethod
    def generate_try_on(
        self, person_image_bytes: bytes, clothing: Clothing, selected_color: str
    ) -> GeneratedTryOnImage:
        """
        Raises app.core.exceptions.TryOnGenerationError on failure. The
        caller (tryon_service) is responsible for the job lifecycle
        (status transitions, saving the result) — a provider only ever
        turns inputs into an image or an error.
        """
        raise NotImplementedError
