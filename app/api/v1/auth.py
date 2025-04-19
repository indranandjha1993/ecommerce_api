from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    UnauthorizedException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    Token,
    UserCreate,
    UserLogin,
    User as UserSchema,
    PasswordResetRequest,
    PasswordReset,
    EmailVerification,
)

router = APIRouter()


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register(
        *,
        db: Session = Depends(get_db),
        user_in: UserCreate,
) -> Any:
    """
    Register a new user.
    """
    # Check if user with this email already exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise BadRequestException(detail="Email already registered")

    # Create new user
    db_user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        phone_number=user_in.phone_number,
        is_active=True,
        is_verified=False,  # User needs to verify email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # TODO: Send verification email

    return db_user


@router.post("/login", response_model=Token)
def login(
        *,
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise UnauthorizedException(detail="Incorrect email or password")
    if not user.is_active:
        raise UnauthorizedException(detail="Inactive user")

    # Update last login timestamp
    from sqlalchemy import func
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()

    # Generate access and refresh tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.id, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login/email", response_model=Token)
def login_email(
        *,
        db: Session = Depends(get_db),
        login_in: UserLogin,
) -> Any:
    """
    Login with email and password.
    """
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.password_hash):
        raise UnauthorizedException(detail="Incorrect email or password")
    if not user.is_active:
        raise UnauthorizedException(detail="Inactive user")

    # Update last login timestamp
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()

    # Generate access and refresh tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.id, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-token", response_model=Token)
def refresh_token(
        *,
        db: Session = Depends(get_db),
        refresh_token: str = Body(...),
) -> Any:
    """
    Refresh access token.
    """
    from jose import jwt, JWTError
    from pydantic import ValidationError
    from app.schemas.user import TokenPayload

    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = TokenPayload(**payload)

        # Verify this is a refresh token
        if not payload.get("type") == "refresh":
            raise UnauthorizedException(detail="Invalid token type")
    except (JWTError, ValidationError):
        raise UnauthorizedException(detail="Invalid token")

    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise NotFoundException(detail="User not found")
    if not user.is_active:
        raise UnauthorizedException(detail="Inactive user")

    # Generate new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.id, expires_delta=access_token_expires)
    new_refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
def request_password_reset(
        *,
        db: Session = Depends(get_db),
        reset_request: PasswordResetRequest,
) -> Any:
    """
    Request a password reset.
    """
    user = db.query(User).filter(User.email == reset_request.email).first()
    if user:
        # Generate reset token
        import secrets

        reset_token = secrets.token_urlsafe(32)
        user.reset_password_token = reset_token
        db.add(user)
        db.commit()

        # TODO: Send password reset email

    # Always return success to prevent email enumeration
    return {"message": "If your email is registered, you will receive a password reset link"}


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
def confirm_password_reset(
        *,
        db: Session = Depends(get_db),
        reset_data: PasswordReset,
) -> Any:
    """
    Confirm a password reset.
    """
    user = db.query(User).filter(User.reset_password_token == reset_data.token).first()
    if not user:
        raise BadRequestException(detail="Invalid reset token")

    # Update password
    user.password_hash = get_password_hash(reset_data.password)
    user.reset_password_token = None
    db.add(user)
    db.commit()

    return {"message": "Password reset successful"}


@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(
        *,
        db: Session = Depends(get_db),
        verification_data: EmailVerification,
) -> Any:
    """
    Verify email address.
    """
    user = db.query(User).filter(User.verification_token == verification_data.token).first()
    if not user:
        raise BadRequestException(detail="Invalid verification token")

    # Mark email as verified
    user.is_verified = True
    user.verification_token = None
    db.add(user)
    db.commit()

    return {"message": "Email verified successfully"}
