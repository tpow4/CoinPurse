from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, FileFormat

# imports types for FKs only during type checking
if TYPE_CHECKING:
    from .account import Account
    from .import_batch import ImportBatch


class ImportTemplate(Base):
    """Import templates for parsing file formats"""

    __tablename__ = "import_templates"

    template_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    template_name: Mapped[str] = mapped_column(String(100))
    file_format: Mapped[FileFormat]
    column_mappings: Mapped[dict[str, Any]] = mapped_column(JSON)
    amount_config: Mapped[dict[str, Any]] = mapped_column(JSON)
    header_row: Mapped[int] = mapped_column(default=1)
    skip_rows: Mapped[int] = mapped_column(default=0)
    date_format: Mapped[str] = mapped_column(String(50), default="%m/%d/%Y")
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    modified_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationship: accounts using this template
    accounts: Mapped[list["Account"]] = relationship(back_populates="import_template")

    # Relationship: one template can have many import batches
    import_batches: Mapped[list["ImportBatch"]] = relationship(back_populates="template")

    def __repr__(self):
        return f"<ImportTemplate(id={self.template_id}, name='{self.template_name}')>"
