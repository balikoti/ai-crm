from typing import Optional, Any, Dict
from pydantic import BaseModel, Field

class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = "new"
    attrs: Dict[str, Any] = Field(default_factory=dict)

class ContactOut(ContactCreate):
    id: int
    class Config:
        from_attributes = True

class PropertyCreate(BaseModel):
    address: str
    city: Optional[str] = None
    state_province: Optional[str] = None
    country: Optional[str] = "Canada"
    status: Optional[str] = "prospect"
    attrs: Dict[str, Any] = Field(default_factory=dict)

class PropertyOut(PropertyCreate):
    id: int
    class Config:
        from_attributes = True

class TransactionCreate(BaseModel):
    contact_id: int
    property_id: int
    side: Optional[str] = "buy"
    stage: Optional[str] = "lead"
    offer_price: Optional[float] = None
    close_price: Optional[float] = None
    attrs: Dict[str, Any] = Field(default_factory=dict)

class TransactionOut(TransactionCreate):
    id: int
    class Config:
        from_attributes = True

class PatchAttrs(BaseModel):
    attrs: Dict[str, Any] = Field(default_factory=dict)
