from fastapi import Depends, Header, HTTPException, status

from app.config import settings
from app.core.security import UserPrincipal, authenticate_request


async def get_current_principal(
    authorization: str | None = Header(None, alias="Authorization"),
    x_dev_user_id: str | None = Header(None, alias="X-Dev-User-Id"),
    x_user_id: str | None = Header(None, alias="X-User-Id"),
    x_role: str | None = Header(None, alias="X-Role"),
) -> UserPrincipal:
    return authenticate_request(settings, authorization, x_dev_user_id, x_user_id, x_role)


async def get_current_user(principal: UserPrincipal = Depends(get_current_principal)) -> str:
    """Compatibility helper for dependencies that only need the user id."""
    if isinstance(principal, UserPrincipal):
        return principal.user_id
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")


async def require_admin(
    principal: UserPrincipal = Depends(get_current_principal),
) -> UserPrincipal:
    if not isinstance(principal, UserPrincipal) or principal.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Admin role required."},
        )
    return principal
