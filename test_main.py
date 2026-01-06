import pytest
from httpx import AsyncClient
from fastapi import status
from main import app


@pytest.mark.asyncio
async def test_root():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to FastAPI MongoDB CRUD API"}


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_create_item():
    """Test creating a new item"""
    item_data = {
        "name": "Test Laptop",
        "description": "A test laptop",
        "price": 999.99,
        "quantity": 5,
        "category": "Electronics",
        "is_active": True
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/items/", json=item_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["price"] == item_data["price"]
    assert "_id" in data


@pytest.mark.asyncio
async def test_create_item_invalid_data():
    """Test creating item with invalid data"""
    item_data = {
        "name": "",  # Invalid: empty name
        "price": -100,  # Invalid: negative price
        "quantity": -5  # Invalid: negative quantity
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/items/", json=item_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_all_items():
    """Test getting all items"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/items/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_all_items_with_pagination():
    """Test getting items with pagination"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/items/?skip=0&limit=5")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5


@pytest.mark.asyncio
async def test_get_item_by_id(test_item_id):
    """Test getting a specific item by ID"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/items/{test_item_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["_id"] == test_item_id


@pytest.mark.asyncio
async def test_get_item_by_invalid_id():
    """Test getting item with invalid ID"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/items/invalid_id_format")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_item_not_found():
    """Test getting non-existent item"""
    fake_id = "507f1f77bcf86cd799439011"
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/items/{fake_id}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_item(test_item_id):
    """Test updating an item"""
    update_data = {
        "price": 899.99,
        "quantity": 3
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(f"/items/{test_item_id}", json=update_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["price"] == update_data["price"]
    assert data["quantity"] == update_data["quantity"]


@pytest.mark.asyncio
async def test_update_item_invalid_data(test_item_id):
    """Test updating item with invalid data"""
    update_data = {
        "price": -500  # Invalid: negative price
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(f"/items/{test_item_id}", json=update_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_update_nonexistent_item():
    """Test updating non-existent item"""
    fake_id = "507f1f77bcf86cd799439011"
    update_data = {"price": 999.99}
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(f"/items/{fake_id}", json=update_data)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_search_items():
    """Test searching items"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/items/search/?q=laptop")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_search_items_no_query():
    """Test search without query parameter"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/items/search/")
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_items_by_category():
    """Test getting items by category"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/items/category/Electronics")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_active_items():
    """Test getting active items only"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/items/active/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_low_stock_items():
    """Test getting low stock items"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/items/low-stock/?threshold=10")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_deactivate_item(test_item_id):
    """Test soft delete (deactivate) an item"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.patch(f"/items/{test_item_id}/deactivate")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_get_total_inventory_value():
    """Test getting total inventory value"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/stats/total-value")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_inventory_value" in data
    assert "currency" in data
    assert isinstance(data["total_inventory_value"], (int, float))


@pytest.mark.asyncio
async def test_bulk_update_prices():
    """Test bulk price update"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/items/bulk/update-prices?multiplier=1.1")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "modified_count" in data
    assert "multiplier" in data


@pytest.mark.asyncio
async def test_delete_item(test_item_id):
    """Test deleting an item"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(f"/items/{test_item_id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_nonexistent_item():
    """Test deleting non-existent item"""
    fake_id = "507f1f77bcf86cd799439011"
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(f"/items/{fake_id}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND