# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GMAIL_CLIENT_ID: str
    GMAIL_CLIENT_SECRET: str
    GMAIL_REFRESH_TOKEN: str
    GMAIL_SENDER: str

    model_config = {
        "env_file": ".env"
    }

settings = Settings()