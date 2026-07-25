from fastapi import FastAPI
from app.api.products import router as product_router
from app.models.product import Product
from app.database.database import engine, Base

app = FastAPI(title="Product Catalog API")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Welcome to Production Catalog API"}


app.include_router(product_router, prefix="/products", tags=["Products"])
