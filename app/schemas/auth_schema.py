from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    name: str  # Compulsory
    profile_link: Optional[str] = "Not Provided" 
    email: Optional[EmailStr] = None # Optional, validates email format if provided