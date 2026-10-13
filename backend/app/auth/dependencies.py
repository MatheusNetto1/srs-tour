from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.auth import service
from app.core.dependencies import DbSession
from app.users.models import User

# Caminho absoluto: o Swagger resolve um tokenUrl relativo a partir de
# /openapi.json, o que descartaria o prefixo /api/v1.
# auto_error=False para que a ausência do token também passe pelo mecanismo
# central de erros (mesma mensagem e cabeçalho dos demais 401).
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: DbSession,
) -> User:
    return service.get_user_from_token(db, token)


CurrentUser = Annotated[User, Depends(get_current_user)]
