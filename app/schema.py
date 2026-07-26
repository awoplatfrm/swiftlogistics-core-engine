from pydantic import model_validator, Field, EmailStr, BaseModel
from typing import List, Optional
from datetime import datetime


class ParcelItem(BaseModel):

    description: str
    value_ngn: float = Field(..., gt=0, description="value should be in naira")
    weight: float = Field(..., gt=0, description="weight in kg")
    quantity: Optional[int] = 1


class Dimension(BaseModel):
    length: float
    width: float
    height: float


class RegisterShipment(BaseModel):
    description: Optional[str] = None
    total_weight: float
    dimension: Optional[Dimension] = None
    parcels: List[ParcelItem]


class RegisterShipmentResponse(BaseModel):
    id: int
    merchant_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RegisterMerchant(BaseModel):
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


class LoginMerchant(BaseModel):
    email: EmailStr
    password: str


class RegisterMerchantResponse(BaseModel):
    id: int
    business_name: str
    email: EmailStr
    phone_number: str
    is_loggedin: bool
    account_created_at: datetime

    class Config:
        from_attributes = True


class MerchantTokenResponse(BaseModel):
    access_token: str
    token_type: str
    merchant: RegisterMerchantResponse
