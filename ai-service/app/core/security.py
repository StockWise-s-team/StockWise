from dataclasses import dataclass
from typing import Any, Protocol

from fastapi import HTTPException, status

from app.config import Settings


@dataclass(frozen=True)
class UserPrincipal:
    user_id: str
    role: str


def _unauthorized(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "UNAUTHORIZED", "message": message},
    )


def _normalize_role(role: Any) -> str:
    return str(role or "user").removeprefix("ROLE_").lower()


class AuthStrategy(Protocol):
    def authenticate(
        self,
        authorization: str | None,
        dev_user_id: str | None,
        gateway_user_id: str | None,
        gateway_role: str | None,
    ) -> UserPrincipal:
        ...


class DevelopmentAuthStrategy:
    def __init__(self, config: Settings):
        self.config = config

    def authenticate(self, authorization: str | None, dev_user_id: str | None, gateway_user_id: str | None, gateway_role: str | None) -> UserPrincipal:
        return UserPrincipal(user_id=dev_user_id or self.config.AI_DEMO_USER_ID, role="admin")


class GatewayAuthStrategy:
    def __init__(self, config: Settings):
        self.config = config

    def authenticate(self, authorization: str | None, dev_user_id: str | None, gateway_user_id: str | None, gateway_role: str | None) -> UserPrincipal:
        if dev_user_id:
            raise _unauthorized("Development identity is disabled.")
        if not self.config.AI_TRUST_GATEWAY_HEADERS:
            raise _unauthorized("Gateway identity headers are disabled.")
        if not gateway_user_id:
            raise _unauthorized("Missing gateway identity.")
        return UserPrincipal(user_id=gateway_user_id, role=_normalize_role(gateway_role))


class JWTAuthStrategy:
    def __init__(self, config: Settings):
        self.config = config

    def authenticate(self, authorization: str | None, dev_user_id: str | None, gateway_user_id: str | None, gateway_role: str | None) -> UserPrincipal:
        if dev_user_id:
            raise _unauthorized("Development identity is disabled.")
        if not authorization or not authorization.startswith("Bearer "):
            raise _unauthorized("Missing bearer token.")
        if not self.config.JWT_SECRET:
            raise _unauthorized("JWT verification is not configured.")

        from jose import JWTError, jwt

        try:
            payload = jwt.decode(
                authorization.removeprefix("Bearer ").strip(),
                self.config.JWT_SECRET,
                algorithms=[self.config.JWT_ALGORITHM],
            )
        except JWTError as exc:
            raise _unauthorized("Invalid or expired bearer token.") from exc
        user_id = payload.get(self.config.AI_JWT_USER_ID_CLAIM)
        if not user_id:
            raise _unauthorized("Bearer token is missing the user identity claim.")
        return UserPrincipal(
            user_id=str(user_id),
            role=_normalize_role(payload.get(self.config.AI_JWT_ROLE_CLAIM)),
        )


def authenticate_request(
    config: Settings,
    authorization: str | None,
    dev_user_id: str | None,
    gateway_user_id: str | None,
    gateway_role: str | None,
) -> UserPrincipal:
    strategies: dict[str, AuthStrategy] = {
        "development": DevelopmentAuthStrategy(config),
        "gateway": GatewayAuthStrategy(config),
        "jwt": JWTAuthStrategy(config),
    }
    strategy = strategies.get(config.AI_AUTH_MODE.lower())
    if not strategy:
        raise _unauthorized("Unsupported authentication mode.")
    return strategy.authenticate(authorization, dev_user_id, gateway_user_id, gateway_role)
