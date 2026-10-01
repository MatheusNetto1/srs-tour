from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.indicators.router import router as indicators_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

register_exception_handlers(app)

app.include_router(
    api_router,
    prefix="/api/v1",
)

app.include_router(
    indicators_router,
    prefix="/api/v1/indicators",
)

@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
    }
