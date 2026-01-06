from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List

from database import Database, get_collection
from models import ItemCreate, ItemUpdate, ItemResponse
from schemas import (
    ItemListResponseSchema,
    MessageResponseSchema,
    HealthCheckSchema,
    ItemResponseSchema
)
from crud import CRUDOperations


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    await Database.connect_db()
    
    yield
    
    # Shutdown
    await Database.close_db()


# Initialize FastAPI app
app = FastAPI(
    title="FastAPI MongoDB CRUD API",
    description="Complete CRUD API with FastAPI and MongoDB (Modular Structure)",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=MessageResponseSchema, tags=["Root"])
async def root():
    """Root endpoint"""
    return {"message": "Welcome to FastAPI MongoDB CRUD API"}


@app.get("/health", response_model=HealthCheckSchema, tags=["Health"])
async def health_check():
    """Check API and database health"""
    try:
        database = Database.get_database()
        await database.client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "message": "All systems operational"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )


@app.post(
    "/items/",
    response_model=ItemResponseSchema,
    status_code=status.HTTP_201_CREATED,
    tags=["Items"]
)
async def create_item(item: ItemCreate):
    """Create a new item"""
    collection = await get_collection()
    crud = CRUDOperations(collection)
    
    created_item = await crud.create(item)
    return created_item


@app.get("/items/", response_model=List[ItemResponseSchema], tags=["Items"])
async def get_all_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return")
):
    """Get all items with pagination"""
    collection = await get_collection()
    crud = CRUDOperations(collection)
    
    items, total = await crud.get_all(skip=skip, limit=limit)
    return items


@app.get("/items/search/", response_model=List[ItemResponseSchema], tags=["Items"])
async def search_items(
    q: str = Query(..., min_length=1, description="Search term"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Search items by name or description"""
    collection = await get_collection()
    crud = CRUDOperations(collection)
    
    items, total = await crud.search(q, skip=skip, limit=limit)
    return items


@app.get("/items/category/{category}", response_model=List[ItemResponseSchema], tags=["Items"])
async def get_items_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get items by category"""
    collection = await get_collection()
    crud = CRUDOperations(collection)
    
    items, total = await crud.get_by_category(category, skip=skip, limit=limit)
    return items


@app.get("/items/active/", response_model=List[ItemResponseSchema], tags=["Items"])
async def get_active_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get only active items"""
    collection = await get_collection()
    crud = CRUDOperations(collection)
    
    items, total = await crud.get_active_items(skip=skip, limit=limit)
    return items


@app.get("/items/low-stock/", response_model=List[ItemResponseSchema], tags=["Items"])
async def get_low_stock_items(
    threshold: int = Query(5, ge=0, description="Stock threshold")
):
    """Get items with low stock"""
    collection = await get_collection()
    crud = CRUDOperations(collection)
    
    items = await crud.get_low_stock_items(threshold=threshold)
    return items


@app.get("/items/{item_id}", response_model=ItemResponseSchema, tags=["Items"])
async def get_item(item_id: str):
    """Get a single item by ID"""
    collection = await get_collection()
    crud = CRUDOperations(collection)
    
    item = await crud.get_by_id(item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    return item


@app.put("/items/{item_id}", response_model=ItemResponseSchema, tags=["Items"])
async def update_item(item_id: str, item_update: ItemUpdate):
    """Update an existing item"""
    collection = await get_collection()
    crud = CRUDOperations(collection)
    
    updated_item = await crud.update(item_id, item_update)
    
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found or no valid fields to update"
        )
    
    return updated_item


@app.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Items"]
)
async def delete_item(item_id: str):
    """Permanently delete an item"""
    collection = await get_collection()
    crud = CRUDOperations(collection)
    
    deleted = await crud.delete(item_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    return None


@app.patch("/items/{item_id}/deactivate", response_model=ItemResponseSchema, tags=["Items"])
async def deactivate_item(item_id: str):
    """Soft delete (deactivate) an item"""
    collection = await get_collection()
    crud = CRUDOperations(collection)
    
    item = await crud.soft_delete(item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    return item


@app.get("/stats/total-value", tags=["Statistics"])
async def get_total_inventory_value():
    """Get total inventory value"""
    collection = await get_collection()
    crud = CRUDOperations(collection)
    
    total_value = await crud.get_total_value()
    
    return {
        "total_inventory_value": round(total_value, 2),
        "currency": "USD"
    }


@app.post("/items/bulk/update-prices", tags=["Bulk Operations"])
async def bulk_update_prices(multiplier: float = Query(..., gt=0, description="Price multiplier")):
    """Bulk update all item prices"""
    collection = await get_collection()
    crud = CRUDOperations(collection)
    
    modified_count = await crud.bulk_update_prices(multiplier)
    
    return {
        "message": f"Successfully updated {modified_count} items",
        "modified_count": modified_count,
        "multiplier": multiplier
    }