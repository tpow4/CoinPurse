from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base

class Category(Base):
    """Transaction categories"""
    __tablename__ = 'categories'
    
    category_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    
    # Relationship: one category can have many transactions
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.category_id}, name='{self.name}')>"