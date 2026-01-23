"""
Repository layer for ImportBatch model
Handles all database operations for import batches
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.base import ImportStatus
from models.import_batch import ImportBatch


class ImportBatchRepository:
    """Repository for ImportBatch database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, import_batch_id: int) -> ImportBatch | None:
        """Get import batch by ID"""
        return self.db.get(ImportBatch, import_batch_id)

    def get_all(self, limit: int = 100) -> list[ImportBatch]:
        """
        Get all import batches, most recent first

        Args:
            limit: Maximum number of batches to return
        """
        stmt = select(ImportBatch).order_by(ImportBatch.created_at.desc()).limit(limit)
        return list(self.db.scalars(stmt))

    def get_by_account(self, account_id: int, limit: int = 100) -> list[ImportBatch]:
        """
        Get all batches for a specific account

        Args:
            account_id: The account ID to filter by
            limit: Maximum number of batches to return
        """
        stmt = (
            select(ImportBatch)
            .where(ImportBatch.account_id == account_id)
            .order_by(ImportBatch.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def get_by_status(self, status: ImportStatus, limit: int = 100) -> list[ImportBatch]:
        """
        Get all batches with a specific status

        Args:
            status: The status to filter by
            limit: Maximum number of batches to return
        """
        stmt = (
            select(ImportBatch)
            .where(ImportBatch.status == status)
            .order_by(ImportBatch.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def get_pending_previews(self, limit: int = 100) -> list[ImportBatch]:
        """Get all batches in PREVIEW status (not yet confirmed)"""
        return self.get_by_status(ImportStatus.PREVIEW, limit)

    def create(self, batch: ImportBatch) -> ImportBatch:
        """Create a new import batch"""
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def update(self, batch: ImportBatch) -> ImportBatch:
        """Update an existing import batch"""
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def mark_completed(
        self, batch: ImportBatch, imported_count: int, skipped_count: int, duplicate_count: int
    ) -> ImportBatch:
        """
        Mark a batch as completed with final counts

        Args:
            batch: The batch to update
            imported_count: Number of transactions successfully imported
            skipped_count: Number of transactions skipped
            duplicate_count: Number of duplicate transactions found
        """
        batch.status = ImportStatus.COMPLETED
        batch.imported_count = imported_count
        batch.skipped_count = skipped_count
        batch.duplicate_count = duplicate_count
        batch.imported_at = datetime.now(UTC)
        batch.parsed_transactions = None  # Clear parsed data after import
        return self.update(batch)

    def mark_failed(self, batch: ImportBatch) -> ImportBatch:
        """Mark a batch as failed"""
        batch.status = ImportStatus.FAILED
        batch.parsed_transactions = None  # Clear parsed data on failure
        return self.update(batch)

    def delete(self, batch: ImportBatch) -> None:
        """Permanently delete a batch"""
        self.db.delete(batch)
        self.db.commit()

    def exists(self, import_batch_id: int) -> bool:
        """Check if a batch exists"""
        return self.get_by_id(import_batch_id) is not None

    def cleanup_old_previews(self, hours: int = 24) -> int:
        """
        Delete preview batches older than specified hours

        Args:
            hours: Delete previews older than this many hours

        Returns:
            Number of batches deleted
        """
        cutoff = datetime.now(UTC) - timedelta(hours=hours)
        stmt = select(ImportBatch).where(
            ImportBatch.status == ImportStatus.PREVIEW, ImportBatch.created_at < cutoff
        )
        old_batches = list(self.db.scalars(stmt))
        count = len(old_batches)
        for batch in old_batches:
            self.db.delete(batch)
        self.db.commit()
        return count
