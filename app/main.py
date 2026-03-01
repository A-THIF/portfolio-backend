from fastapi import FastAPI
from app.routes.contact import router as contact_router

app = FastAPI()

app.include_router(contact_router)