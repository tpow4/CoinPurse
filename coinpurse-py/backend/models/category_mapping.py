from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

# imports types for FKs only during type checking
if TYPE_CHECKING:
    from .category import Category
    from .institution import Institution


class CategoryMapping(Base):
    """Maps institution-specific category names to CoinPurse categories"""

    __tablename__ = "category_mappings"

    __table_args__ = (
        UniqueConstraint("institution_id", "bank_category_name", name="uq_institution_bank_category"),
    )

    mapping_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.institution_id"))
    bank_category_name: Mapped[str] = mapped_column(String(100))
    coinpurse_category_id: Mapped[int] = mapped_column(ForeignKey("categories.category_id"))
    priority: Mapped[int] = mapped_column(default=1)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    modified_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    institution: Mapped["Institution"] = relationship(back_populates="category_mappings")
    category: Mapped["Category"] = relationship(back_populates="category_mappings")

    def __repr__(self):
        return f"<CategoryMapping(id={self.mapping_id}, bank='{self.bank_category_name}')>"
