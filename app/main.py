from fastapi import FastAPI
from app.api.products import router as product_router

app = FastAPI(title="Product Catalog API")


@app.get("/")
def root():
    return {"message": "Welcome to Production Catalog API"}


app.include_router(product_router, prefix="/products", tags=["Products"])
