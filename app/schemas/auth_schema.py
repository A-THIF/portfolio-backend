from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    name: str
    # Adding Optional and allowing None/null inputs
    profile_link: Optional[str] = None 
    email: Optional[str] = None

    class Config:
        from_attributes = True
        extra = "ignore"