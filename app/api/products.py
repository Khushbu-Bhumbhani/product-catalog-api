from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from fastapi.responses import Response
from app.database.database import get_db
from app.crud.product import (
    create_product,
    update_product,
    delete_product,
    get_product,
    get_products,
)
from app.schemas.product import ProductUpdate, ProductCreate, ProductResponse

router = APIRouter()


@router.get("/", response_model=list[ProductResponse])
def get_products_route(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    order: str | None = 'asc',
    db: Session = Depends(get_db),
):
    return get_products(
        db=db,
        page=page,
        limit=limit,
        category=category,
        min_price=min_price,
        max_price=max_price,
        search=search,
        sort_by=sort_by,
        order=order
    )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_route(product_id: int, db: Session = Depends(get_db)):
    return get_product(db=db, product_id=product_id)


@router.post("/", response_model=ProductResponse)
def create_product_route(product: ProductCreate, db: Session = Depends(get_db)):
    return create_product(db=db, product=product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product_route(
    product_id: int, product: ProductUpdate, db: Session = Depends(get_db)
):
    return update_product(db=db, product_id=product_id, product=product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_route(product_id: int, db: Session = Depends(get_db)):
    delete_product(db=db, product_id=product_id)
