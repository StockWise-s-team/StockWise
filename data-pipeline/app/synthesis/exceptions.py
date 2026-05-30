class SynthesisError(Exception):
    """Base exception for all synthesis components."""
    pass


class GeminiRateLimitError(SynthesisError):
    """Raised when Gemini API returns a rate limit error."""
    pass


class GeminiParseError(SynthesisError):
    """Raised when Gemini returns malformed or invalid JSON."""
    pass


class WikiNotFoundError(SynthesisError):
    """Raised when a wiki record cannot be found for a given symbol."""
    pass
