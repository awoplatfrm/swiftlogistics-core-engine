from pydantic import model_validator, Field, EmailStr, BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


# merchant Auth
class MerchantIn(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone_number: str = Field(..., min_length=11, max_length=14)
    password: str = Field(
        ..., min_length=6, description="password must be atleast 6 characters"
    )
    confirm_password: str

    @model_validator(mode="after")
    def password_check(self):
        if self.password != self.confirm_password:
            raise ValueError("password do not match")
        return self


class MerchantOut(BaseModel):
    id: int
    business_name: str
    email: EmailStr
    phone_number: str
    is_loggedin: bool
    account_created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginMerchant(BaseModel):
    email: EmailStr
    password: str


class MerchantTokenOut(BaseModel):
    access_token: str
    token_type: str
    merchant: MerchantOut


# shipment operation


class Contact(BaseModel):
    full_name: str = Field(..., min_length=2, json_schema_extra=" joe daniel")
    email: Optional[str] = Field(None, json_schema_extra="example@email.com")
    phone_number: str = Field(..., min_length=11, max_length=14)
    address: str = Field(..., json_schema_extra="12 Marina Road")
    city: str = Field(..., json_schema_extra="Lagos Island")
    state: str = Field(..., json_schema_extra="Lagos")
    country: str = Field(..., json_schema_extra="Nigeria")


class ContactIn(Contact):
    pass


class ContactOut(Contact):

    pass
    model_config = ConfigDict(from_attributes=True)


class ParcelItem(BaseModel):
    description: str
    value_ngn: float = Field(..., gt=0, description="value should be in naira")
    weight: float = Field(..., gt=0, description="weight in kg")
    quantity: Optional[int] = 1


class Dimensions(BaseModel):
    length: float
    width: float
    height: float


class ShipmentIn(BaseModel):
    description: str = Field(..., min_length=2, json_schema_extra="a pair of shoe")
    total_weight: float = Field(..., gt=0, json_schema_extra=3.5)
    dimensions: Dimensions
    parcels: List[ParcelItem]
    status: Optional[str] = Field(default="pending", json_schema_extra="in_transit")
    sender: ContactIn
    recipient: ContactIn


class ShipmentOut(BaseModel):
    id: int
    merchant_id: int
    sender: ContactOut
    recipient: ContactOut
    model_config = ConfigDict(from_attributes=True)


class ContactUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2)
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


class ContactUpdateIn(ContactUpdate):
    pass
    model_config = ConfigDict(from_attributes=True)


class ShipmentUpdateContactOut(BaseModel):
    id: int
    full_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: str
    city: str
    state: str
    country: str

    model_config = ConfigDict(from_attributes=True)


class ShipmentsUpdateIn(BaseModel):
    description: Optional[str] = Field(None)
    total_weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[Dimensions] = None
    parcels: List[ParcelItem] | None = None
    status: Optional[str] = Field(None)
    sender: Optional[ContactUpdateIn] = None
    recipient: Optional[ContactUpdateIn] = None


class ShipmentUpdateOut(BaseModel):
    id: int
    merchant_id: int
    description: Optional[str] = None
    total_weight: float
    dimensions: Optional[Dimensions] = None
    parcels: List[ParcelItem] = []
    status: str
    account_created_at: datetime

    sender: ShipmentUpdateContactOut
    recipient: ShipmentUpdateContactOut

    model_config = ConfigDict(from_attributes=True)


class PaginatedShipments(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[ShipmentOut]
