import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from database import Database, get_database, get_collection


@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection is established"""
    db = Database.get_database()
    
    assert db is not None
    assert isinstance(db, AsyncIOMotorDatabase)


@pytest.mark.asyncio
async def test_database_ping():
    """Test database ping command"""
    db = Database.get_database()
    
    result = await db.client.admin.command('ping')
    
    assert result is not None
    assert result.get('ok') == 1.0


@pytest.mark.asyncio
async def test_get_database_dependency():
    """Test get_database dependency function"""
    db = await get_database()
    
    assert db is not None
    assert isinstance(db, AsyncIOMotorDatabase)


@pytest.mark.asyncio
async def test_get_collection():
    """Test getting collection instance"""
    collection = Database.get_collection("test_collection")
    
    assert collection is not None
    assert isinstance(collection, AsyncIOMotorCollection)
    assert collection.name == "test_collection"


@pytest.mark.asyncio
async def test_get_collection_dependency():
    """Test get_collection dependency function"""
    collection = await get_collection()
    
    assert collection is not None
    assert isinstance(collection, AsyncIOMotorCollection)


@pytest.mark.asyncio
async def test_database_operations(test_collection):
    """Test basic database operations"""
    # Insert
    result = await test_collection.insert_one({"test": "data"})
    assert result.inserted_id is not None
    
    # Find
    document = await test_collection.find_one({"_id": result.inserted_id})
    assert document is not None
    assert document["test"] == "data"
    
    # Update
    update_result = await test_collection.update_one(
        {"_id": result.inserted_id},
        {"$set": {"test": "updated"}}
    )
    assert update_result.modified_count == 1
    
    # Delete
    delete_result = await test_collection.delete_one({"_id": result.inserted_id})
    assert delete_result.deleted_count == 1


@pytest.mark.asyncio
async def test_collection_count(test_collection):
    """Test counting documents in collection"""
    # Insert test documents
    await test_collection.insert_many([
        {"name": "Item 1"},
        {"name": "Item 2"},
        {"name": "Item 3"}
    ])
    
    count = await test_collection.count_documents({})
    
    assert count == 3


@pytest.mark.asyncio
async def test_collection_find_multiple(test_collection):
    """Test finding multiple documents"""
    # Insert test documents
    test_docs = [
        {"name": "Item 1", "category": "A"},
        {"name": "Item 2", "category": "B"},
        {"name": "Item 3", "category": "A"}
    ]
    await test_collection.insert_many(test_docs)
    
    # Find documents
    cursor = test_collection.find({"category": "A"})
    results = await cursor.to_list(length=None)
    
    assert len(results) == 2
    assert all(doc["category"] == "A" for doc in results)


@pytest.mark.asyncio
async def test_collection_aggregation(test_collection):
    """Test aggregation pipeline"""
    # Insert test documents
    await test_collection.insert_many([
        {"name": "Item 1", "price": 100, "quantity": 2},
        {"name": "Item 2", "price": 50, "quantity": 5},
        {"name": "Item 3", "price": 200, "quantity": 1}
    ])
    
    # Aggregate total value
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total": {"$sum": {"$multiply": ["$price", "$quantity"]}}
            }
        }
    ]
    
    result = await test_collection.aggregate(pipeline).to_list(1)
    
    assert len(result) == 1
    assert result[0]["total"] == 650  # (100*2) + (50*5) + (200*1)


@pytest.mark.asyncio
async def test_collection_index_creation(test_collection):
    """Test creating indexes"""
    # Create index
    await test_collection.create_index("name")
    
    # Get indexes
    indexes = await test_collection.index_information()
    
    assert "name_1" in indexes


@pytest.mark.asyncio
async def test_database_list_collections():
    """Test listing collections in database"""
    db = Database.get_database()
    
    collections = await db.list_collection_names()
    
    assert isinstance(collections, list)