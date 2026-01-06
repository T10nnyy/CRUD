from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fastapi_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "items")

# Global database client
db_client: Optional[AsyncIOMotorClient] = None


class Database:
    """Database connection manager"""
    
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        try:
            cls.client = AsyncIOMotorClient(MONGODB_URL)
            cls.database = cls.client[DATABASE_NAME]
            
            # Test connection
            await cls.client.admin.command('ping')
            print(f"✓ Connected to MongoDB at {MONGODB_URL}")
            print(f"✓ Using database: {DATABASE_NAME}")
            
        except Exception as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            raise e

    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("✓ MongoDB connection closed")

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if cls.database is None:
            raise Exception("Database not initialized. Call connect_db() first.")
        return cls.database

    @classmethod
    def get_collection(cls, collection_name: str = COLLECTION_NAME):
        """Get collection instance"""
        database = cls.get_database()
        return database[collection_name]


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get database instance"""
    return Database.get_database()


async def get_collection():
    """Dependency to get collection instance"""
    return Database.get_collection(COLLECTION_NAME)