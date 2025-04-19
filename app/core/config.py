import secrets
from typing import List, Optional, Union

from pydantic import (
    AnyHttpUrl,
    EmailStr,
    field_validator,
    ConfigDict
)
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env"
    )

    API_PREFIX: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 7 days = 7 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    # CORS settings
    CORS_ORIGINS: Union[List[str], List[AnyHttpUrl]] = []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    # Database settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        # Directly access the validation info dictionary
        if isinstance(v, str):
            return v

        # Build the connection string manually
        values = info.data

        user = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        host = values.get("POSTGRES_SERVER")
        db = values.get("POSTGRES_DB", "")

        # Raise an error if critical values are missing
        if not all([user, password, host]):
            raise ValueError("Database connection parameters are missing")

        # Convert the connection string to a proper format that SQLAlchemy can use
        return f"postgresql://{user}:{password}@{host}/{db}"

    # Redis settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0

    # Email settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # Project settings
    PROJECT_NAME: str = "E-commerce API"
    ADMIN_EMAIL: EmailStr

    # External services
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # AWS S3 for file storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_STORAGE_BUCKET_NAME: Optional[str] = None
    AWS_S3_REGION_NAME: Optional[str] = None


# Use function to allow for potential lazy loading or environment-specific configuration
def get_settings():
    return Settings()


# Create settings instance
settings = get_settings()
