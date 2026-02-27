"""Admin-facing endpoints.

These routes expose system-wide monitoring information such as metrics,
sync status, and audit logs. They are protected with admin role checks.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.services.sync.supabase_sync import SupabaseSyncService
from app.utils.auth import require_role
from app.utils.storage import get_metrics
from app.utils.storage import list_audit_logs

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


@router.get("/logs")
def admin_logs(limit: int = 100, _role: str = Depends(require_role("admin"))):
    return {"items": list_audit_logs(limit=limit)}
