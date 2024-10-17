from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime, date
from bson import ObjectId

class ItemBase(BaseModel):
    name: str = Field(..., example="Sample Item")
    email: EmailStr = Field(..., example="user@example.com")
    item_name: str = Field(..., example="Widget")
    quantity: int = Field(..., ge=0, example=10)
    expiry_date: date = Field(..., example="2024-12-31")

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Updated Item")
    email: Optional[EmailStr] = Field(None, example="newuser@example.com")
    item_name: Optional[str] = Field(None, example="Gadget")
    quantity: Optional[int] = Field(None, ge=0, example=20)
    expiry_date: Optional[date] = Field(None, example="2025-01-01")

class Item(ItemBase):

    id: str = Field(..., alias="_id")
    insert_date: datetime = Field(default_factory=datetime.utcnow)

    @validator('id', pre=True, always=True)
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        model_config = {
            "populate_by_name": True,
            "json_encoders": {
                datetime: lambda dt: dt.isoformat(),
            },
            "from_attributes": True,
        }

class ClockInBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    location: str = Field(..., example="New York Office")

class ClockInCreate(ClockInBase):
    pass

class ClockInUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, example="updateduser@example.com")
    location: Optional[str] = Field(None, example="San Francisco Office")

class ClockInRecord(ClockInBase):
    id: str = Field(..., alias="_id")
    insert_datetime: datetime = Field(default_factory=datetime.utcnow)

    @validator('id', pre=True, always=True)
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        model_config = {
            "populate_by_name": True,
            "json_encoders": {
                datetime: lambda dt: dt.isoformat(),
            },
            "from_attributes": True,
        }
