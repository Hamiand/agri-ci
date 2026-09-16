import os
from fastapi import HTTPException
def require_commercial_runtime():
    """Fail closed when a production instance is missing launch-critical configuration."""
    if os.getenv("APP_ENV","development")!="production":
        return
    required=("DATABASE_URL","JWT_SECRET","PAYMENT_WEBHOOK_SECRET","CORS_ORIGINS")
    missing=[k for k in required if not os.getenv(k,"").strip()]
    if missing:
        raise HTTPException(status_code=503,detail="COMMERCIAL_RUNTIME_NOT_READY")
