from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class StockHistory(Base):
    __tablename__ = "stock_history"

    id = Column(Integer, primary_key=True, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=False)

    change_type = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)

    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)

    note = Column(String, nullable=True)
    created_by = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    variant = relationship("ProductVariant", back_populates="stock_history")
