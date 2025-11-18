from functools import lru_cache

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration sourced from environment variables or .env."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    keycloak_server_url: AnyHttpUrl = Field(
        default="http://localhost:8080", validation_alias="KEYCLOAK_SERVER_URL"
    )
    keycloak_realm: str = Field(default="master", validation_alias="KEYCLOAK_REALM")
    keycloak_client_id: str = Field(
        default="backend-service", validation_alias="KEYCLOAK_CLIENT_ID"
    )
    keycloak_audience: str | None = Field(
        default=None, validation_alias="KEYCLOAK_AUDIENCE"
    )  # defaults to client id at runtime
    jwks_cache_ttl: int = Field(default=300, validation_alias="KEYCLOAK_JWKS_CACHE_TTL")
    keycloak_admin_realm: str = Field(
        default="master", validation_alias="KEYCLOAK_ADMIN_REALM"
    )
    keycloak_admin_client_id: str = Field(
        default="admin-cli", validation_alias="KEYCLOAK_ADMIN_CLIENT_ID"
    )
    keycloak_admin_username: str = Field(
        default="admin", validation_alias="KEYCLOAK_ADMIN_USERNAME"
    )
    keycloak_admin_password: SecretStr = Field(
        default="admin", validation_alias="KEYCLOAK_ADMIN_PASSWORD"
    )
    service_username: str = Field(
        default="service-user", validation_alias="SERVICE_USERNAME"
    )
    service_password: SecretStr = Field(
        default="service-pass", validation_alias="SERVICE_PASSWORD"
    )

    @property
    def issuer(self) -> str:
        # مهم 👇 اسلش اضافهٔ آخر URL رو می‌بُره
        base = str(self.keycloak_server_url).rstrip("/")
        return f"{base}/realms/{self.keycloak_realm}"

    @property
    def jwks_url(self) -> str:
        return f"{self.issuer}/protocol/openid-connect/certs"

    @property
    def resolved_audience(self) -> str:
        return self.keycloak_audience or self.keycloak_client_id


@lru_cache
def get_settings() -> Settings:
    return Settings()
