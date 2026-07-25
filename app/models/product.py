from datetime import datetime
from sqlalchemy import Float, String, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)
    quantity: Mapped[int] = mapped_column()
    description: Mapped[str | None] = mapped_column(
        String(500), nullable=True, default=None
    )
    category: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
