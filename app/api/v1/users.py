from typing import Any, List
from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_active_user,
    get_current_active_superuser,
)
from app.api.dependencies.pagination import PaginationParams, get_pagination
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.core.security import get_password_hash, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.address import (
    Address as AddressSchema,
    AddressCreate,
    AddressUpdate,
)
from app.schemas.user import (
    User as UserSchema,
    UserCreate,
    UserUpdate,
)

router = APIRouter()


@router.get("/me", response_model=UserSchema)
def read_current_user(
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=UserSchema)
def update_current_user(
        *,
        db: Session = Depends(get_db),
        user_in: UserUpdate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update current user.
    
    This endpoint allows users to update their profile information including:
    - Personal details (name, email, phone number)
    - Account settings
    - Password (requires current password verification)
    
    When changing password:
    - The current password must be provided and verified
    - The new password must meet the system's password requirements
    - Password history policies may prevent reuse of recent passwords
    
    Email changes may require verification depending on system settings.
    """
    try:
        # Verify current password if a new password is being set
        if user_in.password and user_in.current_password:
            if not verify_password(user_in.current_password, current_user.password_hash):
                raise BadRequestException(detail="Incorrect password")
        elif user_in.password:
            raise BadRequestException(detail="Current password is required")

        # Check if email is being changed
        if user_in.email and user_in.email != current_user.email:
            # Check if the new email is already in use
            existing_user = db.query(User).filter(User.email == user_in.email).first()
            if existing_user:
                raise BadRequestException(detail="Email already registered")
            
            # TODO: Implement email verification for email changes
            # For now, just update the email directly

        # Update user data
        for key, value in user_in.model_dump(exclude_unset=True).items():
            if key == "password":
                current_user.password_hash = get_password_hash(value)
                # Update last password change timestamp
                current_user.last_password_change = datetime.utcnow()
            elif key == "current_password":
                continue  # Skip this field
            else:
                setattr(current_user, key, value)

        db.add(current_user)
        db.commit()
        db.refresh(current_user)

        return current_user
    except BadRequestException:
        raise
    except Exception as e:
        print(f"Error updating user: {str(e)}")
        raise BadRequestException(detail="Error updating user profile")


@router.get("", response_model=List[UserSchema])
def read_users(
        db: Session = Depends(get_db),
        pagination: PaginationParams = Depends(get_pagination),
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get list of users. Only for superusers.
    """
    users = db.query(User).offset(pagination.skip).limit(pagination.size).all()
    return users


@router.get("/{user_id}", response_model=UserSchema)
def read_user(
        *,
        db: Session = Depends(get_db),
        user_id: str,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get a specific user by ID. Only for superusers.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException(detail="User not found")
    return user


@router.post("", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(
        *,
        db: Session = Depends(get_db),
        user_in: UserCreate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create a new user. Only for superusers.
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
        is_active=user_in.is_active,
        is_verified=True,  # Admin-created users are automatically verified
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
        *,
        db: Session = Depends(get_db),
        user_id: str,
        user_in: UserUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a user. Only for superusers.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException(detail="User not found")

    # Update user data
    for key, value in user_in.model_dump(exclude_unset=True).items():
        if key == "password":
            user.password_hash = get_password_hash(value)
        elif key == "current_password":
            continue  # Skip this field
        else:
            setattr(user, key, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        *,
        db: Session = Depends(get_db),
        user_id: str,
        current_user: User = Depends(get_current_active_superuser),
) -> None:
    """
    Delete a user. Only for superusers.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException(detail="User not found")

    # Prevent deleting self
    if str(user.id) == str(current_user.id):
        raise BadRequestException(detail="Cannot delete yourself")

    db.delete(user)
    db.commit()

    # For status code 204, we should not return anything
    # FastAPI will handle this correctly when the return type is None


# Address endpoints
@router.get("/me/addresses", response_model=List[AddressSchema])
def read_current_user_addresses(
        *,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user's addresses.
    """
    from app.models.address import Address

    addresses = db.query(Address).filter(Address.user_id == current_user.id).all()
    return addresses


@router.post("/me/addresses", response_model=AddressSchema, status_code=status.HTTP_201_CREATED)
def create_current_user_address(
        *,
        db: Session = Depends(get_db),
        address_in: AddressCreate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new address for the current user.
    
    This endpoint allows users to add a new shipping or billing address to their profile.
    
    Features:
    - Users can have multiple addresses
    - Addresses can be designated as shipping or billing type
    - One address of each type can be set as the default
    - If this is the first address of its type, it will automatically be set as default
    - Address validation ensures required fields are provided
    
    The address will be associated with the current authenticated user.
    """
    try:
        from app.models.address import Address

        # Validate address fields
        if not address_in.street_address_1:
            raise BadRequestException(detail="Street address 1 is required")
        
        if not address_in.city:
            raise BadRequestException(detail="City is required")
            
        if not address_in.postal_code:
            raise BadRequestException(detail="Postal code is required")
            
        if not address_in.country:
            raise BadRequestException(detail="Country is required")

        # If this is the first address or marked as default, unset other defaults
        if address_in.is_default or db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.address_type == address_in.address_type
        ).count() == 0:
            db.query(Address).filter(
                Address.user_id == current_user.id,
                Address.address_type == address_in.address_type
            ).update({"is_default": False})
            address_in.is_default = True

        # Create new address
        db_address = Address(
            user_id=current_user.id,
            **address_in.model_dump()
        )
        db.add(db_address)
        db.commit()
        db.refresh(db_address)

        return db_address
    except BadRequestException:
        raise
    except Exception as e:
        print(f"Error creating address: {str(e)}")
        raise BadRequestException(detail="Error creating address")


@router.get("/me/addresses/{address_id}", response_model=AddressSchema)
def read_current_user_address(
        *,
        db: Session = Depends(get_db),
        address_id: str,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific address for the current user.
    """
    from app.models.address import Address

    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()

    if not address:
        raise NotFoundException(detail="Address not found")

    return address


@router.put("/me/addresses/{address_id}", response_model=AddressSchema)
def update_current_user_address(
        *,
        db: Session = Depends(get_db),
        address_id: str,
        address_in: AddressUpdate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a specific address for the current user.
    """
    from app.models.address import Address

    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()

    if not address:
        raise NotFoundException(detail="Address not found")

    # If setting as default, unset other defaults
    if address_in.is_default and address_in.is_default != address.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.id != address_id,
            Address.address_type == (address_in.address_type or address.address_type)
        ).update({"is_default": False})

    # Update address
    for key, value in address_in.model_dump(exclude_unset=True).items():
        setattr(address, key, value)

    db.add(address)
    db.commit()
    db.refresh(address)

    return address


@router.delete("/me/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user_address(
        *,
        db: Session = Depends(get_db),
        address_id: str,
        current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a specific address for the current user.
    """
    from app.models.address import Address

    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()

    if not address:
        raise NotFoundException(detail="Address not found")

    db.delete(address)
    db.commit()

    # If this was a default address, set another address as default
    if address.is_default:
        another_address = db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.address_type == address.address_type
        ).first()

        if another_address:
            another_address.is_default = True
            db.add(another_address)
            db.commit()

    # For status code 204, we should not return anything
