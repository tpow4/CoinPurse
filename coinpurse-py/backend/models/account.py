# models/account.py
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import Base, AccountType

class Account(Base):
    """Financial accounts (checking, credit cards, investments)"""
    __tablename__ = 'accounts'
    
    account_id = Column(Integer, primary_key=True, autoincrement=True)
    institution_id = Column(Integer, ForeignKey('institutions.institution_id'), nullable=False)
    account_name = Column(String, nullable=False)
    account_type = Column(SQLEnum(AccountType), nullable=False)
    account_subtype = Column(String)  # For "roth_ira", "traditional_ira", etc.
    last_4_digits = Column(String)
    tracks_transactions = Column(Boolean, default=False, nullable=False)
    tracks_balances = Column(Boolean, default=False, nullable=False)
    active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    modified_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    institution = relationship("Institution", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan") 
    balances = relationship("AccountBalance", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Account(id={self.account_id}, name='{self.account_name}', type={self.account_type.value})>"
    