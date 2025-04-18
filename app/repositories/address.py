import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.address import Address, AddressType
from app.repositories.base import BaseRepository
from app.schemas.address import AddressCreate, AddressUpdate


class AddressRepository(BaseRepository[Address, AddressCreate, AddressUpdate]):
    """
    Address repository for data access operations.
    """

    def get_user_addresses(self, db: Session, user_id: uuid.UUID) -> List[Address]:
        """
        Get all addresses for a user.
        """
        return db.query(Address).filter(Address.user_id == user_id).all()

    def get_user_address_by_id(self, db: Session, user_id: uuid.UUID, address_id: uuid.UUID) -> Optional[Address]:
        """
        Get a specific address for a user by ID.
        """
        return db.query(Address).filter(
            Address.id == address_id,
            Address.user_id == user_id
        ).first()

    def get_default_shipping_address(self, db: Session, user_id: uuid.UUID) -> Optional[Address]:
        """
        Get the default shipping address for a user.
        """
        return db.query(Address).filter(
            Address.user_id == user_id,
            Address.is_default == True,
            (Address.address_type == AddressType.SHIPPING) | (Address.address_type == AddressType.BOTH)
        ).first()

    def get_default_billing_address(self, db: Session, user_id: uuid.UUID) -> Optional[Address]:
        """
        Get the default billing address for a user.
        """
        return db.query(Address).filter(
            Address.user_id == user_id,
            Address.is_default == True,
            (Address.address_type == AddressType.BILLING) | (Address.address_type == AddressType.BOTH)
        ).first()

    def create_address(self, db: Session, obj_in: AddressCreate, user_id: uuid.UUID) -> Address:
        """
        Create a new address for a user.
        """
        # If this is the first address or marked as default, unset other defaults
        if obj_in.is_default or db.query(Address).filter(Address.user_id == user_id).count() == 0:
            db.query(Address).filter(
                Address.user_id == user_id,
                Address.address_type == obj_in.address_type
            ).update({"is_default": False})
            obj_in_data = obj_in.dict()
            obj_in_data["is_default"] = True
        else:
            obj_in_data = obj_in.dict()

        # Create address
        db_obj = Address(
            **obj_in_data,
            user_id=user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_address(
            self, db: Session, db_obj: Address, obj_in: AddressUpdate, user_id: uuid.UUID
    ) -> Address:
        """
        Update an address.
        """
        # If setting as default, unset other defaults
        if obj_in.is_default and obj_in.is_default != db_obj.is_default:
            address_type = obj_in.address_type or db_obj.address_type
            db.query(Address).filter(
                Address.user_id == user_id,
                Address.id != db_obj.id,
                Address.address_type == address_type
            ).update({"is_default": False})

        # Update address
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def set_default_after_deletion(self, db: Session, user_id: uuid.UUID, address_type: AddressType) -> None:
        """
        Set another address as default after deletion of a default address.
        """
        another_address = db.query(Address).filter(
            Address.user_id == user_id,
            Address.address_type == address_type
        ).first()

        if another_address:
            another_address.is_default = True
            db.add(another_address)
            db.commit()


address_repository = AddressRepository(Address)
