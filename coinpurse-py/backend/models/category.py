from datetime import datetime, timezone
from .base import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

class Category(Base):
    """Transaction categories"""
    __tablename__ = 'categories'
    
    category_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship: one category can have many transactions
    transactions = relationship("Transaction", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.category_id}, name='{self.name}')>"