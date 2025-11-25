"""
Repository layer for Category model
Handles all database operations for categories
"""
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from models.category import Category


class CategoryRepository:
    """Repository for Category database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        return self.db.get(Category, category_id)

    def get_all(self, include_inactive: bool = False) -> List[Category]:
        """
        Get all categories

        Args:
            include_inactive: If True, includes inactive categories
        """
        stmt = select(Category)
        if not include_inactive:
            stmt = stmt.where(Category.is_active)
        stmt = stmt.order_by(Category.name)
        return list(self.db.scalars(stmt))

    def get_by_name(self, name: str) -> Optional[Category]:
        """Get category by exact name"""
        stmt = select(Category).where(Category.name == name)
        return self.db.scalar(stmt)

    def search_by_name(self, search_term: str, include_inactive: bool = False) -> List[Category]:
        """
        Search categories by partial name match

        Args:
            search_term: The search term to match
            include_inactive: If True, includes inactive categories
        """
        stmt = select(Category).where(
            Category.name.ilike(f"%{search_term}%")
        )
        if not include_inactive:
            stmt = stmt.where(Category.is_active)
        stmt = stmt.order_by(Category.name)
        return list(self.db.scalars(stmt))

    def create(self, category: Category) -> Category:
        """Create a new category"""
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(self, category: Category) -> Category:
        """Update an existing category"""
        self.db.commit()
        self.db.refresh(category)
        return category

    def soft_delete(self, category: Category) -> Category:
        """Soft delete a category by setting is_active to False"""
        category.is_active = False
        return self.update(category)

    def hard_delete(self, category: Category) -> None:
        """Permanently delete a category (use with caution!)"""
        self.db.delete(category)
        self.db.commit()

    def exists(self, category_id: int) -> bool:
        """Check if a category exists"""
        return self.get_by_id(category_id) is not None

    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if a category name already exists (among active categories)

        Args:
            name: Category name to check
            exclude_id: Optional ID to exclude (for updates)
        """
        stmt = select(Category).where(
            Category.name == name,
            Category.is_active
        )
        if exclude_id:
            stmt = stmt.where(Category.category_id != exclude_id)
        return self.db.scalar(stmt) is not None
