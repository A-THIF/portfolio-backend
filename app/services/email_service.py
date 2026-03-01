import resend  # Import the module, not a class
import os
from app.config import settings

# Configure the global API key
resend.api_key = os.getenv("RESEND_API_KEY")

def send_contact_email(name: str, profile_link: str):
    try:
        # Use resend.Emails.send() with a dictionary/params
        params = {
            "from": os.getenv("FROM_EMAIL", "onboarding@resend.dev"),
            "to": [settings.ADMIN_EMAIL],
            "subject": "🚀 New Portfolio Visitor",
            "html": f"""
            <p>New visitor submitted details:</p>
            <p><b>Name:</b> {name}</p>
            <p><b>Profile:</b> <a href="{profile_link}">{profile_link}</a></p>
            """,
        }
        
        resend.Emails.send(params)
        return True
    except Exception as e:
        print("Email error:", e)
        return False
