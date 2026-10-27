import re

from fastapi import status
from fastapi.testclient import TestClient

from app.core.messages import get_message
from app.main import app

ADMIN_PREFIX = "/api/v1/admin"


def test_all_admin_routes_require_authentication(
    anonymous_client: TestClient,
) -> None:
    admin_routes = {
        path: operations
        for path, operations in app.openapi()["paths"].items()
        if path.startswith(ADMIN_PREFIX)
    }

    assert admin_routes

    for route_path, operations in admin_routes.items():
        path = re.sub(r"\{[^}]+\}", "1", route_path)

        for method in operations:
            response = anonymous_client.request(method, path)

            assert response.status_code == status.HTTP_401_UNAUTHORIZED, (
                f"{method.upper()} {route_path} não está protegido"
            )
            assert response.json()["detail"] == get_message("auth.invalid_token")
