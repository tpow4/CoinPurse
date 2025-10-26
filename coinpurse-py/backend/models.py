from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

class Institution(Base):
    """Financial institutions (banks, brokerages)"""
    __tablename__ = 'institutions'
    
    institution_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    accounts = relationship("Account", back_populates="institution")

    def __repr__(self):
        return f"<Institution(id={self.institution_id}, name='{self.name}')>"
    
class Account(Base):
    """Financial accounts (checking, credit cards, investments)"""
    __tablename__ = 'accounts'

    account_id = Column(Integer, primary_key=True, autoincrement=True)
    institution_id = Column(Integer, ForeignKey('institutions.institution_id'), nullable=False)
    account_name = Column(String, nullable=False)
    account_type = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    modified_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship: many accounts belong to one institution
    institution = relationship("Institution", back_populates="accounts")

    def __repr__(self):
        return f"<Account(id={self.account_id}, name='{self.account_name}')>"
