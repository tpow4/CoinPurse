"""
Duplicate detection service for transaction imports
"""

from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Transaction


@dataclass(frozen=True)
class TransactionHash:
    """
    Hashable representation of a transaction for duplicate detection.

    Matches on:
    - account_id
    - transaction_date (exact)
    - description (normalized: lowercase, trimmed)
    - transaction_type (DEBIT or CREDIT)
    - amount (exact cents)
    """

    account_id: int
    transaction_date: date
    description: str
    transaction_type: str
    amount: int

    @classmethod
    def from_transaction(cls, txn: Transaction) -> "TransactionHash":
        """Create a hash from an existing Transaction model"""
        return cls(
            account_id=txn.account_id,
            transaction_date=txn.transaction_date,
            description=txn.description.lower().strip(),
            transaction_type="CREDIT" if txn.amount >= 0 else "DEBIT",
            amount=txn.amount,
        )

    @classmethod
    def from_parsed_row(
        cls,
        account_id: int,
        transaction_date: date,
        description: str,
        transaction_type: str,
        amount: int,
    ) -> "TransactionHash":
        """Create a hash from parsed row data"""
        return cls(
            account_id=account_id,
            transaction_date=transaction_date,
            description=description.lower().strip(),
            transaction_type=transaction_type,
            amount=amount,
        )


class DuplicateDetector:
    """Service for detecting duplicate transactions"""

    def __init__(self, db: Session):
        self.db = db
        self._hash_cache: set[TransactionHash] | None = None
        self._cached_account_id: int | None = None

    def build_hash_set(self, account_id: int) -> set[TransactionHash]:
        """
        Build a set of transaction hashes for an account.

        Args:
            account_id: The account to load transactions for

        Returns:
            Set of TransactionHash objects for duplicate checking
        """
        # Return cached set if available for same account
        if self._hash_cache is not None and self._cached_account_id == account_id:
            return self._hash_cache

        stmt = select(Transaction).where(
            Transaction.account_id == account_id,
            Transaction.is_active == True,  # noqa: E712
        )
        transactions = list(self.db.scalars(stmt))

        self._hash_cache = {TransactionHash.from_transaction(txn) for txn in transactions}
        self._cached_account_id = account_id

        return self._hash_cache

    def is_duplicate(
        self,
        account_id: int,
        transaction_date: date,
        description: str,
        transaction_type: str,
        amount: int,
    ) -> bool:
        """
        Check if a transaction would be a duplicate.

        Args:
            account_id: Account ID
            transaction_date: Transaction date
            description: Transaction description
            transaction_type: CREDIT or DEBIT
            amount: Amount in cents

        Returns:
            True if this transaction already exists
        """
        hash_set = self.build_hash_set(account_id)
        txn_hash = TransactionHash.from_parsed_row(
            account_id=account_id,
            transaction_date=transaction_date,
            description=description,
            transaction_type=transaction_type,
            amount=amount,
        )
        return txn_hash in hash_set

    def check_duplicates(
        self,
        account_id: int,
        parsed_transactions: list[dict],
    ) -> list[dict]:
        """
        Check a list of parsed transactions for duplicates.

        Args:
            account_id: Account ID to check against
            parsed_transactions: List of parsed transaction dicts

        Returns:
            Same list with 'is_duplicate' field updated
        """
        hash_set = self.build_hash_set(account_id)

        for txn in parsed_transactions:
            # Skip if no valid transaction date
            txn_date = self._normalize_date(txn.get("transaction_date"))
            if txn_date is None:
                txn["is_duplicate"] = False
                continue

            txn_hash = TransactionHash.from_parsed_row(
                account_id=account_id,
                transaction_date=txn_date,
                description=txn.get("description", ""),
                transaction_type=txn.get("transaction_type", "DEBIT"),
                amount=txn.get("amount", 0),
            )
            txn["is_duplicate"] = txn_hash in hash_set

        return parsed_transactions

    @staticmethod
    def _normalize_date(value: date | datetime | str | None) -> date | None:
        """Normalize parsed dates from JSON-friendly values."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                return None
        return None

    def clear_cache(self):
        """Clear the hash cache"""
        self._hash_cache = None
        self._cached_account_id = None
