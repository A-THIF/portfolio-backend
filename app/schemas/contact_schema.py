from pydantic import BaseModel

class ContactRequest(BaseModel):
    name: str
    profile_link: str