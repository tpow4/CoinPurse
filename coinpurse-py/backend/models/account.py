from typing import List
from datetime import datetime, timezone

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped

from .base import Base, AccountType

class Account(Base):
    """Financial accounts (checking, credit cards, investments)"""
    __tablename__ = 'accounts'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey('institutions.id'))
    account_name: Mapped[str]
    account_type: Mapped[AccountType]
    account_subtype: Mapped[str]
    last_4_digits: Mapped[str]
    tracks_transactions: Mapped[bool] = mapped_column(default=False)
    tracks_balances: Mapped[bool] = mapped_column(default=False)
    active: Mapped[bool] = mapped_column(default=True)
    display_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    modified_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    institution: Mapped["Institution"] = relationship(back_populates="accounts")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="account", cascade="all, delete-orphan") 
    balances: Mapped[List["AccountBalance"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.account_name}', type={self.account_type.value})>"
    