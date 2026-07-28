from pydantic import BaseModel, Field, ConfigDict


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


class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None, min_length=1, description="The Name of the Product"
    )
    description: str | None = Field(
        default=None, max_length=500, description="Product Description"
    )
    price: float | None = Field(
        default=None, gt=0, description="Price must me higher than zero"
    )
    quantity: int | None = Field(default=None, ge=0, description="Available inventory")
    category: str | None = Field(
        default=None, max_length=50, description="Product Category"
    )


class ProductResponse(ProductCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
