"""
Unit tests for CategoryMappingRepository group methods
"""

import pytest
from sqlalchemy.orm import Session

from models import Category, CategoryMapping, Institution
from repositories.category_mapping_repository import CategoryMappingRepository


class TestGetActiveByGroup:
    """Tests for get_active_by_group"""

    def test_returns_matching_mappings(self, db_session: Session):
        inst = Institution(name="Test Bank")
        cat1 = Category(name="Cat1")
        cat2 = Category(name="Cat2")
        db_session.add_all([inst, cat1, cat2])
        db_session.commit()

        for c in [cat1, cat2]:
            db_session.add(
                CategoryMapping(
                    institution_id=inst.institution_id,
                    bank_category_name="Dining",
                    coinpurse_category_id=c.category_id,
                )
            )
        db_session.commit()

        repo = CategoryMappingRepository(db_session)
        result = repo.get_active_by_group(inst.institution_id, "Dining")
        assert len(result) == 2

    def test_excludes_inactive(self, db_session: Session):
        inst = Institution(name="Test Bank")
        cat = Category(name="Cat")
        db_session.add_all([inst, cat])
        db_session.commit()

        db_session.add(
            CategoryMapping(
                institution_id=inst.institution_id,
                bank_category_name="Inactive",
                coinpurse_category_id=cat.category_id,
                is_active=False,
            )
        )
        db_session.commit()

        repo = CategoryMappingRepository(db_session)
        result = repo.get_active_by_group(inst.institution_id, "Inactive")
        assert len(result) == 0

    def test_excludes_different_group(self, db_session: Session):
        inst = Institution(name="Test Bank")
        cat = Category(name="Cat")
        db_session.add_all([inst, cat])
        db_session.commit()

        db_session.add(
            CategoryMapping(
                institution_id=inst.institution_id,
                bank_category_name="Other",
                coinpurse_category_id=cat.category_id,
            )
        )
        db_session.commit()

        repo = CategoryMappingRepository(db_session)
        result = repo.get_active_by_group(inst.institution_id, "Dining")
        assert len(result) == 0


class TestSaveGroup:
    """Tests for save_group"""

    @pytest.fixture
    def setup(self, db_session: Session):
        inst = Institution(name="Save Bank")
        cats = [Category(name=f"Cat{i}") for i in range(4)]
        db_session.add(inst)
        db_session.add_all(cats)
        db_session.commit()
        db_session.refresh(inst)
        for c in cats:
            db_session.refresh(c)
        return {
            "inst": inst,
            "cats": cats,
            "repo": CategoryMappingRepository(db_session),
        }

    def test_creates_new_group(self, setup):
        repo = setup["repo"]
        inst = setup["inst"]
        cats = setup["cats"]

        result = repo.save_group(
            inst.institution_id, "New Group", [cats[0].category_id, cats[1].category_id]
        )

        assert len(result) == 2
        cat_ids = {m.coinpurse_category_id for m in result}
        assert cat_ids == {cats[0].category_id, cats[1].category_id}

    def test_adds_to_existing_group(self, db_session, setup):
        repo = setup["repo"]
        inst = setup["inst"]
        cats = setup["cats"]

        db_session.add(
            CategoryMapping(
                institution_id=inst.institution_id,
                bank_category_name="Existing",
                coinpurse_category_id=cats[0].category_id,
            )
        )
        db_session.commit()

        result = repo.save_group(
            inst.institution_id, "Existing", [cats[0].category_id, cats[1].category_id]
        )

        assert len(result) == 2

    def test_removes_from_existing_group(self, db_session, setup):
        repo = setup["repo"]
        inst = setup["inst"]
        cats = setup["cats"]

        for c in cats[:3]:
            db_session.add(
                CategoryMapping(
                    institution_id=inst.institution_id,
                    bank_category_name="Shrink",
                    coinpurse_category_id=c.category_id,
                )
            )
        db_session.commit()

        result = repo.save_group(inst.institution_id, "Shrink", [cats[0].category_id])

        assert len(result) == 1
        assert result[0].coinpurse_category_id == cats[0].category_id

    def test_renames_group(self, db_session, setup):
        repo = setup["repo"]
        inst = setup["inst"]
        cats = setup["cats"]

        db_session.add(
            CategoryMapping(
                institution_id=inst.institution_id,
                bank_category_name="Before",
                coinpurse_category_id=cats[0].category_id,
            )
        )
        db_session.commit()

        result = repo.save_group(
            inst.institution_id,
            "After",
            [cats[0].category_id],
            old_bank_category_name="Before",
        )

        assert len(result) == 1
        assert result[0].bank_category_name == "After"

        # Old name should be gone
        old = repo.get_active_by_group(inst.institution_id, "Before")
        assert len(old) == 0

    def test_rename_and_modify(self, db_session, setup):
        repo = setup["repo"]
        inst = setup["inst"]
        cats = setup["cats"]

        for c in cats[:2]:
            db_session.add(
                CategoryMapping(
                    institution_id=inst.institution_id,
                    bank_category_name="OldName",
                    coinpurse_category_id=c.category_id,
                )
            )
        db_session.commit()

        # Rename and swap cats[1] for cats[2]
        result = repo.save_group(
            inst.institution_id,
            "NewName",
            [cats[0].category_id, cats[2].category_id],
            old_bank_category_name="OldName",
        )

        assert len(result) == 2
        assert all(m.bank_category_name == "NewName" for m in result)
        cat_ids = {m.coinpurse_category_id for m in result}
        assert cat_ids == {cats[0].category_id, cats[2].category_id}

    def test_retains_existing_mapping_ids(self, db_session, setup):
        """Retained mappings should keep their original mapping_id"""
        repo = setup["repo"]
        inst = setup["inst"]
        cats = setup["cats"]

        m = CategoryMapping(
            institution_id=inst.institution_id,
            bank_category_name="Stable",
            coinpurse_category_id=cats[0].category_id,
        )
        db_session.add(m)
        db_session.commit()
        db_session.refresh(m)
        original_id = m.mapping_id

        result = repo.save_group(
            inst.institution_id, "Stable", [cats[0].category_id, cats[1].category_id]
        )

        retained = [r for r in result if r.coinpurse_category_id == cats[0].category_id]
        assert len(retained) == 1
        assert retained[0].mapping_id == original_id


class TestDeleteGroup:
    """Tests for delete_group"""

    def test_deletes_all_in_group(self, db_session: Session):
        inst = Institution(name="Delete Bank")
        cat1 = Category(name="D1")
        cat2 = Category(name="D2")
        db_session.add_all([inst, cat1, cat2])
        db_session.commit()

        for c in [cat1, cat2]:
            db_session.add(
                CategoryMapping(
                    institution_id=inst.institution_id,
                    bank_category_name="Gone",
                    coinpurse_category_id=c.category_id,
                )
            )
        db_session.commit()

        repo = CategoryMappingRepository(db_session)
        repo.delete_group(inst.institution_id, "Gone")

        remaining = repo.get_active_by_group(inst.institution_id, "Gone")
        assert len(remaining) == 0

    def test_does_not_affect_other_groups(self, db_session: Session):
        inst = Institution(name="Delete Bank 2")
        cat1 = Category(name="Keep1")
        cat2 = Category(name="Keep2")
        db_session.add_all([inst, cat1, cat2])
        db_session.commit()

        db_session.add(
            CategoryMapping(
                institution_id=inst.institution_id,
                bank_category_name="ToDelete",
                coinpurse_category_id=cat1.category_id,
            )
        )
        db_session.add(
            CategoryMapping(
                institution_id=inst.institution_id,
                bank_category_name="ToKeep",
                coinpurse_category_id=cat2.category_id,
            )
        )
        db_session.commit()

        repo = CategoryMappingRepository(db_session)
        repo.delete_group(inst.institution_id, "ToDelete")

        kept = repo.get_active_by_group(inst.institution_id, "ToKeep")
        assert len(kept) == 1

    def test_delete_empty_group_is_noop(self, db_session: Session):
        inst = Institution(name="Empty Bank")
        db_session.add(inst)
        db_session.commit()

        repo = CategoryMappingRepository(db_session)
        # Should not raise
        repo.delete_group(inst.institution_id, "Nonexistent")
        # verify still empty
        assert repo.get_active_by_group(inst.institution_id, "Nonexistent") == []
