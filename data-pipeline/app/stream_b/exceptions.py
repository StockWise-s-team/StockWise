class StreamBError(Exception):
    """Base exception for all Stream B components."""

    pass


class CrawlError(StreamBError):
    """Raised when a crawler fails to fetch or parse a page."""

    def __init__(self, url: str, message: str):
        self.url = url
        super().__init__(f"[{url}] {message}")


class TransformError(StreamBError):
    """Raised when a transformer fails to process raw data."""

    def __init__(self, source: str, message: str):
        self.source = source
        super().__init__(f"[{source}] {message}")


class EmbeddingError(StreamBError):
    """Raised when embedding or upsert to Qdrant fails."""

    pass


class SourceMapError(TransformError):
    """Raised when source_name cannot be mapped to a source_id."""

    def __init__(self, source_name: str):
        super().__init__(source_name, f"No source_id found for source_name='{source_name}'")
