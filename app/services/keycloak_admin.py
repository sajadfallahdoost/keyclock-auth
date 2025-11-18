from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException, status

from app.core.config import Settings, get_settings


class KeycloakAdminClient:
    """Thin async wrapper around the Keycloak Admin REST API."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()

    @property
    def _token_url(self) -> str:
        return f"{self.settings.keycloak_server_url}/realms/{self.settings.keycloak_admin_realm}/protocol/openid-connect/token"

    @property
    def _users_url(self) -> str:
        return f"{self.settings.keycloak_server_url}/admin/realms/{self.settings.keycloak_realm}/users"

    @property
    def _roles_url(self) -> str:
        return f"{self.settings.keycloak_server_url}/admin/realms/{self.settings.keycloak_realm}/roles"

    async def _admin_token(self) -> str:
        data = {
            "client_id": self.settings.keycloak_admin_client_id,
            "grant_type": "password",
            "username": self.settings.keycloak_admin_username,
            "password": self.settings.keycloak_admin_password.get_secret_value(),
        }
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(self._token_url, data=data)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to obtain Keycloak admin token.",
                )
            return response.json()["access_token"]

    def _auth_header(self, token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    async def create_user(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        token = await self._admin_token()
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                self._users_url, json=payload, headers=self._auth_header(token)
            )
            if response.status_code == status.HTTP_409_CONFLICT:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already exists in Keycloak.",
                )
            if response.status_code != status.HTTP_201_CREATED:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Keycloak failed to create user.",
                )
            location = response.headers.get("Location", "")
            user_id = location.rstrip("/").split("/")[-1]
            return await self.get_user(user_id, token=token)

    async def get_user(self, user_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        token = token or await self._admin_token()
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{self._users_url}/{user_id}", headers=self._auth_header(token)
            )
            if response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=404, detail="Keycloak user not found.")
            if response.status_code != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to fetch user from Keycloak.",
                )
            return response.json()

    async def list_users(
        self, search: Optional[str] = None, token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        token = token or await self._admin_token()
        params = {"search": search, "max": 50} if search else {"max": 50}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                self._users_url, params=params, headers=self._auth_header(token)
            )
            if response.status_code != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to list users from Keycloak.",
                )
            return response.json()

    async def assign_realm_role(
        self, user_id: str, role_name: str, token: Optional[str] = None
    ) -> None:
        token = token or await self._admin_token()
        role = await self._get_realm_role(role_name, token)
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{self._users_url}/{user_id}/role-mappings/realm",
                json=[role],
                headers=self._auth_header(token),
            )
            if response.status_code not in (
                status.HTTP_204_NO_CONTENT,
                status.HTTP_201_CREATED,
            ):
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to assign '{role_name}' role.",
                )

    async def _get_realm_role(self, role_name: str, token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{self._roles_url}/{role_name}", headers=self._auth_header(token)
            )
            if response.status_code != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Role '{role_name}' not found in Keycloak.",
                )
            return response.json()



