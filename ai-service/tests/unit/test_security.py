from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from app.config import Settings
from app.api.dependencies import require_admin
from app.core.security import UserPrincipal, authenticate_request


def make_settings(**updates):
    return Settings(_env_file=None, **updates)


def test_development_mode_accepts_explicit_identity():
    settings = make_settings(AI_AUTH_MODE="development")
    principal = authenticate_request(settings, None, "dev-user", None, None)
    assert principal.user_id == "dev-user"


def test_jwt_mode_rejects_dev_identity():
    settings = make_settings(AI_AUTH_MODE="jwt", JWT_SECRET="secret")
    with pytest.raises(HTTPException) as exc:
        authenticate_request(settings, None, "spoofed", None, None)
    assert exc.value.status_code == 401


def test_gateway_headers_are_disabled_by_default():
    settings = make_settings(AI_AUTH_MODE="gateway", AI_TRUST_GATEWAY_HEADERS=False)
    with pytest.raises(HTTPException):
        authenticate_request(settings, None, None, "user-1", "admin")


def test_valid_jwt_returns_claims():
    settings = make_settings(AI_AUTH_MODE="jwt", JWT_SECRET="secret")
    token = jwt.encode(
        {"sub": "user-1", "role": "ROLE_ADMIN", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "secret",
        algorithm="HS256",
    )
    principal = authenticate_request(settings, f"Bearer {token}", None, None, None)
    assert principal.user_id == "user-1"
    assert principal.role == "admin"


def test_expired_jwt_is_rejected():
    settings = make_settings(AI_AUTH_MODE="jwt", JWT_SECRET="secret")
    token = jwt.encode(
        {"sub": "user-1", "exp": datetime.now(timezone.utc) - timedelta(minutes=5)},
        "secret",
        algorithm="HS256",
    )
    with pytest.raises(HTTPException):
        authenticate_request(settings, f"Bearer {token}", None, None, None)


@pytest.mark.asyncio
async def test_non_admin_principal_is_forbidden():
    with pytest.raises(HTTPException) as exc:
        await require_admin(UserPrincipal(user_id="user-1", role="user"))
    assert exc.value.status_code == 403
