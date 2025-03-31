from fastapi import HTTPException, status


class URLShortenerException(HTTPException):
    """Base exception for URL shortener application"""

    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)


class LinkNotFoundException(URLShortenerException):
    """Exception raised when a link is not found"""

    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class DuplicateAliasException(URLShortenerException):
    """Exception raised when a custom alias already exists"""

    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)
