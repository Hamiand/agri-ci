from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _trace_id(request: Request):
    return getattr(request.state, "request_id", None)


def _message_from_code(code: str) -> str:
    return code.replace("_", " ").title()


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Return one stable AGRI-CI error envelope for HTTP/business failures.

    `detail` is temporarily retained at the top level for pilot-client backward
    compatibility. New clients should consume the canonical `error` object.
    """
    detail = exc.detail if isinstance(exc.detail, str) else "REQUEST_FAILED"
    return JSONResponse(
        status_code=exc.status_code,
        headers=getattr(exc, "headers", None),
        content={
            "detail": detail,
            "error": {
                "code": detail,
                "message": _message_from_code(detail),
                "details": {},
                "trace_id": _trace_id(request),
            },
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Normalize FastAPI/Pydantic 422 responses without leaking input values."""
    fields = []
    for error in exc.errors():
        fields.append(
            {
                "location": [str(part) for part in error.get("loc", ())],
                "message": error.get("msg", "Invalid value"),
                "type": error.get("type", "validation_error"),
            }
        )
    return JSONResponse(
        status_code=422,
        content={
            "detail": "VALIDATION_ERROR",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation Error",
                "details": {"fields": fields},
                "trace_id": _trace_id(request),
            },
        },
    )
