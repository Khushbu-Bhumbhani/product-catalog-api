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
    

        