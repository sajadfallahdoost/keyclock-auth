from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, EmailStr, Field

from app.core.security import require_role
from app.services.keycloak_admin import KeycloakAdminClient

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    dependencies=[Depends(require_role("admin"))],
)


class UserCreateBody(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    password: str = Field(..., min_length=8)
    role: str = Field(default="client", pattern="^(admin|client)$")


class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[EmailStr] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    enabled: bool


def get_admin_client() -> KeycloakAdminClient:
    return KeycloakAdminClient()


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a Keycloak user",
)
async def create_user(
    payload: UserCreateBody, kc: KeycloakAdminClient = Depends(get_admin_client)
) -> Dict[str, Any]:
    kc_payload: Dict[str, Any] = {
        "username": payload.username,
        "email": payload.email,
        "firstName": payload.first_name,
        "lastName": payload.last_name,
        "enabled": True,
        "emailVerified": bool(payload.email),
        "credentials": [
            {
                "type": "password",
                "value": payload.password,
                "temporary": False,
            }
        ],
    }
    user = await kc.create_user(kc_payload)
    await kc.assign_realm_role(user["id"], payload.role)
    return user


@router.get(
    "",
    response_model=List[UserResponse],
    summary="List Keycloak users (search by username)",
)
async def list_users(
    search: Optional[str] = Query(default=None, description="Search by username"),
    kc: KeycloakAdminClient = Depends(get_admin_client),
) -> List[Dict[str, Any]]:
    return await kc.list_users(search=search)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Retrieve a Keycloak user by ID",
)
async def get_user(user_id: str, kc: KeycloakAdminClient = Depends(get_admin_client)) -> Dict[str, Any]:
    return await kc.get_user(user_id)

