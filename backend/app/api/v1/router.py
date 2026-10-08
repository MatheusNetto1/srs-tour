from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.indicators.router import admin_router as indicators_admin_router
from app.indicators.router import router as indicators_router
from app.tourism.router import router as tourism_router
from app.users.router import router as users_router

"""

from app.reports.router import router as reports_router

"""

api_router = APIRouter()

# Namespace administrativo (/api/v1/admin/<recurso>): todo domínio registra aqui
# o seu router administrativo, que concentra qualquer leitura de rascunhos ou
# alteração de dados. As rotas públicas ficam fora deste grupo.
admin_router = APIRouter(prefix="/admin")

admin_router.include_router(
    indicators_admin_router,
    prefix="/indicators",
)

api_router.include_router(admin_router)

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"],
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["Users"],
)

api_router.include_router(
    indicators_router,
    prefix="/indicators",
)

"""

api_router.include_router(
    reports_router,
    prefix="/reports",
    tags=["Reports"],
)

"""

api_router.include_router(
    tourism_router,
    prefix="/tourism",
    tags=["Tourism"],
)
