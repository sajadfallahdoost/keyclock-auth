from typing import Any, Dict

from fastapi import Depends, FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse

from api.v1.routers import router as api_router
from app.core.config import get_settings
from app.core.security import get_current_user, get_service_user, require_role

app = FastAPI(
    title="FastAPI + Keycloak",
    description="Sample project demonstrating Keycloak protected routes.",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.include_router(api_router)


@app.get("/")
async def home() -> Dict[str, Any]:
    settings = get_settings()
    return {
        "message": "FastAPI with Keycloak project is running!",
        "realm": settings.keycloak_realm,
        "issuer": settings.issuer,
    }


@app.get("/me")
async def read_profile(claims: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    return {
        "sub": claims.get("sub"),
        "preferred_username": claims.get("preferred_username"),
        "email": claims.get("email"),
        "roles": claims.get("realm_access", {}).get("roles", []),
    }


@app.get("/admin")
async def admin_portal(_: Dict[str, Any] = Depends(require_role("admin"))) -> Dict[str, Any]:
    return {"message": "You have admin access from Keycloak!"}


@app.get("/service-data")
async def service_data(service: Dict[str, Any] = Depends(get_service_user)) -> Dict[str, Any]:
    return {
        "message": "Local service account authenticated via HTTP Basic.",
        "service_user": service["sub"],
    }


@app.get("/openapi.json", include_in_schema=False)
async def openapi_json() -> JSONResponse:
    return JSONResponse(app.openapi())


@app.get("/docs", include_in_schema=False)
async def custom_swagger():
    return get_swagger_ui_html(openapi_url="/openapi.json", title=app.title)
