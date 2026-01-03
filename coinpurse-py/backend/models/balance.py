from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .account import Account


class AccountBalance(Base):
    """Weekly balance snapshots for investment/savings accounts"""

    __tablename__ = "account_balances"

    balance_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.account_id"))
    balance: Mapped[int]
    balance_date: Mapped[date]
    notes: Mapped[str | None]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    modified_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationship: many balances belong to one account
    account: Mapped["Account"] = relationship(back_populates="balances")

    # Constraint: one balance per account per date
    __table_args__ = (
        UniqueConstraint("account_id", "balance_date", name="uq_account_balance_date"),
    )

    def __repr__(self):
        return f"<AccountBalance(id={self.balance_id}, account_id={self.account_id}, balance=${self.balance / 100:.2f}, date={self.balance_date})>"
