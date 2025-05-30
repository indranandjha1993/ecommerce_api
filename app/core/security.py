from datetime import datetime, timedelta
from typing import Any, Optional, Union

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.utils.datetime_utils import utcnow

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 with Bearer token
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/auth/login"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    """
    return pwd_context.hash(password)


def create_access_token(
        subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    """
    if expires_delta:
        expire = utcnow() + expires_delta
    else:
        expire = utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(
        subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    """
    if expires_delta:
        expire = utcnow() + expires_delta
    else:
        expire = utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 2
        )
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt
