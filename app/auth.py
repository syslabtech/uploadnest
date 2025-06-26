import os
from pathlib import Path
from dotenv import load_dotenv
import hashlib
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import logging

# Always load .env from backend root
BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_ROOT / '.env')

USERNAME = os.environ.get('BASIC_AUTH_USERNAME', 'admin')
PASSWORD_HASH = os.environ.get('PASSWORD_HASH')

security = HTTPBasic()
logger = logging.getLogger(__name__)

def verify_password(username: str, password: str) -> bool:
    if not PASSWORD_HASH or not username:
        return False
    if username != USERNAME:
        return False
    return hashlib.md5(password.encode()).hexdigest() == PASSWORD_HASH

def basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    logger.info(f"Auth attempt: username='{credentials.username}', password='{credentials.password}', hash='{hashlib.md5(credentials.password.encode()).hexdigest()}'")
    if not verify_password(credentials.username, credentials.password):
        logger.warning(f"Auth failed for username='{credentials.username}'")
        raise HTTPException(status_code=401, detail="Invalid username or password")
    logger.info(f"Auth success for username='{credentials.username}'")
    return True
