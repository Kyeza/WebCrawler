class InvalidSeedUrlError(Exception):
    """Raised when a provided seed URL is invalid."""

    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Scheduler initialed with invalid seed URL: {url}")