# app/services/email_service.py

import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.config import settings

def send_contact_email(name: str, profile_link: str) -> bool:
    try:
        creds = Credentials(
            None,
            refresh_token=settings.GMAIL_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GMAIL_CLIENT_ID,
            client_secret=settings.GMAIL_CLIENT_SECRET,
            scopes=["https://www.googleapis.com/auth/gmail.send"],
        )

        # Refresh access token automatically
        creds.refresh(Request())

        service = build("gmail", "v1", credentials=creds)

        body = f"""
New Portfolio Submission 🚀

Name: {name}
Profile: {profile_link}
        """

        message = MIMEText(body)
        message["to"] = settings.GMAIL_SENDER
        message["from"] = settings.GMAIL_SENDER
        message["subject"] = "🚀 New Portfolio Visitor"

        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        service.users().messages().send(
            userId="me",
            body={"raw": raw_message}
        ).execute()

        print("Email sent successfully via Gmail API!")
        return True

    except Exception as e:
        print("Gmail API error:", e)
        return False