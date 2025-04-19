import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User

logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """
    Initialize the database with required initial data.
    """
    try:
        # Create a superuser if it doesn't exist
        create_superuser(db)
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def create_superuser(db: Session) -> None:
    """
    Create a superuser if it doesn't exist.
    """
    admin_email = settings.ADMIN_EMAIL

    try:
        # Check if superuser already exists
        user = db.query(User).filter(User.email == admin_email).first()

        if not user:
            logger.info(f"Creating superuser with email: {admin_email}")
            user = User(
                email=admin_email,
                password_hash=get_password_hash("admin"),  # Default password - change immediately
                first_name="Admin",
                last_name="User",
                is_active=True,
                is_superuser=True,
                is_verified=True,
            )
            db.add(user)
            db.commit()
            logger.info(f"Superuser created with email: {admin_email}")
        else:
            logger.info(f"Superuser already exists with email: {admin_email}")

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating superuser: {e}")
        raise
