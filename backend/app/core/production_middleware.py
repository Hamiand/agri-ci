import uuid
from starlette.middleware.base import BaseHTTPMiddleware
class ProductionHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self,request,call_next):
        request_id=request.headers.get("X-Request-ID") or str(uuid.uuid4())
        response=await call_next(request)
        response.headers["X-Request-ID"]=request_id
        response.headers["X-Content-Type-Options"]="nosniff"
        response.headers["X-Frame-Options"]="DENY"
        response.headers["Referrer-Policy"]="no-referrer"
        response.headers["Cache-Control"]="no-store" if request.url.path.startswith(("/auth","/payments")) else response.headers.get("Cache-Control","")
        return response
