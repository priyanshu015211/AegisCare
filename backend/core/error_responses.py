from fastapi import HTTPException, status
from typing import Optional, Any
from datetime import datetime

def create_error_response(
    message: str,
    status_code: int = 500,
    detail: Optional[str] = None,
    error_code: Optional[str] = None
):
    return HTTPException(
        status_code=status_code,
        detail={
            "status": "error",
            "message": message,
            "detail": detail,
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
