from datetime import datetime, date, timezone

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base, TransactionType

class Transaction(Base):
    """Individual transactions for checking/credit card accounts"""
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.category_id'))
    transaction_date: Mapped[date]
    posted_date: Mapped[date]
    amount: Mapped[int]
    description: Mapped[str]
    transaction_type: Mapped[TransactionType]
    notes: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    modified_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship: many transactions belong to an account and a category
    account: Mapped["Account"] = relationship(back_populates="transactions")
    category: Mapped["Category"] = relationship(back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, amount=${self.amount/100:.2f}, desc='{self.description[:30]}')>"