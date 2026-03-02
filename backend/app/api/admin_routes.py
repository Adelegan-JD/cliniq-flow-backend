from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends

from app.services.sync.supabase_sync import SupabaseSyncService
from app.utils.auth import require_role
from app.utils.storage import get_metrics
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from app.dependency.dependencies import verify_admin
import os
from dotenv import load_dotenv

load_dotenv()


router = APIRouter()

class AdminCreateUserRequest(BaseModel):
    email: EmailStr
    # Optional: If you want to set a temporary password
    password: str | None = None
    role: str | None = None

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

@router.post("/invite-user")
async def invite_user(
    request: AdminCreateUserRequest, admin_user=Depends(verify_admin)
):
    try:
        # 1. Using inviteUserByEmail triggers the Supabase 'Invite' email template automatically
        response = supabase_admin.auth.admin.create_user(
            {
                "email": request.email,
                "password": request.password,
                "email_confirm": True,
                "user_metadata": {
                    "role": request.role,
                    "created_by_admin": True,
                    "needs_password_update": True,
                    "created_by": admin_user.email
                },
            }
        )
        return {"message": f"User created by admin: {admin_user.email}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/metrics")
def admin_metrics(_role: str = Depends(require_role("admin"))):
    return get_metrics()


@router.get("/sync/status")
def sync_status(_role: str = Depends(require_role("admin"))):
    return SupabaseSyncService().status()


@router.post("/sync/run")
def run_sync(_role: str = Depends(require_role("admin"))):
    return SupabaseSyncService().sync_once()


@router.get("/users")
async def list_users(admin_user=Depends(verify_admin)):
    """Admin-only: list users exposing only `display_name` and `role` from metadata."""
    try:
        result = supabase_admin.auth.admin.list_users()

        # Normalize the returned users list from different SDK response shapes
        if isinstance(result, dict):
            raw_users = result.get("users") or result.get("data") or []
        elif hasattr(result, "data"):
            raw_users = result.data or []
        else:
            raw_users = result or []

        def to_dict(obj):
            if obj is None:
                return {}
            if isinstance(obj, dict):
                return obj
            # pydantic/BaseModel style
            if hasattr(obj, "dict") and callable(getattr(obj, "dict")):
                try:
                    return obj.dict()
                except Exception:
                    pass
            # fallback to __dict__
            if hasattr(obj, "__dict__"):
                try:
                    return obj.__dict__
                except Exception:
                    pass
            return {}

        users = []
        for u in raw_users:
            u_dict = to_dict(u)
            metadata = to_dict(u_dict.get("user_metadata") or u_dict.get("raw_user_meta_data") or u_dict.get("raw_user_metadata"))
            display_name = u_dict.get("display_name") or metadata.get("display_name")
            users.append({
                "display_name": display_name,
                "role": metadata.get("role"),
            })
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
