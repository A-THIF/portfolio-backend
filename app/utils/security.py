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
    
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = None
    
    # 1. Check Header (Flutter)
    if credentials:
        token = credentials.credentials
        
    # 2. Check Cookie (HTML Dashboard)
    if not token:
        token = request.cookies.get("admin_session")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Unauthorized: No token or session found"
        )

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Session expired or invalid"
        )
    return payload

def get_current_admin(payload: dict = Depends(get_current_user)):
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin access required"
        )
    return payload