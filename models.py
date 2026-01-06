from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class ItemBase(BaseModel):
    """Base model for Item with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, max_length=500, description="Item description")
    price: float = Field(..., gt=0, description="Item price (must be greater than 0)")
    quantity: int = Field(..., ge=0, description="Item quantity (must be 0 or greater)")
    category: Optional[str] = Field(None, max_length=50, description="Item category")
    is_active: bool = Field(default=True, description="Whether the item is active")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laptop",
                "description": "High-performance gaming laptop",
                "price": 1299.99,
                "quantity": 10,
                "category": "Electronics",
                "is_active": True
            }
        }


class ItemCreate(ItemBase):
    """Model for creating a new item"""
    pass


class ItemUpdate(BaseModel):
    """Model for updating an existing item (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "price": 1199.99,
                "quantity": 8
            }
        }


class ItemInDB(ItemBase):
    """Model for item as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ItemResponse(ItemBase):
    """Model for item in API responses"""
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Laptop",
                "description": "High-performance gaming laptop",
                "price": 1299.99,
                "quantity": 10,
                "category": "Electronics",
                "is_active": True
            }
        }