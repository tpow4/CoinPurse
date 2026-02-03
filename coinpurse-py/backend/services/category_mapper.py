"""
Category mapping service for transaction imports
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Category, CategoryMapping


class CategoryMapper:
    """Service for mapping bank categories to CoinPurse categories"""

    def __init__(self, db: Session):
        self.db = db
        self._mapping_cache: dict[int, dict[str, list[int]]] | None = None
        self._uncategorized_id: int | None = None

    def get_uncategorized_category_id(self) -> int:
        """
        Get the ID of the 'Uncategorized' category.

        Returns:
            Category ID for Uncategorized

        Raises:
            ValueError if Uncategorized category doesn't exist
        """
        if self._uncategorized_id is not None:
            return self._uncategorized_id

        stmt = select(Category).where(
            Category.name == "Uncategorized",
            Category.is_active == True,  # noqa: E712
        )
        category = self.db.scalar(stmt)

        if category is None:
            raise ValueError(
                "Uncategorized category not found. Please run database seeding."
            )

        self._uncategorized_id = category.category_id
        return self._uncategorized_id

    def get_mappings_for_institution(self, institution_id: int) -> dict[str, list[int]]:
        """
        Get all category mappings for an institution.

        Args:
            institution_id: The institution ID

        Returns:
            Dict mapping bank_category_name -> list of coinpurse_category_ids (ordered by priority desc)
        """
        if self._mapping_cache is None:
            self._mapping_cache = {}

        if institution_id in self._mapping_cache:
            return self._mapping_cache[institution_id]

        stmt = (
            select(CategoryMapping)
            .where(
                CategoryMapping.institution_id == institution_id,
                CategoryMapping.is_active == True,  # noqa: E712
            )
            .order_by(CategoryMapping.priority.desc())
        )
        mappings = list(self.db.scalars(stmt))

        # Build dict - each bank category maps to a list of coinpurse category IDs
        mapping_dict: dict[str, list[int]] = {}
        for m in mappings:
            normalized_name = m.bank_category_name.lower().strip()
            mapping_dict.setdefault(normalized_name, []).append(m.coinpurse_category_id)

        self._mapping_cache[institution_id] = mapping_dict
        return mapping_dict

    def map_category(
        self,
        institution_id: int,
        bank_category_name: str | None,
    ) -> int:
        """
        Map a bank category name to a CoinPurse category ID.
        Returns the highest-priority candidate, or Uncategorized if no mapping.

        Args:
            institution_id: The institution ID
            bank_category_name: The bank's category name (can be None)

        Returns:
            CoinPurse category ID (defaults to Uncategorized if no mapping)
        """
        if not bank_category_name:
            return self.get_uncategorized_category_id()

        mappings = self.get_mappings_for_institution(institution_id)
        normalized_name = bank_category_name.lower().strip()

        candidates = mappings.get(normalized_name, [])
        if candidates:
            return candidates[0]

        return self.get_uncategorized_category_id()

    def map_categories(
        self,
        institution_id: int,
        parsed_transactions: list[dict],
    ) -> list[dict]:
        """
        Map categories for a list of parsed transactions.

        Args:
            institution_id: The institution ID
            parsed_transactions: List of parsed transaction dicts

        Returns:
            Same list with 'coinpurse_category_id' and 'candidate_category_ids' fields added
        """
        uncategorized_id = self.get_uncategorized_category_id()
        mappings = self.get_mappings_for_institution(institution_id)

        for txn in parsed_transactions:
            bank_category = txn.get("bank_category") or txn.get("category_name")

            if not bank_category:
                txn["coinpurse_category_id"] = uncategorized_id
                txn["candidate_category_ids"] = []
                continue

            normalized_name = bank_category.lower().strip()
            candidates = mappings.get(normalized_name, [])
            candidate_ids = list(candidates)
            txn["candidate_category_ids"] = candidate_ids
            txn["coinpurse_category_id"] = (
                candidate_ids[0] if candidate_ids else uncategorized_id
            )

        return parsed_transactions

    def clear_cache(self):
        """Clear the mapping cache"""
        self._mapping_cache = None
        self._uncategorized_id = None
