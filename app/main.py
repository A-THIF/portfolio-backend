from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
import logging
import os

from app.routes import admin, auth
from app import admin_dashboard
from app.databases.database import engine, Base
from app.utils.limiter import limiter


class SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # If it's a string message, we can safely redact
        if isinstance(record.msg, str):
            admin_secret = os.getenv("ADMIN_SECRET_KEY")
            if admin_secret and admin_secret in record.msg:
                record.msg = record.msg.replace(admin_secret, "[REDACTED_SENSITIVE_KEY]")
            
            # If Uvicorn access logs are present, the secret might be in the args, not the msg
            if record.args and isinstance(record.args, tuple):
                new_args = list(record.args)
                for i, arg in enumerate(new_args):
                    if isinstance(arg, str) and admin_secret and admin_secret in arg:
                        new_args[i] = arg.replace(admin_secret, "[REDACTED_SENSITIVE_KEY]")
                record.args = tuple(new_args)
        return True

def configure_logging() -> None:
    body_filter = SensitiveDataFilter()
    # Apply to all relevant loggers
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        logger = logging.getLogger(logger_name)
        logger.addFilter(body_filter)
        # Also apply to handlers to be thorough
        for handler in logger.handlers:
            handler.addFilter(body_filter)

# 2. APP INITIALIZATION
app = FastAPI(
    docs_url=None if os.getenv("ENV") == "production" else "/docs",
    redoc_url=None if os.getenv("ENV") == "production" else "/redoc"
)

configure_logging()

# 3. DATABASE SETUP
Base.metadata.create_all(bind=engine)

# 4. MIDDLEWARE & RATE LIMITING
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# 5. CORS
origins = [
    "https://a-thif.netlify.app",
    "https://a-thif-portfolio.netlify.app",
    "https://athif-os.vercel.app"
]

if os.getenv("ENV") != "production":
    origins.append("http://localhost:3000") # Useful for local testing

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. ROUTES
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(admin_dashboard.router)

# 7. GLOBAL EXCEPTION CATCH (Final Safety Net)
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # Prevents raw exception strings (which might contain data) 
        # from leaking to the client in production
        logging.error(f"Unhandled error: {str(e)}")
        return Response("Internal Server Error", status_code=500)
