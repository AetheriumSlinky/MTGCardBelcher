"""Contains different exceptions that can happen during operation."""

class FatalConnectionError(Exception):
    """Fatal error during login."""
    pass


class OperationConnectionException(Exception):
    """Exception during normal operation."""
    pass
