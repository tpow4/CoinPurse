from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

# imports types for FKs only during type checking
if TYPE_CHECKING:
    from .category_mapping import CategoryMapping
    from .transaction import Transaction


class Category(Base):
    """Transaction categories"""

    __tablename__ = "categories"

    category_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    # Relationship: one category can have many transactions
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")

    # Relationship: one category can have many mappings from different institutions
    category_mappings: Mapped[list["CategoryMapping"]] = relationship(back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.category_id}, name='{self.name}')>"
