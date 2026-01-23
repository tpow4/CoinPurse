"""
Unit tests for category mapping service
"""

import pytest

from models import Category, CategoryMapping, Institution
from services import CategoryMapper


class TestCategoryMapper:
    """Tests for CategoryMapper service"""

    @pytest.fixture
    def setup_data(self, db_session):
        """Set up test data"""
        # Create categories
        uncategorized = Category(name="Uncategorized")
        restaurants = Category(name="Restaurants")
        shopping = Category(name="Shopping")
        entertainment = Category(name="Entertainment")
        db_session.add_all([uncategorized, restaurants, shopping, entertainment])
        db_session.commit()

        # Create institutions
        chase = Institution(name="Chase")
        discover = Institution(name="Discover")
        db_session.add_all([chase, discover])
        db_session.commit()

        # Create mappings for Chase
        mapping1 = CategoryMapping(
            institution_id=chase.institution_id,
            bank_category_name="Food & Drink",
            coinpurse_category_id=restaurants.category_id,
        )
        mapping2 = CategoryMapping(
            institution_id=chase.institution_id,
            bank_category_name="Shopping",
            coinpurse_category_id=shopping.category_id,
        )
        mapping3 = CategoryMapping(
            institution_id=chase.institution_id,
            bank_category_name="Entertainment",
            coinpurse_category_id=entertainment.category_id,
        )

        # Create mappings for Discover (different names)
        mapping4 = CategoryMapping(
            institution_id=discover.institution_id,
            bank_category_name="Restaurants",
            coinpurse_category_id=restaurants.category_id,
        )
        mapping5 = CategoryMapping(
            institution_id=discover.institution_id,
            bank_category_name="Merchandise",
            coinpurse_category_id=shopping.category_id,
        )

        db_session.add_all([mapping1, mapping2, mapping3, mapping4, mapping5])
        db_session.commit()

        return {
            "uncategorized": uncategorized,
            "restaurants": restaurants,
            "shopping": shopping,
            "entertainment": entertainment,
            "chase": chase,
            "discover": discover,
        }

    def test_get_uncategorized_category_id(self, db_session, setup_data):
        """Should return the Uncategorized category ID"""
        mapper = CategoryMapper(db_session)

        result = mapper.get_uncategorized_category_id()

        assert result == setup_data["uncategorized"].category_id

    def test_get_uncategorized_not_found(self, db_session):
        """Should raise error if Uncategorized category doesn't exist"""
        mapper = CategoryMapper(db_session)

        with pytest.raises(ValueError, match="Uncategorized category not found"):
            mapper.get_uncategorized_category_id()

    def test_map_category_found(self, db_session, setup_data):
        """Should map bank category to CoinPurse category"""
        mapper = CategoryMapper(db_session)
        chase = setup_data["chase"]
        restaurants = setup_data["restaurants"]

        result = mapper.map_category(chase.institution_id, "Food & Drink")

        assert result == restaurants.category_id

    def test_map_category_case_insensitive(self, db_session, setup_data):
        """Should match category names case-insensitively"""
        mapper = CategoryMapper(db_session)
        chase = setup_data["chase"]
        restaurants = setup_data["restaurants"]

        result = mapper.map_category(chase.institution_id, "FOOD & DRINK")

        assert result == restaurants.category_id

    def test_map_category_trims_whitespace(self, db_session, setup_data):
        """Should trim whitespace from category names"""
        mapper = CategoryMapper(db_session)
        chase = setup_data["chase"]
        restaurants = setup_data["restaurants"]

        result = mapper.map_category(chase.institution_id, "  Food & Drink  ")

        assert result == restaurants.category_id

    def test_map_category_not_found(self, db_session, setup_data):
        """Should return Uncategorized for unknown category"""
        mapper = CategoryMapper(db_session)
        chase = setup_data["chase"]
        uncategorized = setup_data["uncategorized"]

        result = mapper.map_category(chase.institution_id, "Unknown Category")

        assert result == uncategorized.category_id

    def test_map_category_none_input(self, db_session, setup_data):
        """Should return Uncategorized for None category"""
        mapper = CategoryMapper(db_session)
        chase = setup_data["chase"]
        uncategorized = setup_data["uncategorized"]

        result = mapper.map_category(chase.institution_id, None)

        assert result == uncategorized.category_id

    def test_map_category_empty_string(self, db_session, setup_data):
        """Should return Uncategorized for empty string"""
        mapper = CategoryMapper(db_session)
        chase = setup_data["chase"]
        uncategorized = setup_data["uncategorized"]

        result = mapper.map_category(chase.institution_id, "")

        assert result == uncategorized.category_id

    def test_map_category_different_institutions(self, db_session, setup_data):
        """Different institutions should have different mappings"""
        mapper = CategoryMapper(db_session)
        chase = setup_data["chase"]
        discover = setup_data["discover"]
        restaurants = setup_data["restaurants"]
        uncategorized = setup_data["uncategorized"]

        # Chase uses "Food & Drink"
        chase_result = mapper.map_category(chase.institution_id, "Restaurants")
        assert chase_result == uncategorized.category_id  # Not mapped for Chase

        # Discover uses "Restaurants"
        discover_result = mapper.map_category(discover.institution_id, "Restaurants")
        assert discover_result == restaurants.category_id

    def test_map_categories_batch(self, db_session, setup_data):
        """Should map categories for multiple transactions"""
        mapper = CategoryMapper(db_session)
        chase = setup_data["chase"]

        parsed = [
            {"row_number": 1, "bank_category": "Food & Drink"},
            {"row_number": 2, "bank_category": "Shopping"},
            {"row_number": 3, "bank_category": "Unknown"},
            {"row_number": 4, "bank_category": None},
        ]

        result = mapper.map_categories(chase.institution_id, parsed)

        assert result[0]["coinpurse_category_id"] == setup_data["restaurants"].category_id
        assert result[1]["coinpurse_category_id"] == setup_data["shopping"].category_id
        assert result[2]["coinpurse_category_id"] == setup_data["uncategorized"].category_id
        assert result[3]["coinpurse_category_id"] == setup_data["uncategorized"].category_id

    def test_cache_is_used(self, db_session, setup_data):
        """Should cache mappings for performance"""
        mapper = CategoryMapper(db_session)
        chase = setup_data["chase"]

        # First call builds cache
        mapper.get_mappings_for_institution(chase.institution_id)
        assert chase.institution_id in mapper._mapping_cache

        # Cache should contain the mappings
        cached = mapper._mapping_cache[chase.institution_id]
        assert "food & drink" in cached
        assert "shopping" in cached

    def test_clear_cache(self, db_session, setup_data):
        """Should clear cache when requested"""
        mapper = CategoryMapper(db_session)
        chase = setup_data["chase"]

        mapper.get_mappings_for_institution(chase.institution_id)
        mapper.get_uncategorized_category_id()

        mapper.clear_cache()

        assert mapper._mapping_cache is None
        assert mapper._uncategorized_id is None
