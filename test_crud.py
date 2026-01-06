import pytest
from bson import ObjectId
from models import ItemCreate, ItemUpdate
from crud import CRUDOperations


@pytest.mark.asyncio
async def test_create_item(test_collection):
    """Test creating a new item"""
    crud = CRUDOperations(test_collection)
    
    item_data = ItemCreate(
        name="Test Item",
        description="Test description",
        price=99.99,
        quantity=10,
        category="Test",
        is_active=True
    )
    
    result = await crud.create(item_data)
    
    assert result is not None
    assert result["name"] == "Test Item"
    assert result["price"] == 99.99
    assert "_id" in result


@pytest.mark.asyncio
async def test_get_by_id(test_collection, test_item):
    """Test getting item by ID"""
    crud = CRUDOperations(test_collection)
    item_id = test_item["_id"]
    
    result = await crud.get_by_id(item_id)
    
    assert result is not None
    assert result["_id"] == item_id
    assert result["name"] == test_item["name"]


@pytest.mark.asyncio
async def test_get_by_invalid_id(test_collection):
    """Test getting item with invalid ID"""
    crud = CRUDOperations(test_collection)
    
    result = await crud.get_by_id("invalid_id")
    
    assert result is None


@pytest.mark.asyncio
async def test_get_by_nonexistent_id(test_collection):
    """Test getting non-existent item"""
    crud = CRUDOperations(test_collection)
    fake_id = str(ObjectId())
    
    result = await crud.get_by_id(fake_id)
    
    assert result is None


@pytest.mark.asyncio
async def test_get_all(test_collection, test_items):
    """Test getting all items"""
    crud = CRUDOperations(test_collection)
    
    items, total = await crud.get_all()
    
    assert isinstance(items, list)
    assert len(items) > 0
    assert total >= len(items)


@pytest.mark.asyncio
async def test_get_all_with_pagination(test_collection, test_items):
    """Test getting items with pagination"""
    crud = CRUDOperations(test_collection)
    
    items, total = await crud.get_all(skip=0, limit=2)
    
    assert len(items) <= 2
    assert total >= len(items)


@pytest.mark.asyncio
async def test_get_all_with_filter(test_collection, test_items):
    """Test getting items with filter"""
    crud = CRUDOperations(test_collection)
    
    items, total = await crud.get_all(filter_dict={"category": "Electronics"})
    
    assert isinstance(items, list)
    for item in items:
        assert item.get("category") == "Electronics"


@pytest.mark.asyncio
async def test_get_by_category(test_collection, test_items):
    """Test getting items by category"""
    crud = CRUDOperations(test_collection)
    
    items, total = await crud.get_by_category("Electronics")
    
    assert isinstance(items, list)
    for item in items:
        assert item.get("category") == "Electronics"


@pytest.mark.asyncio
async def test_get_active_items(test_collection, test_items):
    """Test getting only active items"""
    crud = CRUDOperations(test_collection)
    
    items, total = await crud.get_active_items()
    
    assert isinstance(items, list)
    for item in items:
        assert item.get("is_active") is True


@pytest.mark.asyncio
async def test_update_item(test_collection, test_item):
    """Test updating an item"""
    crud = CRUDOperations(test_collection)
    item_id = test_item["_id"]
    
    update_data = ItemUpdate(price=149.99, quantity=15)
    result = await crud.update(item_id, update_data)
    
    assert result is not None
    assert result["price"] == 149.99
    assert result["quantity"] == 15


@pytest.mark.asyncio
async def test_update_partial_fields(test_collection, test_item):
    """Test updating only some fields"""
    crud = CRUDOperations(test_collection)
    item_id = test_item["_id"]
    
    original_name = test_item["name"]
    update_data = ItemUpdate(price=199.99)
    result = await crud.update(item_id, update_data)
    
    assert result is not None
    assert result["price"] == 199.99
    assert result["name"] == original_name  # Name should remain unchanged


@pytest.mark.asyncio
async def test_update_nonexistent_item(test_collection):
    """Test updating non-existent item"""
    crud = CRUDOperations(test_collection)
    fake_id = str(ObjectId())
    
    update_data = ItemUpdate(price=99.99)
    result = await crud.update(fake_id, update_data)
    
    assert result is None


@pytest.mark.asyncio
async def test_update_with_empty_data(test_collection, test_item):
    """Test updating with no valid fields"""
    crud = CRUDOperations(test_collection)
    item_id = test_item["_id"]
    
    update_data = ItemUpdate()
    result = await crud.update(item_id, update_data)
    
    assert result is None


@pytest.mark.asyncio
async def test_delete_item(test_collection, test_item):
    """Test deleting an item"""
    crud = CRUDOperations(test_collection)
    item_id = test_item["_id"]
    
    result = await crud.delete(item_id)
    
    assert result is True
    
    # Verify item is deleted
    deleted_item = await crud.get_by_id(item_id)
    assert deleted_item is None


@pytest.mark.asyncio
async def test_delete_nonexistent_item(test_collection):
    """Test deleting non-existent item"""
    crud = CRUDOperations(test_collection)
    fake_id = str(ObjectId())
    
    result = await crud.delete(fake_id)
    
    assert result is False


@pytest.mark.asyncio
async def test_soft_delete(test_collection, test_item):
    """Test soft deleting an item"""
    crud = CRUDOperations(test_collection)
    item_id = test_item["_id"]
    
    result = await crud.soft_delete(item_id)
    
    assert result is not None
    assert result["is_active"] is False


@pytest.mark.asyncio
async def test_search_items(test_collection, test_items):
    """Test searching items"""
    crud = CRUDOperations(test_collection)
    
    items, total = await crud.search("Laptop")
    
    assert isinstance(items, list)
    assert total >= 0


@pytest.mark.asyncio
async def test_search_case_insensitive(test_collection, test_items):
    """Test case-insensitive search"""
    crud = CRUDOperations(test_collection)
    
    items_lower, _ = await crud.search("laptop")
    items_upper, _ = await crud.search("LAPTOP")
    
    assert len(items_lower) == len(items_upper)


@pytest.mark.asyncio
async def test_bulk_update_prices(test_collection, test_items):
    """Test bulk updating prices"""
    crud = CRUDOperations(test_collection)
    
    modified_count = await crud.bulk_update_prices(1.5)
    
    assert modified_count >= 0
    
    # Verify prices are updated
    items, _ = await crud.get_all()
    for item in items:
        assert item["price"] > 0


@pytest.mark.asyncio
async def test_get_total_value(test_collection, test_items):
    """Test calculating total inventory value"""
    crud = CRUDOperations(test_collection)
    
    total_value = await crud.get_total_value()
    
    assert isinstance(total_value, (int, float))
    assert total_value >= 0


@pytest.mark.asyncio
async def test_get_total_value_empty_collection(test_collection):
    """Test total value with empty collection"""
    crud = CRUDOperations(test_collection)
    await test_collection.delete_many({})
    
    total_value = await crud.get_total_value()
    
    assert total_value == 0.0


@pytest.mark.asyncio
async def test_get_low_stock_items(test_collection):
    """Test getting low stock items"""
    crud = CRUDOperations(test_collection)
    
    # Create items with different quantities
    await test_collection.insert_many([
        {"name": "Low Stock 1", "price": 10, "quantity": 2, "is_active": True},
        {"name": "Low Stock 2", "price": 20, "quantity": 4, "is_active": True},
        {"name": "High Stock", "price": 30, "quantity": 100, "is_active": True}
    ])
    
    low_stock_items = await crud.get_low_stock_items(threshold=5)
    
    assert isinstance(low_stock_items, list)
    assert len(low_stock_items) >= 2
    for item in low_stock_items:
        assert item["quantity"] < 5