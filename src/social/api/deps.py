from dataclasses import dataclass, field

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from social.config import get_settings
from social.core.security import decode_jwt

bearer_scheme = HTTPBearer()


@dataclass
class Principal:
    sub: str
    is_admin: bool = False
    scopes: list[str] = field(default_factory=list)
    claims: dict = field(default_factory=dict)


async def get_principal(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Principal:
    token = credentials.credentials
    settings = get_settings()

    if token == settings.admin_token:
        return Principal(sub="admin", is_admin=True, scopes=["*"])

    claims = decode_jwt(token)
    if claims is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return Principal(
        sub=claims.get("sub", "unknown"),
        is_admin=claims.get("admin", False),
        scopes=claims.get("scopes", []),
        claims=claims,
    )


def require_permissions(*required_scopes: str):
    async def checker(principal: Principal = Depends(get_principal)) -> Principal:
        if principal.is_admin:
            return principal
        if "*" in principal.scopes:
            return principal
        for scope in required_scopes:
            if scope not in principal.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required scope: {scope}",
                )
        return principal

    return checker
