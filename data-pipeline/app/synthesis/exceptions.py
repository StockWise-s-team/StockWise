class SynthesisError(Exception):
    """Base exception for all synthesis components."""
    pass


class LLMRateLimitError(SynthesisError):
    """Raised when the LLM API returns a rate limit error."""
    pass


class LLMParseError(SynthesisError):
    """Raised when the LLM returns malformed or invalid JSON."""
    pass


class WikiNotFoundError(SynthesisError):
    """Raised when a wiki record cannot be found for a given symbol."""
    pass


class RateLimitExceeded(SynthesisError):
    """Raised when an external API rate limit is hit."""
    pass
