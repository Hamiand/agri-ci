from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

async def http_exception_handler(request: Request, exc: HTTPException):
    trace_id = getattr(request.state, "request_id", None)
    detail = exc.detail if isinstance(exc.detail, str) else "REQUEST_FAILED"
    return JSONResponse(status_code=exc.status_code, content={
        "error": {"code": detail, "message": detail.replace("_", " ").title(),
                  "details": {}, "trace_id": trace_id}
    })
