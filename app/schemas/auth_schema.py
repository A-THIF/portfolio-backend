from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    name: str
    profile_link: str
    email: Optional[str] = None  # This tells FastAPI: "It's okay if this is missing"
    class Config:
        extra = "ignore" # This prevents 422 if the frontend sends extra "junk" data