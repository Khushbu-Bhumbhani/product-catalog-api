from app.schemas.product import ProductCreate, ProductUpdate
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.product import Product


def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_products(db: Session):
    products = db.query(Product).all()
    return products


def get_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=404, detail=f"Product with product id {product_id} not found"
        )
    return product


def update_product(db: Session, product_id: int, product: ProductUpdate):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(
            status_code=404, detail=f"Product with product id {product_id} not found"
        )
    update_data = product.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404,detail=f"Product with product id {product_id} not found")
    db.delete(db_product)
    db.commit()
    return db_product
