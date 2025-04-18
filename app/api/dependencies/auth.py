from typing import Optional

from fastapi import Depends
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.core.security import oauth2_scheme
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import TokenPayload


def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
) -> User:
    """
    Validate access token and return current user.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise UnauthorizedException(detail="Could not validate credentials")

    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise UnauthorizedException(detail="User not found")
    if not user.is_active:
        raise UnauthorizedException(detail="Inactive user")

    return user


def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.
    """
    if not current_user.is_active:
        raise ForbiddenException(detail="Inactive user")
    return current_user


def get_current_active_superuser(
        current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active superuser.
    """
    if not current_user.is_superuser:
        raise ForbiddenException(detail="The user doesn't have enough privileges")
    return current_user


def get_optional_current_user(
        db: Session = Depends(get_db),
        token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None.
    """
    if not token:
        return None

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        return None

    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user or not user.is_active:
        return None

    return user
