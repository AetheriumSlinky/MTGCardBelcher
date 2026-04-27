"""Contains different exceptions that can happen during operation."""

class LoginException(Exception):
    """Exception during login."""
    pass


class FatalConnectionError(Exception):
    """Fatal error during login."""
    pass


class MainOperationException(Exception):
    """Exception during normal operation."""
    pass
