from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

# Legacy import kept for review:
# from supabase import create_client, Client
# Commented out because eager Supabase imports made auth wiring fail in
# environments where Supabase is intentionally optional.

load_dotenv()

reusable_oauth2 = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Legacy eager client kept for review:
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
# Commented out because it crashed import-time startup when env vars or the
# Supabase package were missing.


def _get_supabase_client():
    try:
        from supabase import create_client
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Supabase auth is not available") from exc

    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=503, detail="Supabase auth is not configured")

    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


async def verify_admin(authorization: HTTPAuthorizationCredentials = Depends(reusable_oauth2)):
    # Extract "Bearer <token>"
    token = authorization.credentials

    try:
        supabase = _get_supabase_client()
        # Ask Supabase to verify this specific user's token
        user_resp = supabase.auth.get_user(token)
        user = user_resp.user

        # Check the metadata we set earlier
        role = user.user_metadata.get("role")
        
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin privileges required")
            
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session or token")
