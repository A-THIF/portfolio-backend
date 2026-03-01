import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")

settings = Settings()