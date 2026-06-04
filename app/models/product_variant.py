from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    size = Column(String, nullable=False)
    color = Column(String, nullable=False)

    buy_price = Column(Float, nullable=False)
    sell_price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)

    sku = Column(String, nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product", back_populates="variants")
    stock_history = relationship("StockHistory", back_populates="variant")
