from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import AccountType, Base, TaxTreatmentType

# imports types for FKs only during type checking
if TYPE_CHECKING:
    from .balance import AccountBalance
    from .institution import Institution
    from .transaction import Transaction


class Account(Base):
    """Financial accounts (checking, credit cards, investments)"""

    __tablename__ = "accounts"

    account_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    institution_id: Mapped[int] = mapped_column(
        ForeignKey("institutions.institution_id")
    )
    account_name: Mapped[str]
    account_type: Mapped[AccountType]
    tax_treatment: Mapped[TaxTreatmentType]
    last_4_digits: Mapped[str]
    tracks_transactions: Mapped[bool] = mapped_column(default=False)
    tracks_balances: Mapped[bool] = mapped_column(default=False)
    active: Mapped[bool] = mapped_column(default=True)
    display_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    modified_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    institution: Mapped["Institution"] = relationship(back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
    balances: Mapped[list["AccountBalance"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Account(id={self.account_id}, name='{self.account_name}', type={self.account_type.value})>"
