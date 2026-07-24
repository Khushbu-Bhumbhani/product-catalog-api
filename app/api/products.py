from fastapi import APIRouter, HTTPException, status
from app.schemas.product import ProductCreate, ProductResponse
from fastapi.responses import Response

router = APIRouter()

products = []


@router.get("/", response_model=list[ProductResponse])
def get_product():
    return {"products": products}


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    raise HTTPException(
        status_code=404, detail=f"Product with product id {product_id} not found"
    )


@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate):
    product_dict = product.model_dump()
    product_dict["id"] = len(products) + 1
    products.append(product_dict)
    return {"message": "Product Created", "product": products}


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductCreate):
    for p in products:
        if p["id"] == product_id:
            update_product = product.model_dump()
            update_product["id"] = product_id
            p.update(update_product)
            return p
    raise HTTPException(
        status_code=404, detail=f"Product with product id {product_id} not found"
    )

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def detele_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            products.remove(p)
            return Response()
        
    raise HTTPException(status_code=404,detail=f"product with product id {product_id} not found")