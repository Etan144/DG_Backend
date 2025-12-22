from datetime import datetime, timedelta
from typing import Optional 
from app.core.config import settings
from bson import ObjectId
from app.db.database import db
from fastapi import Depends

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

user_collection = db.users


#JWT Config

SECRET_KEY = settings.secret_key
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Token generation
def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {"sub": subject, "exp": expire, "iat": datetime.utcnow()}

    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Token verification
def decode_access_token(token: str) -> str:
    """decode a JWT access token and return the subject."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject: str = payload.get("sub")
        if subject is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return subject
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
# Get current user from token
def get_current_user(token: str = Depends(oauth2_scheme)):
    user_id = decode_access_token(token)

    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user