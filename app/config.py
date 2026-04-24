# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    TELEGRAM_CHAT_ID: str
    DATABASE_URL: str
    SECRET_KEY: str 

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()