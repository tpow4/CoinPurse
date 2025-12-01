"""
Repository layer for Transaction model
Handles all database operations for transactions
"""
from typing import List, Optional
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from models.transaction import Transaction


class TransactionRepository:
    """Repository for Transaction database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID"""
        return self.db.get(Transaction, transaction_id)

    def get_all(self, include_inactive: bool = False) -> List[Transaction]:
        """
        Get all transactions ordered by transaction date descending

        Args:
            include_inactive: If True, includes inactive transactions
        """
        stmt = select(Transaction)
        if not include_inactive:
            stmt = stmt.where(Transaction.is_active)
        stmt = stmt.order_by(Transaction.transaction_date.desc())
        return list(self.db.scalars(stmt))

    def get_by_account(self, account_id: int, include_inactive: bool = False) -> List[Transaction]:
        """
        Get all transactions for a specific account

        Args:
            account_id: The account ID to filter by
            include_inactive: If True, includes inactive transactions
        """
        stmt = select(Transaction).where(
            Transaction.account_id == account_id
        )
        if not include_inactive:
            stmt = stmt.where(Transaction.is_active)
        stmt = stmt.order_by(Transaction.transaction_date.desc())
        return list(self.db.scalars(stmt))

    def get_by_category(self, category_id: int, include_inactive: bool = False) -> List[Transaction]:
        """
        Get all transactions for a specific category

        Args:
            category_id: The category ID to filter by
            include_inactive: If True, includes inactive transactions
        """
        stmt = select(Transaction).where(
            Transaction.category_id == category_id
        )
        if not include_inactive:
            stmt = stmt.where(Transaction.is_active)
        stmt = stmt.order_by(Transaction.transaction_date.desc())
        return list(self.db.scalars(stmt))

    def get_by_date_range(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        account_id: int | None = None,
        category_id: int | None = None,
        include_inactive: bool = False
    ) -> List[Transaction]:
        """
        Get transactions within a date range, optionally filtered by account and/or category

        Args:
            start_date: Optional start date (inclusive)
            end_date: Optional end date (inclusive)
            account_id: Optional account ID to filter by
            category_id: Optional category ID to filter by
            include_inactive: If True, includes inactive transactions
        """
        stmt = select(Transaction)

        if not include_inactive:
            stmt = stmt.where(Transaction.is_active)
        if start_date is not None:
            stmt = stmt.where(Transaction.transaction_date >= start_date)
        if end_date is not None:
            stmt = stmt.where(Transaction.transaction_date <= end_date)
        if account_id is not None:
            stmt = stmt.where(Transaction.account_id == account_id)
        if category_id is not None:
            stmt = stmt.where(Transaction.category_id == category_id)

        stmt = stmt.order_by(Transaction.transaction_date.desc())
        return list(self.db.scalars(stmt))

    def search_by_description(self, search_term: str, include_inactive: bool = False) -> List[Transaction]:
        """
        Search transactions by partial description match

        Args:
            search_term: The search term to match
            include_inactive: If True, includes inactive transactions
        """
        stmt = select(Transaction).where(
            Transaction.description.ilike(f"%{search_term}%")
        )
        if not include_inactive:
            stmt = stmt.where(Transaction.is_active)
        stmt = stmt.order_by(Transaction.transaction_date.desc())
        return list(self.db.scalars(stmt))

    def create(self, transaction: Transaction) -> Transaction:
        """Create a new transaction"""
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def update(self, transaction: Transaction) -> Transaction:
        """Update an existing transaction"""
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def soft_delete(self, transaction: Transaction) -> Transaction:
        """Soft delete a transaction by setting is_active to False"""
        transaction.is_active = False
        return self.update(transaction)

    def hard_delete(self, transaction: Transaction) -> None:
        """Permanently delete a transaction (use with caution!)"""
        self.db.delete(transaction)
        self.db.commit()

    def exists(self, transaction_id: int) -> bool:
        """Check if a transaction exists"""
        return self.get_by_id(transaction_id) is not None
