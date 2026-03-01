# app/routes/contact.py
from fastapi import APIRouter, HTTPException
from app.schemas.contact_schema import ContactRequest
from app.services.email_service import send_contact_email
from app.utils.validators import is_valid_url, is_non_empty_string

router = APIRouter()

@router.post("/contact")
def submit_contact(data: ContactRequest):
    # ✅ Validate input first
    if not is_non_empty_string(data.name) or not is_valid_url(data.profile_link):
        raise HTTPException(status_code=400, detail="Invalid input")
    
    # ✅ Send email via Resend
    success = send_contact_email(data.name, data.profile_link)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email")
    
    return {"message": "Details submitted successfully"}