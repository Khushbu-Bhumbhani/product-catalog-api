from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, description="The Name of the Product")
    description: str | None = Field(
        default=None, max_length=500, description="Product Description"
    )
    price: float = Field(gt=0, description="Price must me higher than zero")
    quantity: int = Field(ge=0, description="Available inventory")
    category: str | None = Field(
        default=None, max_length=50, description="Product Category"
    )

class ProductResponse(ProductCreate):
    id:int