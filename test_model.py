import pytest
from pydantic import ValidationError
from bson import ObjectId
from models import (
    PyObjectId,
    ItemBase,
    ItemCreate,
    ItemUpdate,
    ItemResponse
)


def test_py_object_id_valid():
    """Test PyObjectId with valid ObjectId"""
    valid_id = ObjectId()
    result = PyObjectId.validate(valid_id)
    assert isinstance(result, ObjectId)


def test_py_object_id_valid_string():
    """Test PyObjectId with valid ObjectId string"""
    valid_id_str = str(ObjectId())
    result = PyObjectId.validate(valid_id_str)
    assert isinstance(result, ObjectId)


def test_py_object_id_invalid():
    """Test PyObjectId with invalid ID"""
    with pytest.raises(ValueError, match="Invalid ObjectId"):
        PyObjectId.validate("invalid_id")


def test_item_base_valid():
    """Test creating valid ItemBase"""
    item = ItemBase(
        name="Test Item",
        description="Test description",
        price=99.99,
        quantity=10,
        category="Electronics",
        is_active=True
    )
    
    assert item.name == "Test Item"
    assert item.price == 99.99
    assert item.quantity == 10
    assert item.is_active is True


def test_item_base_minimal():
    """Test ItemBase with minimal required fields"""
    item = ItemBase(
        name="Minimal Item",
        price=50.0,
        quantity=5
    )
    
    assert item.name == "Minimal Item"
    assert item.description is None
    assert item.category is None
    assert item.is_active is True  # Default value


def test_item_base_invalid_name_empty():
    """Test ItemBase with empty name"""
    with pytest.raises(ValidationError) as exc_info:
        ItemBase(
            name="",
            price=99.99,
            quantity=10
        )
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("name",) for error in errors)


def test_item_base_invalid_name_too_long():
    """Test ItemBase with name exceeding max length"""
    with pytest.raises(ValidationError) as exc_info:
        ItemBase(
            name="x" * 101,  # Exceeds max_length of 100
            price=99.99,
            quantity=10
        )
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("name",) for error in errors)


def test_item_base_invalid_price_negative():
    """Test ItemBase with negative price"""
    with pytest.raises(ValidationError) as exc_info:
        ItemBase(
            name="Test Item",
            price=-10.0,
            quantity=5
        )
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("price",) for error in errors)


def test_item_base_invalid_price_zero():
    """Test ItemBase with zero price"""
    with pytest.raises(ValidationError) as exc_info:
        ItemBase(
            name="Test Item",
            price=0.0,
            quantity=5
        )
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("price",) for error in errors)


def test_item_base_invalid_quantity_negative():
    """Test ItemBase with negative quantity"""
    with pytest.raises(ValidationError) as exc_info:
        ItemBase(
            name="Test Item",
            price=99.99,
            quantity=-5
        )
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("quantity",) for error in errors)


def test_item_base_quantity_zero():
    """Test ItemBase with zero quantity (valid)"""
    item = ItemBase(
        name="Test Item",
        price=99.99,
        quantity=0
    )
    
    assert item.quantity == 0


def test_item_base_description_too_long():
    """Test ItemBase with description exceeding max length"""
    with pytest.raises(ValidationError) as exc_info:
        ItemBase(
            name="Test Item",
            description="x" * 501,  # Exceeds max_length of 500
            price=99.99,
            quantity=10
        )
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("description",) for error in errors)


def test_item_create_valid():
    """Test creating valid ItemCreate"""
    item = ItemCreate(
        name="New Item",
        price=149.99,
        quantity=20,
        category="Books"
    )
    
    assert item.name == "New Item"
    assert item.price == 149.99


def test_item_create_inherits_validation():
    """Test that ItemCreate inherits ItemBase validation"""
    with pytest.raises(ValidationError):
        ItemCreate(
            name="",  # Invalid
            price=99.99,
            quantity=10
        )


def test_item_update_all_optional():
    """Test ItemUpdate with all fields optional"""
    item = ItemUpdate()
    
    assert item.name is None
    assert item.price is None
    assert item.quantity is None
    assert item.category is None
    assert item.is_active is None


def test_item_update_partial():
    """Test ItemUpdate with some fields"""
    item = ItemUpdate(
        price=199.99,
        quantity=15
    )
    
    assert item.price == 199.99
    assert item.quantity == 15
    assert item.name is None


def test_item_update_validation():
    """Test ItemUpdate field validation"""
    with pytest.raises(ValidationError) as exc_info:
        ItemUpdate(price=-50.0)
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("price",) for error in errors)


def test_item_response_with_id():
    """Test ItemResponse with ID"""
    item = ItemResponse(
        _id="507f1f77bcf86cd799439011",
        name="Response Item",
        price=299.99,
        quantity=30
    )
    
    assert item.id == "507f1f77bcf86cd799439011"
    assert item.name == "Response Item"


def test_item_response_alias():
    """Test ItemResponse _id alias"""
    data = {
        "_id": "507f1f77bcf86cd799439011",
        "name": "Test",
        "price": 100.0,
        "quantity": 5,
        "is_active": True
    }
    
    item = ItemResponse(**data)
    assert item.id == "507f1f77bcf86cd799439011"


def test_item_base_category_max_length():
    """Test category field max length"""
    with pytest.raises(ValidationError) as exc_info:
        ItemBase(
            name="Test",
            price=99.99,
            quantity=10,
            category="x" * 51  # Exceeds max_length of 50
        )
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("category",) for error in errors)


def test_item_model_dump():
    """Test model serialization"""
    item = ItemCreate(
        name="Test Item",
        description="Test",
        price=99.99,
        quantity=10,
        category="Electronics"
    )
    
    data = item.model_dump()
    
    assert isinstance(data, dict)
    assert data["name"] == "Test Item"
    assert data["price"] == 99.99


def test_item_model_dump_exclude_none():
    """Test model serialization excluding None values"""
    item = ItemUpdate(price=99.99)
    
    data = item.model_dump(exclude_none=True)
    
    assert "price" in data
    assert "name" not in data
    assert "quantity" not in data