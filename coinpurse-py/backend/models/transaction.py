# models/transaction.py
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base, TransactionType

class Transaction(Base):
    """Individual transactions for checking/credit card accounts"""
    __tablename__ = 'transactions'
    
    transaction_id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.account_id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.category_id'), nullable=False)
    transaction_date = Column(Date, nullable=False)
    posted_date = Column(Date, nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    notes = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    modified_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship: many transactions belong to an account and a category
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.transaction_id}, amount=${self.amount/100:.2f}, desc='{self.description[:30]}')>"