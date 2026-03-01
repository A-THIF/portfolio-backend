# app/services/email_service.py
from resend import Resend
import os
from app.config import settings

# Initialize Resend with API key
resend = Resend(api_key=os.getenv("RESEND_API_KEY"))

def send_contact_email(name: str, profile_link: str):
    try:
        resend.emails.send(
            from_email=os.getenv("FROM_EMAIL", "athifbka@gmail.com"),
            to=[settings.ADMIN_EMAIL],
            subject="🚀 New Portfolio Visitor",
            html=f"""
            <p>New visitor submitted details:</p>
            <p><b>Name:</b> {name}</p>
            <p><b>Profile:</b> <a href="{profile_link}">{profile_link}</a></p>
            """
        )
        return True
    except Exception as e:
        print("Email error:", e)
        return False