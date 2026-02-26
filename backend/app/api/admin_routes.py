from __future__ import annotations

from fastapi import APIRouter, Depends

from app.services.sync.supabase_sync import SupabaseSyncService
from app.utils.auth import require_role
from app.utils.storage import get_metrics

router = APIRouter()


@router.get("/metrics")
def admin_metrics(_role: str = Depends(require_role("admin"))):
    return get_metrics()


@router.get("/sync/status")
def sync_status(_role: str = Depends(require_role("admin"))):
    return SupabaseSyncService().status()


@router.post("/sync/run")
def run_sync(_role: str = Depends(require_role("admin"))):
    return SupabaseSyncService().sync_once()
