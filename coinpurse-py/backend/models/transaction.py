from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TransactionType

# imports types for FKs only during type checking
if TYPE_CHECKING:
    from .account import Account
    from .category import Category


class Transaction(Base):
    """Individual transactions for checking/credit card accounts"""

    __tablename__ = "transactions"

    transaction_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.account_id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.category_id"))
    transaction_date: Mapped[date]
    posted_date: Mapped[date]
    amount: Mapped[int]
    description: Mapped[str]
    transaction_type: Mapped[TransactionType]
    notes: Mapped[str]
    imported_date: Mapped[datetime | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    modified_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationship: many transactions belong to an account and a category
    account: Mapped["Account"] = relationship(back_populates="transactions")
    category: Mapped["Category"] = relationship(back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.transaction_id}, amount=${self.amount / 100:.2f}, desc='{self.description[:30]}')>"
