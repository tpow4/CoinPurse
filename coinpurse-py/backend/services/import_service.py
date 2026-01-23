"""
Import orchestration service
Coordinates file parsing, duplicate detection, category mapping, and transaction creation
"""

from datetime import UTC, date, datetime
from typing import Any, BinaryIO

from sqlalchemy.orm import Session

from models import (
    Account,
    FileFormat,
    ImportBatch,
    ImportStatus,
    ImportTemplate,
    Transaction,
    TransactionType,
)
from repositories.import_batch_repository import ImportBatchRepository
from repositories.import_template_repository import ImportTemplateRepository
from schemas.import_batch import (
    ImportConfirmResponse,
    ImportPreviewResponse,
    ImportPreviewSummary,
    ParsedTransaction,
)
from services.category_mapper import CategoryMapper
from services.duplicate_detector import DuplicateDetector
from services.parsers import CsvParser, ExcelParser
from services.parsers.base_parser import ParsedRow


class ImportService:
    """Orchestrates the transaction import process"""

    def __init__(self, db: Session):
        self.db = db
        self.template_repo = ImportTemplateRepository(db)
        self.batch_repo = ImportBatchRepository(db)
        self.duplicate_detector = DuplicateDetector(db)
        self.category_mapper = CategoryMapper(db)

    def upload_and_preview(
        self,
        file: BinaryIO,
        file_name: str,
        account_id: int,
        template_id: int,
    ) -> ImportPreviewResponse:
        """
        Upload a file and generate a preview of transactions to import.

        Args:
            file: Binary file object
            file_name: Original filename
            account_id: Target account ID
            template_id: Import template ID to use

        Returns:
            ImportPreviewResponse with import_batch_id, summary, and transactions
        """
        # Load template
        template = self.template_repo.get_by_id(template_id)
        if template is None:
            raise ValueError(f"Template {template_id} not found")

        # Verify account exists
        account = self.db.get(Account, account_id)
        if account is None:
            raise ValueError(f"Account {account_id} not found")

        # Parse file
        parsed_rows = self._parse_file(file, template)

        # Convert to transaction dicts for processing
        transactions = self._rows_to_dicts(parsed_rows)

        # Map categories
        transactions = self.category_mapper.map_categories(
            template.institution_id, transactions
        )

        # Detect duplicates
        transactions = self.duplicate_detector.check_duplicates(account_id, transactions)

        # Calculate summary
        total_rows = len(transactions)
        valid_rows = sum(1 for t in transactions if not t.get("validation_errors"))
        duplicate_count = sum(1 for t in transactions if t.get("is_duplicate"))
        validation_errors = sum(1 for t in transactions if t.get("validation_errors"))

        # Create batch record with PREVIEW status
        batch = ImportBatch(
            account_id=account_id,
            template_id=template_id,
            file_name=file_name,
            file_format=template.file_format,
            total_rows=total_rows,
            duplicate_count=duplicate_count,
            status=ImportStatus.PREVIEW,
            parsed_transactions=transactions,
        )
        batch = self.batch_repo.create(batch)

        # Build response
        summary = ImportPreviewSummary(
            total_rows=total_rows,
            valid_rows=valid_rows,
            duplicate_count=duplicate_count,
            validation_errors=validation_errors,
        )

        parsed_txns = [
            ParsedTransaction(
                row_number=t["row_number"],
                transaction_date=t.get("transaction_date"),
                posted_date=t.get("posted_date"),
                description=t.get("description", ""),
                amount=t.get("amount", 0),
                transaction_type=t.get("transaction_type", "DEBIT"),
                category_name=t.get("bank_category"),
                coinpurse_category_id=t.get("coinpurse_category_id"),
                is_duplicate=t.get("is_duplicate", False),
                validation_errors=t.get("validation_errors", []),
            )
            for t in transactions
        ]

        return ImportPreviewResponse(
            import_batch_id=batch.import_batch_id,
            summary=summary,
            transactions=parsed_txns,
        )

    def confirm_import(
        self,
        import_batch_id: int,
        selected_rows: list[int],
    ) -> ImportConfirmResponse:
        """
        Confirm and execute an import for selected rows.

        Args:
            import_batch_id: The batch ID from preview
            selected_rows: List of row numbers to import

        Returns:
            ImportConfirmResponse with final counts
        """
        # Load batch
        batch = self.batch_repo.get_by_id(import_batch_id)
        if batch is None:
            raise ValueError(f"Batch {import_batch_id} not found")

        if batch.status != ImportStatus.PREVIEW:
            raise ValueError(f"Batch {import_batch_id} is not in PREVIEW status")

        if batch.parsed_transactions is None:
            raise ValueError(f"Batch {import_batch_id} has no parsed transactions")

        # Filter to selected rows
        selected_set = set(selected_rows)
        transactions_to_import = [
            t
            for t in batch.parsed_transactions
            if t["row_number"] in selected_set
            and not t.get("validation_errors")
            and not t.get("is_duplicate")
        ]

        # Calculate counts
        imported_count = 0
        skipped_count = 0
        duplicate_count = 0

        for t in batch.parsed_transactions:
            if t["row_number"] not in selected_set:
                skipped_count += 1
            elif t.get("is_duplicate"):
                duplicate_count += 1
            elif t.get("validation_errors"):
                skipped_count += 1

        # Create transactions
        now = datetime.now(UTC)
        for t in transactions_to_import:
            # Determine transaction type enum
            txn_type = self._map_transaction_type(t.get("transaction_type", "DEBIT"))

            # Parse dates from JSON (stored as ISO strings)
            txn_date = self._parse_date_from_json(t["transaction_date"])
            post_date = self._parse_date_from_json(t.get("posted_date")) or txn_date

            # Skip if no category mapped
            category_id = t.get("coinpurse_category_id")
            if category_id is None:
                skipped_count += 1
                continue

            transaction = Transaction(
                account_id=batch.account_id,
                category_id=t["coinpurse_category_id"],
                transaction_date=txn_date,
                posted_date=post_date,
                amount=t["amount"],
                description=t["description"],
                transaction_type=txn_type,
                notes="",
                imported_date=now,
            )
            self.db.add(transaction)
            imported_count += 1

        # Update batch status
        batch = self.batch_repo.mark_completed(
            batch,
            imported_count=imported_count,
            skipped_count=skipped_count,
            duplicate_count=duplicate_count,
        )

        return ImportConfirmResponse(
            import_batch_id=batch.import_batch_id,
            imported_count=imported_count,
            skipped_count=skipped_count,
            duplicate_count=duplicate_count,
            status=batch.status,
        )

    def _parse_file(self, file: BinaryIO, template: ImportTemplate) -> list[ParsedRow]:
        """Parse a file using the appropriate parser based on template"""
        if template.file_format == FileFormat.CSV:
            parser = CsvParser(
                column_mappings=template.column_mappings,
                amount_config=template.amount_config,
                date_format=template.date_format,
                header_row=template.header_row,
                skip_rows=template.skip_rows,
            )
        elif template.file_format == FileFormat.EXCEL:
            parser = ExcelParser(
                column_mappings=template.column_mappings,
                amount_config=template.amount_config,
                date_format=template.date_format,
                header_row=template.header_row,
                skip_rows=template.skip_rows,
            )
        else:
            raise ValueError(f"Unsupported file format: {template.file_format}")

        return parser.parse(file)

    def _rows_to_dicts(self, rows: list[ParsedRow]) -> list[dict[str, Any]]:
        """Convert ParsedRow objects to dicts for storage"""
        return [
            {
                "row_number": row.row_number,
                "transaction_date": row.transaction_date.isoformat()
                if row.transaction_date
                else None,
                "posted_date": row.posted_date.isoformat() if row.posted_date else None,
                "description": row.description,
                "amount": row.amount,
                "transaction_type": row.transaction_type,
                "bank_category": row.bank_category,
                "validation_errors": row.validation_errors,
            }
            for row in rows
        ]

    def _map_transaction_type(self, type_str: str) -> TransactionType:
        """Map CREDIT/DEBIT string to TransactionType enum"""
        if type_str == "CREDIT":
            return TransactionType.PAYMENT
        else:
            return TransactionType.PURCHASE

    def _parse_date_from_json(self, date_value: str | date | None) -> date | None:
        """Parse a date that may be an ISO string or already a date object"""
        if date_value is None:
            return None
        if isinstance(date_value, date):
            return date_value
        if isinstance(date_value, str):
            return date.fromisoformat(date_value)
        return None
