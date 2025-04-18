import secrets
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.repositories.address import address_repository
from app.repositories.user import user_repository
from app.schemas.address import AddressCreate, AddressUpdate
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """
    User service for business logic.
    """

    def authenticate(self, db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.
        """
        user = user_repository.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def get_by_id(self, db: Session, user_id: uuid.UUID) -> Optional[User]:
        """
        Get a user by ID.
        """
        return user_repository.get(db, id=user_id)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get a user by email.
        """
        return user_repository.get_by_email(db, email=email)

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users with pagination.
        """
        return user_repository.get_multi(db, skip=skip, limit=limit)

    def create(self, db: Session, user_in: UserCreate) -> User:
        """
        Create a new user.
        """
        # Check if user with this email already exists
        user = user_repository.get_by_email(db, email=user_in.email)
        if user:
            raise BadRequestException(detail="Email already registered")

        # Create user
        password_hash = get_password_hash(user_in.password)
        user = user_repository.create_with_password(db, obj_in=user_in, password_hash=password_hash)

        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        user.verification_token = verification_token
        db.add(user)
        db.commit()
        db.refresh(user)

        # TODO: Send verification email

        return user

    def update(self, db: Session, user_id: uuid.UUID, user_in: UserUpdate) -> User:
        """
        Update a user.
        """
        user = user_repository.get(db, id=user_id)
        if not user:
            raise NotFoundException(detail="User not found")

        # Handle password update
        update_data = user_in.dict(exclude_unset=True)
        if "password" in update_data and "current_password" in update_data:
            if not verify_password(update_data["current_password"], user.password_hash):
                raise BadRequestException(detail="Incorrect password")

            # Set password hash
            password_hash = get_password_hash(update_data["password"])
            update_data["password_hash"] = password_hash

            # Remove password fields from update data
            del update_data["password"]
            del update_data["current_password"]

            # Update user
            user = user_repository.update(db, db_obj=user, obj_in=update_data)
        elif "password" in update_data:
            # For admin updates where current password is not required
            password_hash = get_password_hash(update_data["password"])
            update_data["password_hash"] = password_hash
            del update_data["password"]
            user = user_repository.update(db, db_obj=user, obj_in=update_data)
        else:
            # Regular update without password change
            user = user_repository.update(db, db_obj=user, obj_in=update_data)

        return user

    def delete(self, db: Session, user_id: uuid.UUID) -> None:
        """
        Delete a user.
        """
        user = user_repository.get(db, id=user_id)
        if not user:
            raise NotFoundException(detail="User not found")

        user_repository.remove(db, id=user_id)

    def request_password_reset(self, db: Session, email: str) -> None:
        """
        Request a password reset for a user.
        """
        user = user_repository.get_by_email(db, email=email)
        if user:
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            user.reset_password_token = reset_token
            db.add(user)
            db.commit()

            # TODO: Send password reset email

    def reset_password(self, db: Session, token: str, new_password: str) -> User:
        """
        Reset a user's password using a reset token.
        """
        user = db.query(User).filter(User.reset_password_token == token).first()
        if not user:
            raise BadRequestException(detail="Invalid reset token")

        # Update password
        password_hash = get_password_hash(new_password)
        user.password_hash = password_hash
        user.reset_password_token = None
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    def verify_email(self, db: Session, token: str) -> User:
        """
        Verify a user's email using a verification token.
        """
        user = db.query(User).filter(User.verification_token == token).first()
        if not user:
            raise BadRequestException(detail="Invalid verification token")

        # Mark email as verified
        user.is_verified = True
        user.verification_token = None
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    # Address methods
    def get_user_addresses(self, db: Session, user_id: uuid.UUID) -> List:
        """
        Get all addresses for a user.
        """
        return address_repository.get_user_addresses(db, user_id=user_id)

    def get_user_address(self, db: Session, user_id: uuid.UUID, address_id: uuid.UUID):
        """
        Get a specific address for a user.
        """
        address = address_repository.get_user_address_by_id(db, user_id=user_id, address_id=address_id)
        if not address:
            raise NotFoundException(detail="Address not found")
        return address

    def create_user_address(self, db: Session, user_id: uuid.UUID, address_in: AddressCreate):
        """
        Create a new address for a user.
        """
        return address_repository.create_address(db, obj_in=address_in, user_id=user_id)

    def update_user_address(
            self, db: Session, user_id: uuid.UUID, address_id: uuid.UUID, address_in: AddressUpdate
    ):
        """
        Update a specific address for a user.
        """
        address = address_repository.get_user_address_by_id(db, user_id=user_id, address_id=address_id)
        if not address:
            raise NotFoundException(detail="Address not found")

        return address_repository.update_address(db, db_obj=address, obj_in=address_in, user_id=user_id)

    def delete_user_address(self, db: Session, user_id: uuid.UUID, address_id: uuid.UUID) -> None:
        """
        Delete a specific address for a user.
        """
        address = address_repository.get_user_address_by_id(db, user_id=user_id, address_id=address_id)
        if not address:
            raise NotFoundException(detail="Address not found")

        # Store address type for potential default reassignment
        address_type = address.address_type
        is_default = address.is_default

        # Delete address
        address_repository.remove(db, id=address_id)

        # If this was a default address, set another one as default
        if is_default:
            address_repository.set_default_after_deletion(db, user_id=user_id, address_type=address_type)


user_service = UserService()
