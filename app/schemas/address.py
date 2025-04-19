import datetime
import uuid
from typing import Optional

from pydantic import BaseModel

from app.models.address import AddressType


# Shared properties
class AddressBase(BaseModel):
    """Base address schema with common properties."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    street_address_1: str
    street_address_2: Optional[str] = None
    city: str
    state_province: Optional[str] = None
    postal_code: str
    country: str
    phone_number: Optional[str] = None
    address_type: Optional[AddressType] = AddressType.BOTH
    is_default: Optional[bool] = False


# Properties to receive via API on creation
class AddressCreate(AddressBase):
    """Schema for address creation."""
    pass


# Properties to receive via API on update
class AddressUpdate(AddressBase):
    """Schema for address update."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    street_address_1: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


# Properties shared by models stored in DB
class AddressInDBBase(AddressBase):
    """Base schema for addresses in DB."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


# Properties to return to client
class Address(AddressInDBBase):
    """Schema for address response."""
    pass


# Properties stored in DB
class AddressInDB(AddressInDBBase):
    """Schema for address stored in DB."""
    pass


# Schema for address in order context
class OrderAddress(BaseModel):
    """Schema for address in order context."""
    first_name: str
    last_name: str
    company: Optional[str] = None
    street_address_1: str
    street_address_2: Optional[str] = None
    city: str
    state_province: Optional[str] = None
    postal_code: str
    country: str
    phone_number: Optional[str] = None

    model_config = {"from_attributes": True}
