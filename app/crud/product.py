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


def get_products(
    db: Session,
    page: int,
    limit: int,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    order: str | None = None,
):
    offset = (page - 1) * limit
    sort_columns = {
        "name": Product.name,
        "price": Product.price,
        "quantity": Product.quantity,
    }
    # products = db.query(Product).offset(offset).limit(limit).all()
    query = db.query(Product)
    if category is not None:
        query = query.filter(Product.category.ilike(category))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if search is not None:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if sort_by is not None:
        sort_column = sort_columns.get(sort_by)
        if sort_column is None:
            raise HTTPException(
                status_code=400, detail=f"Invalid sort field: {sort_by}"
            )
        if order is not None:
            if order not in ('asc','desc'):
                raise HTTPException(status_code=400,
                                    detail=f"Invalid order field: {order}")
            if order == 'asc':
                query = query.order_by(sort_column.asc())
            elif order == 'desc':
                query = query.order_by(sort_column.desc())
                        
    products = query.offset(offset).limit(limit).all()
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
        raise HTTPException(
            status_code=404, detail=f"Product with product id {product_id} not found"
        )
    db.delete(db_product)
    db.commit()
