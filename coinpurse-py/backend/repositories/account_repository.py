"""
Repository layer for Account model
Handles all database operations for accounts
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.account import Account


class AccountRepository:
    """Repository for Account database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, account_id: int) -> Account | None:
        """Get account by ID"""
        return self.db.get(Account, account_id)

    def get_all(self, include_inactive: bool = False) -> list[Account]:
        """
        Get all accounts

        Args:
            include_inactive: If True, includes inactive accounts
        """
        stmt = select(Account)
        if not include_inactive:
            stmt = stmt.where(Account.active)
        stmt = stmt.order_by(Account.display_order, Account.account_name)
        return list(self.db.scalars(stmt))

    def get_by_institution(
        self, institution_id: int, include_inactive: bool = False
    ) -> list[Account]:
        """
        Get all accounts for a specific institution

        Args:
            institution_id: The institution ID to filter by
            include_inactive: If True, includes inactive accounts
        """
        stmt = select(Account).where(Account.institution_id == institution_id)
        if not include_inactive:
            stmt = stmt.where(Account.active)
        stmt = stmt.order_by(Account.display_order, Account.account_name)
        return list(self.db.scalars(stmt))

    def get_by_name(self, account_name: str) -> Account | None:
        """Get account by exact name"""
        stmt = select(Account).where(Account.account_name == account_name)
        return self.db.scalar(stmt)

    def search_by_name(self, search_term: str) -> list[Account]:
        """Search accounts by partial name match"""
        stmt = (
            select(Account)
            .where(Account.account_name.ilike(f"%{search_term}%"), Account.active)
            .order_by(Account.display_order, Account.account_name)
        )
        return list(self.db.scalars(stmt))

    def create(self, account: Account) -> Account:
        """Create a new account"""
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def update(self, account: Account) -> Account:
        """Update an existing account"""
        self.db.commit()
        self.db.refresh(account)
        return account

    def soft_delete(self, account: Account) -> Account:
        """Soft delete an account by setting active to False"""
        account.active = False
        return self.update(account)

    def hard_delete(self, account: Account) -> None:
        """Permanently delete an account (use with caution!)"""
        self.db.delete(account)
        self.db.commit()

    def exists(self, account_id: int) -> bool:
        """Check if an account exists"""
        return self.get_by_id(account_id) is not None

    def name_exists(self, account_name: str, exclude_id: int | None = None) -> bool:
        """
        Check if an account name already exists

        Args:
            account_name: Account name to check
            exclude_id: Optional ID to exclude (for updates)
        """
        stmt = select(Account).where(Account.account_name == account_name)
        if exclude_id:
            stmt = stmt.where(Account.account_id != exclude_id)
        return self.db.scalar(stmt) is not None
