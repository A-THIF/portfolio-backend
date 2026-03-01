# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    EMAIL_USER: str
    EMAIL_PASSWORD: str
    ADMIN_EMAIL: str

    model_config = {
        "env_file": ".env"
    }

settings = Settings()