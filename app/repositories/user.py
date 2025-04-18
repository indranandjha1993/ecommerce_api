from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """
    User repository for data access operations.
    """

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get a user by email.
        """
        return db.query(User).filter(User.email == email).first()

    def get_active_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get active users with pagination.
        """
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()

    def create_with_password(self, db: Session, obj_in: UserCreate, password_hash: str) -> User:
        """
        Create a user with a hashed password.
        """
        db_obj = User(
            email=obj_in.email,
            password_hash=password_hash,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            phone_number=obj_in.phone_number,
            is_active=True,
            is_verified=False,  # User needs to verify email
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_password(self, db: Session, db_obj: User, password_hash: str) -> User:
        """
        Update a user's password.
        """
        db_obj.password_hash = password_hash
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_verification_status(self, db: Session, db_obj: User, is_verified: bool) -> User:
        """
        Update a user's verification status.
        """
        db_obj.is_verified = is_verified
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


user_repository = UserRepository(User)
