from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from typing import List, Optional, Dict, Any
from models import ItemCreate, ItemUpdate


class CRUDOperations:
    """CRUD operations for items collection"""

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, item_data: ItemCreate) -> Dict[str, Any]:
        """Create a new item"""
        item_dict = item_data.model_dump()
        result = await self.collection.insert_one(item_dict)
        
        created_item = await self.collection.find_one({"_id": result.inserted_id})
        created_item["_id"] = str(created_item["_id"])
        
        return created_item

    async def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a single item by ID"""
        if not ObjectId.is_valid(item_id):
            return None
        
        item = await self.collection.find_one({"_id": ObjectId(item_id)})
        
        if item:
            item["_id"] = str(item["_id"])
        
        return item

    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get all items with pagination and optional filtering"""
        query = filter_dict if filter_dict else {}
        
        # Get total count
        total = await self.collection.count_documents(query)
        
        # Get items
        items = []
        cursor = self.collection.find(query).skip(skip).limit(limit)
        
        async for document in cursor:
            document["_id"] = str(document["_id"])
            items.append(document)
        
        return items, total

    async def get_by_category(
        self, 
        category: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get items by category"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filter_dict={"category": category}
        )

    async def get_active_items(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get only active items"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filter_dict={"is_active": True}
        )

    async def update(
        self, 
        item_id: str, 
        item_data: ItemUpdate
    ) -> Optional[Dict[str, Any]]:
        """Update an existing item"""
        if not ObjectId.is_valid(item_id):
            return None
        
        # Remove None values from update
        update_data = {
            k: v for k, v in item_data.model_dump().items() 
            if v is not None
        }
        
        if not update_data:
            return None
        
        result = await self.collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        updated_item = await self.collection.find_one({"_id": ObjectId(item_id)})
        updated_item["_id"] = str(updated_item["_id"])
        
        return updated_item

    async def delete(self, item_id: str) -> bool:
        """Delete an item"""
        if not ObjectId.is_valid(item_id):
            return False
        
        result = await self.collection.delete_one({"_id": ObjectId(item_id)})
        
        return result.deleted_count > 0

    async def soft_delete(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Soft delete an item by setting is_active to False"""
        if not ObjectId.is_valid(item_id):
            return None
        
        result = await self.collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": {"is_active": False}}
        )
        
        if result.matched_count == 0:
            return None
        
        updated_item = await self.collection.find_one({"_id": ObjectId(item_id)})
        updated_item["_id"] = str(updated_item["_id"])
        
        return updated_item

    async def search(
        self, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> tuple[List[Dict[str, Any]], int]:
        """Search items by name or description"""
        query = {
            "$or": [
                {"name": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}}
            ]
        }
        
        return await self.get_all(skip=skip, limit=limit, filter_dict=query)

    async def bulk_update_prices(
        self, 
        multiplier: float
    ) -> int:
        """Bulk update all item prices by a multiplier"""
        result = await self.collection.update_many(
            {},
            [{"$set": {"price": {"$multiply": ["$price", multiplier]}}}]
        )
        
        return result.modified_count

    async def get_total_value(self) -> float:
        """Calculate total inventory value"""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_value": {
                        "$sum": {"$multiply": ["$price", "$quantity"]}
                    }
                }
            }
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(1)
        
        if result:
            return result[0]["total_value"]
        return 0.0

    async def get_low_stock_items(
        self, 
        threshold: int = 5
    ) -> List[Dict[str, Any]]:
        """Get items with quantity below threshold"""
        items = []
        cursor = self.collection.find({"quantity": {"$lt": threshold}})
        
        async for document in cursor:
            document["_id"] = str(document["_id"])
            items.append(document)
        
        return items