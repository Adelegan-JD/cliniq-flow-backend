from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

reusable_oauth2 = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# We use the ANON client for validation (it respects the user's permissions)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

async def verify_admin(authorization: HTTPAuthorizationCredentials = Depends(reusable_oauth2)):
    # Extract "Bearer <token>"
    token = authorization.credentials
    
    try:
        # Ask Supabase to verify this specific user's token
        user_resp = supabase.auth.get_user(token)
        user = user_resp.user

        # Check the metadata we set earlier
        role = user.user_metadata.get("role")
        
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin privileges required")
            
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session or token")