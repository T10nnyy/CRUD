from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional, List
import os
from contextlib import asynccontextmanager

# Pydantic models
class PyObjectId(ObjectId):
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
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)


class ItemResponse(ItemBase):
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# Database connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "fastapi_db"
COLLECTION_NAME = "items"

db_client: Optional[AsyncIOMotorClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_client
    db_client = AsyncIOMotorClient(MONGODB_URL)
    try:
        await db_client.admin.command('ping')
        print("Connected to MongoDB successfully!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
    
    yield
    
    # Shutdown
    if db_client:
        db_client.close()
        print("MongoDB connection closed")


# FastAPI app
app = FastAPI(
    title="FastAPI MongoDB CRUD",
    description="Simple CRUD API with FastAPI and MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_collection():
    return db_client[DATABASE_NAME][COLLECTION_NAME]


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to FastAPI MongoDB CRUD API"}


@app.post("/items/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, tags=["Items"])
async def create_item(item: ItemCreate):
    """Create a new item"""
    collection = get_collection()
    item_dict = item.model_dump()
    result = await collection.insert_one(item_dict)
    
    created_item = await collection.find_one({"_id": result.inserted_id})
    created_item["_id"] = str(created_item["_id"])
    
    return created_item


@app.get("/items/", response_model=List[ItemResponse], tags=["Items"])
async def get_all_items(skip: int = 0, limit: int = 100):
    """Get all items with pagination"""
    collection = get_collection()
    items = []
    
    cursor = collection.find().skip(skip).limit(limit)
    async for document in cursor:
        document["_id"] = str(document["_id"])
        items.append(document)
    
    return items


@app.get("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
async def get_item(item_id: str):
    """Get a single item by ID"""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID format"
        )
    
    collection = get_collection()
    item = await collection.find_one({"_id": ObjectId(item_id)})
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    item["_id"] = str(item["_id"])
    return item


@app.put("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
async def update_item(item_id: str, item_update: ItemUpdate):
    """Update an existing item"""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID format"
        )
    
    collection = get_collection()
    
    # Remove None values from update
    update_data = {k: v for k, v in item_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )
    
    result = await collection.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    updated_item = await collection.find_one({"_id": ObjectId(item_id)})
    updated_item["_id"] = str(updated_item["_id"])
    
    return updated_item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Items"])
async def delete_item(item_id: str):
    """Delete an item"""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID format"
        )
    
    collection = get_collection()
    result = await collection.delete_one({"_id": ObjectId(item_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    return None


@app.get("/health", tags=["Health"])
async def health_check():
    """Check if the API and database are running"""
    try:
        await db_client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )