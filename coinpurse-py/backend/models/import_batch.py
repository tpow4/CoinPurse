from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, FileFormat, ImportStatus

# imports types for FKs only during type checking
if TYPE_CHECKING:
    from .account import Account
    from .import_template import ImportTemplate


class ImportBatch(Base):
    """Tracks each import session for audit trail"""

    __tablename__ = "import_batches"

    batch_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.account_id"))
    template_id: Mapped[int | None] = mapped_column(
        ForeignKey("import_templates.template_id"), nullable=True
    )
    file_name: Mapped[str] = mapped_column(String(255))
    file_format: Mapped[FileFormat]
    total_rows: Mapped[int] = mapped_column(default=0)
    imported_count: Mapped[int] = mapped_column(default=0)
    skipped_count: Mapped[int] = mapped_column(default=0)
    duplicate_count: Mapped[int] = mapped_column(default=0)
    status: Mapped[ImportStatus] = mapped_column(default=ImportStatus.PREVIEW)
    parsed_transactions: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    imported_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    modified_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    account: Mapped["Account"] = relationship(back_populates="import_batches")
    template: Mapped["ImportTemplate | None"] = relationship(back_populates="import_batches")

    def __repr__(self):
        return f"<ImportBatch(id={self.batch_id}, file='{self.file_name}', status={self.status.value})>"
