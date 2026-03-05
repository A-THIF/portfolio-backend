from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.routes import auth
from app.databases.database import engine, Base
from app.utils.limiter import limiter
from app import admin_dashboard


app = FastAPI()

# Create DB tables
Base.metadata.create_all(bind=engine)

# Attach limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
origins = [
    "https://a-thif.netlify.app",
    "https://a-thif-portfolio.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router( admin_dashboard.router)

import os
print("DATABASE_URL:", os.getenv("DATABASE_URL"))