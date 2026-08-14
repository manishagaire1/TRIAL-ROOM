class AppError(Exception):
    """Base class for errors services raise. API routes translate these
    into HTTP responses — services themselves know nothing about HTTP."""


class EmailAlreadyRegisteredError(AppError):
    pass


class InvalidCredentialsError(AppError):
    pass
