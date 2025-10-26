from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Institution(Base):
    """Financial institutions (banks, brokerages)"""
    __tablename__ = 'institutions'
    
    institution_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship: many accounts can belong to one institution
    accounts = relationship("Account", back_populates="institution")

    def __repr__(self):
        return f"<Institution(id={self.institution_id}, name='{self.name}')>"
