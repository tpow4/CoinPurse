"""
Repository layer for AccountBalance model
Handles all database operations for account balances
"""
from typing import List, Optional
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from models.balance import AccountBalance


class BalanceRepository:
    """Repository for AccountBalance database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, balance_id: int) -> Optional[AccountBalance]:
        """Get balance by ID"""
        return self.db.get(AccountBalance, balance_id)

    def get_all(self, include_inactive: bool = False) -> List[AccountBalance]:
        """
        Get all balances ordered by date descending

        Args:
            include_inactive: If True, includes inactive balances
        """
        stmt = select(AccountBalance)
        if not include_inactive:
            stmt = stmt.where(AccountBalance.is_active)
        stmt = stmt.order_by(AccountBalance.balance_date.desc())
        return list(self.db.scalars(stmt))

    def get_by_account(self, account_id: int, include_inactive: bool = False) -> List[AccountBalance]:
        """
        Get all balances for a specific account

        Args:
            account_id: The account ID to filter by
            include_inactive: If True, includes inactive balances
        """
        stmt = select(AccountBalance).where(
            AccountBalance.account_id == account_id
        )
        if not include_inactive:
            stmt = stmt.where(AccountBalance.is_active)
        stmt = stmt.order_by(AccountBalance.balance_date.desc())
        return list(self.db.scalars(stmt))

    def get_by_account_and_date(self, account_id: int, balance_date: date) -> Optional[AccountBalance]:
        """
        Get balance for a specific account on a specific date

        Args:
            account_id: The account ID
            balance_date: The date to look up
        """
        stmt = select(AccountBalance).where(
            and_(
                AccountBalance.account_id == account_id,
                AccountBalance.balance_date == balance_date
            )
        )
        return self.db.scalar(stmt)

    def get_by_date_range(
        self,
        account_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        include_inactive: bool = False
    ) -> List[AccountBalance]:
        """
        Get balances within a date range, optionally filtered by account

        Args:
            account_id: Optional account ID to filter by
            start_date: Optional start date (inclusive)
            end_date: Optional end date (inclusive)
            include_inactive: If True, includes inactive balances
        """
        stmt = select(AccountBalance)

        if not include_inactive:
            stmt = stmt.where(AccountBalance.is_active)
        if account_id is not None:
            stmt = stmt.where(AccountBalance.account_id == account_id)
        if start_date is not None:
            stmt = stmt.where(AccountBalance.balance_date >= start_date)
        if end_date is not None:
            stmt = stmt.where(AccountBalance.balance_date <= end_date)

        stmt = stmt.order_by(AccountBalance.balance_date.desc())
        return list(self.db.scalars(stmt))

    def get_latest_by_account(self, account_id: int, include_inactive: bool = False) -> Optional[AccountBalance]:
        """
        Get the most recent balance for a specific account

        Args:
            account_id: The account ID
            include_inactive: If True, includes inactive balances
        """
        stmt = select(AccountBalance).where(
            AccountBalance.account_id == account_id
        )
        if not include_inactive:
            stmt = stmt.where(AccountBalance.is_active)
        stmt = stmt.order_by(AccountBalance.balance_date.desc()).limit(1)
        return self.db.scalar(stmt)

    def create(self, balance: AccountBalance) -> AccountBalance:
        """Create a new balance"""
        self.db.add(balance)
        self.db.commit()
        self.db.refresh(balance)
        return balance

    def update(self, balance: AccountBalance) -> AccountBalance:
        """Update an existing balance"""
        self.db.commit()
        self.db.refresh(balance)
        return balance

    def soft_delete(self, balance: AccountBalance) -> AccountBalance:
        """Soft delete a balance by setting is_active to False"""
        balance.is_active = False
        return self.update(balance)

    def hard_delete(self, balance: AccountBalance) -> None:
        """Permanently delete a balance (use with caution!)"""
        self.db.delete(balance)
        self.db.commit()

    def exists(self, balance_id: int) -> bool:
        """Check if a balance exists"""
        return self.get_by_id(balance_id) is not None

    def exists_for_account_and_date(self, account_id: int, balance_date: date, exclude_id: Optional[int] = None) -> bool:
        """
        Check if an active balance already exists for an account on a specific date

        Args:
            account_id: Account ID to check
            balance_date: Date to check
            exclude_id: Optional balance ID to exclude (for updates)
        """
        stmt = select(AccountBalance).where(
            and_(
                AccountBalance.account_id == account_id,
                AccountBalance.balance_date == balance_date,
                AccountBalance.is_active
            )
        )
        if exclude_id:
            stmt = stmt.where(AccountBalance.balance_id != exclude_id)
        return self.db.scalar(stmt) is not None
