from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.router import router as auth_router
from app.farmers.router import router as farmers_router
from app.farms.router import router as farms_router
from app.plots.router import router as plots_router
from app.harvests.router import router as harvests_router
from app.products.router import router as products_router
from app.offers.router import router as offers_router
from app.buyers.router import router as buyers_router
from app.demands.router import router as demands_router
from app.matching.router import router as matching_router
from app.aggregation.router import router as aggregation_router
from app.commitments.router import router as commitments_router
from app.orders.router import router as orders_router
from app.collection.router import router as collection_router
from app.logistics.router import router as logistics_router
from app.deliveries.router import router as deliveries_router
from app.payments.router import router as payments_router
from app.payments.webhook import router as payment_webhook_router
from app.core.config import get_settings
from app.core.exceptions import http_exception_handler
from app.core.middleware import RequestIdMiddleware
from app.core.production import production_checks
from app.database.session import get_db

settings = get_settings()
app = FastAPI(
    title="AGRI-CI Core API",
    version="0.9.1",
    description="AGRI-CI: future harvest and agricultural market orchestration foundation.",
)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_middleware(RequestIdMiddleware)

# CORS_ORIGINS is supplied by the deployment environment as a comma-separated value.
CORS_ORIGINS = settings.cors_origin_list
if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# The canonical AGRI-CI contract currently exposes these routes at the public root.
# API versioning can be introduced behind a gateway without changing domain services.
for router in [
    auth_router,
    farmers_router,
    farms_router,
    plots_router,
    harvests_router,
    products_router,
    offers_router,
    buyers_router,
    demands_router,
    matching_router,
    aggregation_router,
    commitments_router,
    orders_router,
    collection_router,
    logistics_router,
    deliveries_router,
    payments_router,
    payment_webhook_router,
]:
    app.include_router(router)


@app.exception_handler(Exception)
async def unhandled_exception(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Une erreur interne est survenue.",
                "details": {},
                "trace_id": getattr(request.state, "request_id", None),
            }
        },
    )


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "application": settings.app_name,
        "environment": settings.app_env,
        "version": "0.9.1",
    }


@app.get("/ready", tags=["System"])
def ready(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "available"}


@app.get("/production-readiness")
def production_readiness():
    checks, ready = production_checks()
    return {"ready": ready, "checks": checks}


@app.get("/commercial-readiness")
def commercial_readiness():
    checks, ready = production_checks()
    return JSONResponse(
        status_code=200 if ready else 503,
        content={"ready": ready, "checks": checks},
    )
