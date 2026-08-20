from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import pytest

from app.database.database import Base, get_db
from app.models.product import Product
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_get_products(db):
    
    product = Product(
        name = "Test Keyboard",
        price = 75.0,
        quantity = 10,
        description = "Test Gaming Keyboard",
        category = "electronics",
    )
    db.add(product)
    db.commit()
   
    
    response = client.get("/products/")
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert len(data) == 1
    assert data[0]['name'] == "Test Keyboard"
    assert data[0]['category'] == "electronics"
    
def test_empty_products(db):
    response = client.get('/products/')
    
    assert response.status_code == 200
    assert response.json() == []
    
def test_create_product():
    product_data = {
        "name": "Gaming Mouse",
        "price": 50.0,
        "quantity": 20,
        "brand": "Logitech",
        "description": "Wireless gaming mouse",
        "category": "electronics",
    }
    
    response = client.post("/products/",json=product_data)
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Gaming Mouse"
    assert data["brand"] == "Logitech"
    assert data["price"] == 50.0
    assert data["quantity"] == 20
   
def test_get_product(db):
    product = Product(
        name="Test Keyboard",
        price=75.0,
        quantity=10,
        description="Test Gaming Keyboard",
        category="electronics",
    ) 
    db.add(product)
    db.commit()
    db.refresh(product)
    
    product_id = product.id
    
    response = client.get(f"/products/{product_id}")
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data["id"] == product_id
    assert data["name"] == "Test Keyboard"
    assert data["category"] == "electronics"
    
def test_get_product_not_found(db):
    resonse = client.get("/products/9999")
    
    assert resonse.status_code == 404
    
    data = resonse.json()
    
    data["detail"] == "Product with product id 9999 not found"  
    
def test_product_update(db):
    product = Product(
        name="Test Keyboard",
        price=75.0,
        quantity=10,
        description="Test Gaming Keyboard",
        category="electronics",
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    product_id = product.id
    update_data = {
        "price": 90.0,
        "quantity": 5
    }
    response = client.put(f"/products/{product_id}", json= update_data)
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data["id"] == product_id
    assert data["price"] == 90.0
    assert data["quantity"] == 5
    assert data["name"] == "Test Keyboard"
    
def test_update_product_not_found(db):
    update_data = {
            "price": 90.0,
            "quantity": 5
        }
    response = client.put(f"/products/9999", json= update_data)
        
    assert response.status_code == 404
        
    data = response.json()
    assert data["detail"] == "Product with product id 9999 not found"  
    
def test_delete_product(db):
    product = Product(
        name="Test Keyboard",
        price=75.0,
        quantity=10,
        description="Test Gaming Keyboard",
        category="electronics",
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    product_id = product.id
    
    response = client.delete(f"/products/{product_id}")
    
    assert response.status_code == 204
    assert response.content == b""
    
def test_delete_product_not_founc(db):
    response = client.delete("/products/9999")
     
    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Product with product id 9999 not found" 