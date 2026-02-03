"""
Repository layer for CategoryMapping model
Handles all database operations for category mappings
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.category_mapping import CategoryMapping


class CategoryMappingRepository:
    """Repository for CategoryMapping database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, mapping_id: int) -> CategoryMapping | None:
        """Get category mapping by ID"""
        return self.db.get(CategoryMapping, mapping_id)

    def get_all(self, include_inactive: bool = False) -> list[CategoryMapping]:
        """
        Get all category mappings

        Args:
            include_inactive: If True, includes inactive mappings
        """
        stmt = select(CategoryMapping)
        if not include_inactive:
            stmt = stmt.where(CategoryMapping.is_active)
        stmt = stmt.order_by(CategoryMapping.institution_id, CategoryMapping.bank_category_name)
        return list(self.db.scalars(stmt))

    def get_by_institution(
        self, institution_id: int, include_inactive: bool = False
    ) -> list[CategoryMapping]:
        """
        Get all mappings for a specific institution

        Args:
            institution_id: The institution ID to filter by
            include_inactive: If True, includes inactive mappings
        """
        stmt = select(CategoryMapping).where(CategoryMapping.institution_id == institution_id)
        if not include_inactive:
            stmt = stmt.where(CategoryMapping.is_active)
        stmt = stmt.order_by(CategoryMapping.bank_category_name)
        return list(self.db.scalars(stmt))

    def get_by_bank_category(
        self, institution_id: int, bank_category_name: str
    ) -> CategoryMapping | None:
        """
        Get mapping for a specific bank category name at an institution

        Args:
            institution_id: The institution ID
            bank_category_name: The bank's category name
        """
        stmt = (
            select(CategoryMapping)
            .where(
                CategoryMapping.institution_id == institution_id,
                CategoryMapping.bank_category_name == bank_category_name,
                CategoryMapping.is_active,
            )
            .order_by(CategoryMapping.priority.desc())
        )
        return self.db.scalar(stmt)

    def get_mappings_dict(self, institution_id: int) -> dict[str, list[int]]:
        """
        Get all mappings for an institution as a dictionary

        Args:
            institution_id: The institution ID

        Returns:
            Dict mapping bank_category_name -> list of coinpurse_category_ids
        """
        stmt = (
            select(CategoryMapping)
            .where(
                CategoryMapping.institution_id == institution_id,
                CategoryMapping.is_active,
            )
            .order_by(CategoryMapping.bank_category_name, CategoryMapping.priority.desc())
        )
        mappings = list(self.db.scalars(stmt))

        result: dict[str, list[int]] = {}
        for m in mappings:
            result.setdefault(m.bank_category_name, []).append(m.coinpurse_category_id)
        return result

    def create(self, mapping: CategoryMapping) -> CategoryMapping:
        """Create a new category mapping"""
        self.db.add(mapping)
        self.db.commit()
        self.db.refresh(mapping)
        return mapping

    def update(self, mapping: CategoryMapping) -> CategoryMapping:
        """Update an existing category mapping"""
        self.db.commit()
        self.db.refresh(mapping)
        return mapping

    def soft_delete(self, mapping: CategoryMapping) -> CategoryMapping:
        """Soft delete a mapping by setting is_active to False"""
        mapping.is_active = False
        return self.update(mapping)

    def hard_delete(self, mapping: CategoryMapping) -> None:
        """Permanently delete a mapping (use with caution!)"""
        self.db.delete(mapping)
        self.db.commit()

    def exists(self, mapping_id: int) -> bool:
        """Check if a mapping exists"""
        return self.get_by_id(mapping_id) is not None

    def get_active_by_group(
        self, institution_id: int, bank_category_name: str
    ) -> list[CategoryMapping]:
        """Get all active mappings for a specific institution + bank category name group"""
        stmt = (
            select(CategoryMapping)
            .where(
                CategoryMapping.institution_id == institution_id,
                CategoryMapping.bank_category_name == bank_category_name,
                CategoryMapping.is_active,
            )
            .order_by(CategoryMapping.priority.desc())
        )
        return list(self.db.scalars(stmt))

    def save_group(
        self,
        institution_id: int,
        bank_category_name: str,
        coinpurse_category_ids: list[int],
        old_bank_category_name: str | None = None,
    ) -> list[CategoryMapping]:
        """
        Reconcile a mapping group in a single transaction.

        Args:
            institution_id: The institution ID
            bank_category_name: The (possibly new) bank category name
            coinpurse_category_ids: The desired set of coinpurse category IDs
            old_bank_category_name: If renaming, the previous bank category name
        """
        lookup_name = old_bank_category_name or bank_category_name
        existing = self.get_active_by_group(institution_id, lookup_name)

        existing_cat_ids = {m.coinpurse_category_id for m in existing}
        desired_cat_ids = set(coinpurse_category_ids)

        # Delete mappings no longer in the desired set
        for m in existing:
            if m.coinpurse_category_id not in desired_cat_ids:
                self.db.delete(m)

        # Update retained mappings if name changed
        if old_bank_category_name and old_bank_category_name != bank_category_name:
            for m in existing:
                if m.coinpurse_category_id in desired_cat_ids:
                    m.bank_category_name = bank_category_name

        # Create new mappings
        for cat_id in desired_cat_ids - existing_cat_ids:
            new_mapping = CategoryMapping(
                institution_id=institution_id,
                bank_category_name=bank_category_name,
                coinpurse_category_id=cat_id,
            )
            self.db.add(new_mapping)

        self.db.commit()

        # Return the updated group
        return self.get_active_by_group(institution_id, bank_category_name)

    def soft_delete_group(self, institution_id: int, bank_category_name: str) -> None:
        """Soft-delete all active mappings in a group by setting is_active=False"""
        # Only targets active mappings — inactive ones are already soft-deleted
        for m in self.get_active_by_group(institution_id, bank_category_name):
            m.is_active = False
        self.db.commit()

    def delete_group(self, institution_id: int, bank_category_name: str) -> None:
        """Permanently remove all mappings (active and inactive) in a group"""
        # Queries without is_active filter so previously soft-deleted rows are also removed
        stmt = select(CategoryMapping).where(
            CategoryMapping.institution_id == institution_id,
            CategoryMapping.bank_category_name == bank_category_name,
        )
        for m in self.db.scalars(stmt):
            self.db.delete(m)
        self.db.commit()

    def mapping_exists(
        self,
        institution_id: int,
        bank_category_name: str,
        coinpurse_category_id: int,
        exclude_id: int | None = None,
    ) -> bool:
        """
        Check if an exact mapping triple already exists

        Args:
            institution_id: The institution ID
            bank_category_name: The bank's category name
            coinpurse_category_id: The CoinPurse category ID
            exclude_id: Optional ID to exclude (for updates)
        """
        stmt = select(CategoryMapping).where(
            CategoryMapping.institution_id == institution_id,
            CategoryMapping.bank_category_name == bank_category_name,
            CategoryMapping.coinpurse_category_id == coinpurse_category_id,
            CategoryMapping.is_active,
        )
        if exclude_id:
            stmt = stmt.where(CategoryMapping.mapping_id != exclude_id)
        return self.db.scalar(stmt) is not None
