class AppError(Exception):
    """Base class for errors services raise. API routes translate these
    into HTTP responses — services themselves know nothing about HTTP.
    `.message` lives here (not repeated per subclass) so every subclass
    gets a safe, user-facing message without redefining __init__."""

    def __init__(self, message: str = "Something went wrong."):
        self.message = message
        super().__init__(message)


class EmailAlreadyRegisteredError(AppError):
    pass


class InvalidCredentialsError(AppError):
    pass


class ImageValidationError(AppError):
    """Wrong format, too large, too small, corrupt file, etc. The
    message is always safe to show directly to the user (Section 36)."""


class NotFoundError(AppError):
    pass


class ValidationError(AppError):
    """Generic "the request is well-formed JSON but doesn't make sense
    for this data" error — e.g. a size that isn't offered for this
    product. Distinct from Pydantic's automatic 422s, which catch
    malformed request shapes before a service ever runs."""


class TryOnGenerationError(AppError):
    """Raised by an AI provider when generation fails. The message is
    safe to store as TryOnJob.failure_reason and show to the user."""
