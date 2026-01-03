from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

# imports types for FKs only during type checking
if TYPE_CHECKING:
    from .account import Account


class Institution(Base):
    """Financial institutions (banks, brokerages)"""

    __tablename__ = "institutions"

    institution_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    display_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationship: many accounts can belong to one institution
    accounts: Mapped[list["Account"]] = relationship(back_populates="institution")

    def __repr__(self):
        return f"<Institution(id={self.institution_id}, name='{self.name}')>"
