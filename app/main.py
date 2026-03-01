# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.contact import router as contact_router

app = FastAPI()

# Allow your test and production frontend URLs
origins = [
    "https://a-thif.netlify.app",       # testing
    "https://a-thif-portfolio.netlify.app",  # production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contact_router)