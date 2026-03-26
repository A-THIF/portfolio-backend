from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.routes import admin
from app.routes import auth
from app import admin_dashboard

from app.databases.database import engine, Base
from app.utils.limiter import limiter

app = FastAPI()

# DB
Base.metadata.create_all(bind=engine)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
origins = [
    "https://a-thif.netlify.app",
    "https://a-thif-portfolio.netlify.app",
    "https://athif-os.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ROUTES (ORDER DOESN’T MATTER MUCH, BUT KEEP CLEAN)
app.include_router(auth.router)
app.include_router(admin.router)            # contains /public/stats
app.include_router(admin_dashboard.router)  # contains /admin-dashboard