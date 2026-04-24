import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    # Use timezone-aware for the JWT itself (this is standard)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
# C:\Users\parve\Documents\Projects\portfolio-backend\app\utils\security.py

# ... (keep imports and verify_token as is)

# 1. CRITICAL: auto_error=False prevents the 401 crash when the header is missing
security = HTTPBearer(auto_error=False)

async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = None
    
    # Check 1: Authorization Header (used by Flutter API calls)
    if credentials:
        token = credentials.credentials
        
    # Check 2: Cookie (used by the HTML Dashboard after redirect)
    if not token:
        # LOOK HERE: Ensure this name matches what you set in auth.py
        token = request.cookies.get("admin_session")
    
    # If neither exists, THEN we throw the 401
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Session missing. Please login via the frontend."
        )

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Session expired")
        
    return payload