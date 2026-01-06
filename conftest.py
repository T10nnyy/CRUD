import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from typing import AsyncGenerator
from bson import ObjectId

from database import Database


# Test database configuration
TEST_MONGODB_URL = "mongodb://localhost:27017"
TEST_DATABASE_NAME = "test_fastapi_db"
TEST_COLLECTION_NAME = "test_items"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Setup test database connection"""
    await Database.connect_db()
    yield
    await Database.close_db()


@pytest.fixture
async def test_collection():
    """Create a test collection and clean up after tests"""
    database = Database.get_database()
    collection = database[TEST_COLLECTION_NAME]
    
    # Clean collection before test
    await collection.delete_many({})
    
    yield collection
    
    # Clean collection after test
    await collection.delete_many({})


@pytest.fixture
async def test_item(test_collection):
    """Create a single test item"""
    item_data = {
        "name": "Test Laptop",
        "description": "A test laptop for testing",
        "price": 999.99,
        "quantity": 5,
        "category": "Electronics",
        "is_active": True
    }
    
    result = await test_collection.insert_one(item_data)
    item_data["_id"] = str(result.inserted_id)
    
    return item_data


@pytest.fixture
async def test_items(test_collection):
    """Create multiple test items"""
    items_data = [
        {
            "name": "Gaming Laptop",
            "description": "High-performance gaming laptop",
            "price": 1499.99,
            "quantity": 3,
            "category": "Electronics",
            "is_active": True
        },
        {
            "name": "Office Laptop",
            "description": "Business laptop",
            "price": 899.99,
            "quantity": 10,
            "category": "Electronics",
            "is_active": True
        },
        {
            "name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse",
            "price": 29.99,
            "quantity": 50,
            "category": "Accessories",
            "is_active": True
        },
        {
            "name": "Mechanical Keyboard",
            "description": "RGB mechanical keyboard",
            "price": 149.99,
            "quantity": 2,
            "category": "Accessories",
            "is_active": True
        },
        {
            "name": "USB-C Hub",
            "description": "7-in-1 USB-C hub",
            "price": 49.99,
            "quantity": 15,
            "category": "Accessories",
            "is_active": False  # Inactive item
        }
    ]
    
    result = await test_collection.insert_many(items_data)
    
    # Add IDs to items
    for i, item_id in enumerate(result.inserted_ids):
        items_data[i]["_id"] = str(item_id)
    
    return items_data


@pytest.fixture
async def test_item_id(test_item):
    """Get test item ID"""
    return test_item["_id"]


@pytest.fixture
def sample_item_create_data():
    """Sample data for creating an item"""
    return {
        "name": "Sample Item",
        "description": "Sample description",
        "price": 99.99,
        "quantity": 10,
        "category": "Sample",
        "is_active": True
    }


@pytest.fixture
def sample_item_update_data():
    """Sample data for updating an item"""
    return {
        "price": 149.99,
        "quantity": 15
    }


@pytest.fixture
async def empty_collection(test_collection):
    """Provide an empty collection"""
    await test_collection.delete_many({})
    return test_collection


@pytest.fixture
def invalid_object_id():
    """Provide an invalid ObjectId string"""
    return "invalid_id_format"


@pytest.fixture
def valid_object_id():
    """Provide a valid but non-existent ObjectId"""
    return str(ObjectId())


@pytest.fixture
async def cleanup_test_items(test_collection):
    """Cleanup fixture that runs after test"""
    yield
    await test_collection.delete_many({})