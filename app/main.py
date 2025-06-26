from fastapi import FastAPI, Response, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import init_database
from app.routes import router
import logging
from contextlib import asynccontextmanager
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self';"
        response.headers['X-Robots-Tag'] = 'noindex, nofollow, nosnippet, noarchive, notranslate, noimageindex'
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    yield

# Fetch allowed origins from environment variable (comma-separated list)
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app = FastAPI(title="File Upload System", version="1.0.0", lifespan=lifespan)
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=[
        "Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"
    ],
)
app.add_middleware(SecureHeadersMiddleware)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
