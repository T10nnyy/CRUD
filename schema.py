from pydantic import BaseModel, Field
from typing import Optional, List


class ItemSchema(BaseModel):
    """Schema for item data validation"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    category: Optional[str] = Field(None, max_length=50)
    is_active: bool = Field(default=True)


class ItemCreateSchema(ItemSchema):
    """Schema for creating a new item"""
    pass


class ItemUpdateSchema(BaseModel):
    """Schema for updating an item (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class ItemResponseSchema(ItemSchema):
    """Schema for item response with ID"""
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True


class ItemListResponseSchema(BaseModel):
    """Schema for list of items response"""
    items: List[ItemResponseSchema]
    total: int
    skip: int
    limit: int


class MessageResponseSchema(BaseModel):
    """Schema for generic message responses"""
    message: str


class HealthCheckSchema(BaseModel):
    """Schema for health check response"""
    status: str
    database: str
    message: Optional[str] = None


class ErrorResponseSchema(BaseModel):
    """Schema for error responses"""
    detail: str