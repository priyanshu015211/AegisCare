from .error_handler import ErrorHandlerMiddleware, add_exception_handlers
from .request_logger import RequestLoggerMiddleware
from .timing import TimingMiddleware
from .security_headers import SecurityHeadersMiddleware

__all__ = [
    "ErrorHandlerMiddleware",
    "add_exception_handlers",
    "RequestLoggerMiddleware",
    "TimingMiddleware",
    "SecurityHeadersMiddleware",
]
class APIResponse(BaseModel):
    """
    Standardized success response format for all AegisCare APIs.
    All successful responses should follow this structure.
    """
    status: Literal["success"] = "success"
    message: str = "Request completed successfully."
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
