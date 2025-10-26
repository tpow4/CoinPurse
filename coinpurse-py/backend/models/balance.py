# models/balance.py
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base

class AccountBalance(Base):
    """Weekly balance snapshots for investment/savings accounts"""
    __tablename__ = 'account_balances'
    
    balance_id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.account_id'), nullable=False)
    balance = Column(Integer, nullable=False)
    balance_date = Column(Date, nullable=False)
    notes = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    modified_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship: many balances belong to one account
    account = relationship("Account", back_populates="balances")
    
    # Constraint: one balance per account per date
    __table_args__ = (
        UniqueConstraint('account_id', 'balance_date', name='uq_account_balance_date'),
    )
    
    def __repr__(self):
        return f"<AccountBalance(id={self.balance_id}, account_id={self.account_id}, balance=${self.balance/100:.2f}, date={self.balance_date})>"