from fastapi import Header, HTTPException


async def get_current_user(x_user_id: str | None = Header(None, alias="X-User-Id")) -> str:
    """Extract user_id from X-User-Id header set by API Gateway.

    The API Gateway validates the JWT and forwards the user identity.
    The AI service trusts this header on the internal Docker network.

    Returns:
        user_id: The authenticated user's ID.

    Raises:
        HTTPException: 401 if X-User-Id header is missing.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="Missing X-User-Id header. Authentication required.",
        )
    return x_user_id
