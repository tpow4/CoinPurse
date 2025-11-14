from typing import List
from datetime import datetime, timezone

from sqlalchemy import String
from sqlalchemy.orm import relationship, mapped_column, Mapped

from .base import Base

class Institution(Base):
    """Financial institutions (banks, brokerages)"""
    __tablename__ = 'institutions'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    display_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship: many accounts can belong to one institution
    accounts: Mapped[List["Account"]] = relationship(back_populates="institution")

    def __repr__(self):
        return f"<Institution(id={self.id}, name='{self.name}')>"
