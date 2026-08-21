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
    poolclass=StaticPool,
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
        name="Test Keyboard",
        price=75.0,
        quantity=10,
        description="Test Gaming Keyboard",
        category="electronics",
    )
    db.add(product)
    db.commit()

    response = client.get("/products/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Test Keyboard"
    assert data[0]["category"] == "electronics"


def test_empty_products(db):
    response = client.get("/products/")

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

    response = client.post("/products/", json=product_data)

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
    update_data = {"price": 90.0, "quantity": 5}
    response = client.put(f"/products/{product_id}", json=update_data)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["price"] == 90.0
    assert data["quantity"] == 5
    assert data["name"] == "Test Keyboard"


def test_update_product_not_found(db):
    update_data = {"price": 90.0, "quantity": 5}
    response = client.put(f"/products/9999", json=update_data)

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


def test_delete_product_not_found(db):
    response = client.delete("/products/9999")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Product with product id 9999 not found"


def test_filter_by_category(db):
    products = [
        Product(
            name="Keyboard",
            price=75.0,
            quantity=10,
            category="electronics",
        ),
        Product(
            name="Mouse",
            price=30.0,
            quantity=20,
            category="electronics",
        ),
        Product(
            name="Notebook",
            price=10.0,
            quantity=50,
            category="stationery",
        ),
    ]
    db.add_all(products)
    db.commit()
    
    response = client.get("/products/?category=electronics")
    
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert data[0]["category"] == 'electronics'
    assert data[1]["category"] == 'electronics'

def test_filter_by_price_range(db):
    products = [
         Product(
            name="Keyboard",
            price=75.0,
            quantity=10,
            category="electronics",
        ),
        Product(
            name="Mouse",
            price=30.0,
            quantity=20,
            category="electronics",
        ),
        Product(
            name="Monitor",
            price=150.0,
            quantity=5,
            category="electronics",
        ),
    ]
    
    db.add_all(products)
    db.commit()
    
    response = client.get("/products/?min_price=50&max_price=100")
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert len(data) == 1
    assert data[0]["name"] == "Keyboard"
    assert data[0]["price"] == 75.0
    
def test_search_product(db):
    products = [
        Product(
            name="Gaming Keyboard",
            price=75.0,
            quantity=10,
            category="electronics",
        ),
        Product(
            name="Wireless Mouse",
            price=30.0,
            quantity=20,
            category="electronics",
        ),
        Product(
            name="Keyboard Stand",
            price=25.0,
            quantity=15,
            category="accessories",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = client.get("/products/?search=keyboard")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Gaming Keyboard"
    assert data[1]["name"] == "Keyboard Stand"
    
def test_sort_product_by_price_asc(db):
    products = [
        Product(
            name="Monitor",
            price=150.0,
            quantity=5,
            category="electronics",
        ),
        Product(
            name="Keyboard",
            price=75.0,
            quantity=10,
            category="electronics",
        ),
        Product(
            name="Mouse",
            price=30.0,
            quantity=20,
            category="electronics",
        ),
    ]

    db.add_all(products)
    db.commit()
    
    response = client.get("/products/?sort_by=price&order=asc")
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data[0]["price"] == 30.0
    assert data[1]["price"] == 75.0
    assert data[2]["price"] == 150.0
    
def test_invalid_sort_field(db):
    
    response = client.get("/products/?sort_by=invalid")
    
    assert response.status_code == 400
    
    data = response.json()
    
    assert data["detail"] == "Invalid sort field: invalid"

def test_invalid_sort_order(db):
    
    response = client.get("/products/?sort_by=price&order=random")
        
    assert response.status_code == 400
        
    data = response.json()
        
    assert data["detail"] == "Invalid order field: random"
    
def test_sort_products_by_price_desc(db):
    products = [
            Product(
                name="Monitor",
                price=150.0,
                quantity=5,
                category="electronics",
            ),
            Product(
                name="Keyboard",
                price=75.0,
                quantity=10,
                category="electronics",
            ),
            Product(
                name="Mouse",
                price=30.0,
                quantity=20,
                category="electronics",
            ),
        ]
    
    db.add_all(products)
    db.commit()
    
    response = client.get("/products/?sort_by=price&order=desc")
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data[0]["price"] == 150.0
    assert data[1]["price"] == 75.0
    assert data[2]["price"] == 30.0
    
def test_sort_products_default_order(db):
    products = [
        Product(
            name="Monitor",
            price=150.0,
            quantity=5,
            category="electronics",
        ),
        Product(
            name="Keyboard",
            price=75.0,
            quantity=10,
            category="electronics",
        ),
        Product(
            name="Mouse",
            price=30.0,
            quantity=20,
            category="electronics",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = client.get("/products/?sort_by=price")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3
    assert data[0]["price"] == 30.0
    assert data[1]["price"] == 75.0
    assert data[2]["price"] == 150.0
    
def test_pagination(db):
    products = [
        Product(name="Product 1", price=10.0, quantity=1),
        Product(name="Product 2", price=20.0, quantity=1),
        Product(name="Product 3", price=30.0, quantity=1),
        Product(name="Product 4", price=40.0, quantity=1),
        Product(name="Product 5", price=50.0, quantity=1),
    ]

    db.add_all(products)
    db.commit()
    
    response = client.get("/products/?page=2&limit=2")
    
    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Product 3"
    assert data[1]["name"] == "Product 4"
    
def test_invalid_page():
    response = client.get("/products/?page=0")
        
    assert response.status_code == 422
    
def test_invalid_limit():
    response = client.get("/products/?limit=101")
    
    assert response.status_code == 422
    
def test_invalid_limit_zero():
    response = client.get("/products/?limit=0")
        
    assert response.status_code == 422
    
def test_combined_filters(db):
    products = [
        Product(
            name="Gaming Keyboard",
            price=75.0,
            quantity=10,
            category="electronics",
        ),
        Product(
            name="Gaming Mouse",
            price=50.0,
            quantity=20,
            category="electronics",
        ),
        Product(
            name="Office Chair",
            price=100.0,
            quantity=5,
            category="furniture",
        ),
        Product(
            name="Laptop",
            price=500.0,
            quantity=3,
            category="electronics",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = client.get(
        "/products/?category=electronics&min_price=60&max_price=100"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Gaming Keyboard"
    assert data[0]["price"] == 75.0
    assert data[0]["category"] == "electronics"
    
    
    