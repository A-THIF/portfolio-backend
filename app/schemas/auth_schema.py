from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    name: str
    profile_link: str
    email: str = None # Add this if it's missing!