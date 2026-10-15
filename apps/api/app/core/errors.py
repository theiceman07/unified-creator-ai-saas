
from fastapi import HTTPException


class AppError(HTTPException):
    def __init__(self, code: str, message: str, retryable: bool = False, run_id: str | None = None, status_code: int = 400):
        super().__init__(status_code=status_code, detail={
            "error": {
                "code": code,
                "message": message,
                "retryable": retryable,
                "run_id": run_id
            }
        })

class ValidationError(AppError):
    def __init__(self, message: str, run_id: str | None = None):
        super().__init__("VALIDATION_ERROR", message, False, run_id, 400)

class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__("NOT_FOUND", message, False, None, 404)
        
class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__("UNAUTHORIZED", message, False, None, 401)
