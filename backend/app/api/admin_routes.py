from __future__ import annotations

from fastapi import APIRouter, Depends

from app.utils.auth import require_role
from app.utils.storage import get_metrics

router = APIRouter()


@router.get("/metrics")
def admin_metrics(_role: str = Depends(require_role("admin"))):
    return get_metrics()
