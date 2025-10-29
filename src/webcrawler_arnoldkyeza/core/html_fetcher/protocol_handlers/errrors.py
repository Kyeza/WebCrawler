class UnsupportedContentTypeError(Exception):
    """Exception raised when the fetched content is not of a supported type."""

    def __init__(self, content_type):
        self.content_type = content_type
        super().__init__(f"Unsupported content type: {content_type}")