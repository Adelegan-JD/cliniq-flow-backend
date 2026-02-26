from __future__ import annotations

from typing import Callable

from fastapi import Header, HTTPException

from app.utils.errors import error_payload


def require_role(*allowed_roles: str) -> Callable[[str | None], str]:
    allowed = {r.lower() for r in allowed_roles}

    def dependency(x_role: str | None = Header(default=None, alias="X-Role")) -> str:
        role = (x_role or "").strip().lower()
        if role not in allowed:
            raise HTTPException(
                status_code=403,
                detail=error_payload(
                    "FORBIDDEN",
                    "Insufficient role for this endpoint",
                    {"required_any_of": sorted(allowed), "received": role or None},
                ),
            )
        return role

    return dependency
