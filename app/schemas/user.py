import datetime
import uuid
from typing import Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    ConfigDict
)


# Shared properties
class UserBase(BaseModel):
    """Base user schema with common properties."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    """Schema for user creation."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    confirm_password: str

    # Validation is now handled in the API endpoint

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123",
                "confirm_password": "strongpassword123",
                "first_name": "John",
                "last_name": "Doe"
            }
        }
    )


# Properties to receive via API on update
class UserUpdate(UserBase):
    """Schema for user update."""
    password: Optional[str] = Field(None, min_length=8)
    current_password: Optional[str] = None

    @field_validator('password')
    @classmethod
    def password_strength(cls, v, info):
        if v is not None and len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "Updated",
                "last_name": "Name",
                "current_password": "oldpassword123",
                "password": "newstrongpassword123"
            }
        }
    )


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    """Base schema for users in DB."""
    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    last_login: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Properties to return to client
class User(UserInDBBase):
    """Schema for user response."""
    pass


# Properties stored in DB
class UserInDB(UserInDBBase):
    """Schema for user stored in DB."""
    password_hash: str


# Token schema
class Token(BaseModel):
    """Schema for auth token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Token payload schema
class TokenPayload(BaseModel):
    """Schema for token payload."""
    sub: str
    exp: int


# Refresh token schema
class RefreshToken(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


# User login schema
class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "yourpassword123"
            }
        }
    )


# Password reset request schema
class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


# Password reset confirmation schema
class PasswordReset(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        values = info.data
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "reset_token_here",
                "password": "newstrongpassword123",
                "confirm_password": "newstrongpassword123"
            }
        }
    )


# Email verification schema
class EmailVerification(BaseModel):
    """Schema for email verification."""
    token: str
