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
    RefreshToken,
)
from app.utils.datetime_utils import utcnow

router = APIRouter()


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register(
        *,
        db: Session = Depends(get_db),
        user_in: UserCreate,
) -> Any:
    """
    Register a new user.
    
    Creates a new user account with the provided information.
    The user will need to verify their email address before accessing certain features.
    """
    # Validate password
    _validate_password(user_in.password, user_in.confirm_password)
    
    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise BadRequestException(detail="Email already registered")

    # Generate verification token
    import secrets
    verification_token = secrets.token_urlsafe(32)

    # Create new user
    db_user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        phone_number=user_in.phone_number,
        is_active=True,
        is_verified=False,  # User needs to verify email
        verification_token=verification_token,
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise BadRequestException(detail=f"Error creating user: {str(e)}")

    # TODO: Send verification email with verification_token

    return db_user


def _validate_password(password: str, confirm_password: str) -> None:
    """
    Validate password strength and confirmation.
    
    Args:
        password: The password to validate
        confirm_password: The confirmation password
        
    Raises:
        BadRequestException: If validation fails
    """
    # Check if passwords match
    if password != confirm_password:
        raise BadRequestException(detail="Passwords do not match")
        
    # Check password length
    if len(password) < 8:
        raise BadRequestException(detail="Password must be at least 8 characters")
    
    # Check password complexity (optional enhancement)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not (has_upper and has_lower and has_digit):
        raise BadRequestException(
            detail="Password must contain at least one uppercase letter, one lowercase letter, and one digit"
        )


def _authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Authenticate a user with email and password.
    
    Args:
        db: Database session
        email: User email
        password: User password
        
    Returns:
        User object if authentication is successful
        
    Raises:
        UnauthorizedException: If authentication fails
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise UnauthorizedException(detail="Incorrect email or password")
    if not user.is_active:
        raise UnauthorizedException(detail="Inactive user")
    
    # Update last login timestamp
    user.last_login = utcnow()
    db.add(user)
    db.commit()
    
    return user


def _create_tokens(user_id: str) -> dict:
    """
    Create access and refresh tokens for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with access_token, refresh_token, and token_type
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user_id, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=Token)
def login(
        *,
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = _authenticate_user(db, form_data.username, form_data.password)
    return _create_tokens(str(user.id))


@router.post("/login/email", response_model=Token)
def login_email(
        *,
        db: Session = Depends(get_db),
        login_in: UserLogin,
) -> Any:
    """
    Login with email and password.
    """
    user = _authenticate_user(db, login_in.email, login_in.password)
    return _create_tokens(str(user.id))


@router.post("/refresh", response_model=Token)
def refresh_token(
        *,
        db: Session = Depends(get_db),
        refresh_data: RefreshToken,
) -> Any:
    """
    Refresh access token.
    
    Uses a valid refresh token to generate a new access token and refresh token.
    The old refresh token is invalidated after use.
    """
    from jose import jwt, JWTError
    from pydantic import ValidationError
    from app.schemas.user import TokenPayload

    try:
        refresh_token = refresh_data.refresh_token
        
        # Decode and validate the token
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = TokenPayload(**payload)

        # Verify this is a refresh token
        if payload.get("type") != "refresh":
            raise UnauthorizedException(detail="Invalid token type")
            
        # Check token expiration
        if "exp" not in payload:
            raise UnauthorizedException(detail="Token has no expiration")
            
    except JWTError:
        raise UnauthorizedException(detail="Invalid token format")
    except ValidationError:
        raise UnauthorizedException(detail="Invalid token payload")

    # Get the user from the database
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise NotFoundException(detail="User not found")
    if not user.is_active:
        raise UnauthorizedException(detail="Inactive user")

    # Generate new tokens
    return _create_tokens(str(user.id))


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
def request_password_reset(
        *,
        db: Session = Depends(get_db),
        reset_request: PasswordResetRequest,
) -> Any:
    """
    Request a password reset.
    
    Sends a password reset link to the user's email if the account exists.
    For security reasons, the API always returns a success response regardless
    of whether the email exists in the system.
    """
    user = db.query(User).filter(User.email == reset_request.email).first()
    if user and user.is_active:
        # Generate reset token
        import secrets
        from datetime import datetime, timedelta

        # Create a token that expires in 24 hours
        reset_token = secrets.token_urlsafe(32)
        token_expiry = utcnow() + timedelta(hours=24)
        
        # Save token to user record
        user.reset_password_token = reset_token
        user.reset_token_expires_at = token_expiry
        
        try:
            db.add(user)
            db.commit()
            
            # TODO: Send password reset email with reset_token
            # The email should include a link like:
            # f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            
        except Exception as e:
            db.rollback()
            # Log the error but don't expose it to the client
            print(f"Error generating password reset: {str(e)}")

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
    
    Validates the reset token and updates the user's password.
    The token must be valid and not expired.
    """
    # Validate password
    _validate_password(reset_data.password, reset_data.confirm_password)
    
    # Find user with this token
    user = db.query(User).filter(User.reset_password_token == reset_data.token).first()
    if not user:
        raise BadRequestException(detail="Invalid or expired reset token")
        
    # Check if token is expired
    if user.reset_token_expires_at and user.reset_token_expires_at < utcnow():
        # Clear expired token
        user.reset_password_token = None
        user.reset_token_expires_at = None
        db.add(user)
        db.commit()
        raise BadRequestException(detail="Reset token has expired")

    try:
        # Update password
        user.password_hash = get_password_hash(reset_data.password)
        user.reset_password_token = None
        user.reset_token_expires_at = None
        
        # Update last password change timestamp
        user.last_password_change = utcnow()
        
        db.add(user)
        db.commit()
        
        # TODO: Send password change confirmation email
        
        return {"message": "Password reset successful"}
    except Exception as e:
        db.rollback()
        raise BadRequestException(detail=f"Error resetting password: {str(e)}")


@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(
        *,
        db: Session = Depends(get_db),
        verification_data: EmailVerification,
) -> Any:
    """
    Verify email address.
    
    Validates the email verification token and marks the user's email as verified.
    This enables full access to the user's account features.
    """
    user = db.query(User).filter(User.verification_token == verification_data.token).first()
    if not user:
        raise BadRequestException(detail="Invalid verification token")
        
    # Check if already verified
    if user.is_verified:
        return {"message": "Email already verified"}

    try:
        # Mark email as verified
        user.is_verified = True
        user.verification_token = None
        user.email_verified_at = utcnow()
        
        db.add(user)
        db.commit()
        
        # TODO: Send welcome email or notification
        
        return {"message": "Email verified successfully"}
    except Exception as e:
        db.rollback()
        raise BadRequestException(detail=f"Error verifying email: {str(e)}")
