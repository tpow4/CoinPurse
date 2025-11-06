from typing import Optional
from datetime import datetime, date, timezone

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped

from backend.models.account import Account
from .base import Base

class AccountBalance(Base):
    """Weekly balance snapshots for investment/savings accounts"""
    __tablename__ = 'account_balances'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    balance: Mapped[int]
    balance_date: Mapped[date]
    notes: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    modified_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship: many balances belong to one account
    account: Mapped["Account"] = relationship(back_populates="balances")
    
    # Constraint: one balance per account per date
    __table_args__ = (
        UniqueConstraint('account_id', 'balance_date', name='uq_account_balance_date'),
    )
    
    def __repr__(self):
        return f"<AccountBalance(id={self.id}, account_id={self.account_id}, balance=${self.balance/100:.2f}, date={self.balance_date})>"