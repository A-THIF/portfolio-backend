from app.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_contact_email(name: str, profile_link: str):
    try:
        message = MIMEMultipart()
        message["From"] = settings.EMAIL_USER
        message["To"] = settings.ADMIN_EMAIL
        message["Subject"] = "🚀 New Portfolio Visitor"

        body = f"""
        New visitor submitted details:

        Name: {name}
        Profile: {profile_link}
        """
        message.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        server.sendmail(settings.EMAIL_USER, settings.ADMIN_EMAIL, message.as_string())
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print("Email error:", e)
        return False