"""
Unit tests for duplicate detection service
"""

from datetime import date

import pytest

from models import Account, AccountType, Category, Institution, TaxTreatmentType, Transaction, TransactionType
from services import DuplicateDetector, TransactionHash


class TestTransactionHash:
    """Tests for TransactionHash dataclass"""

    def test_hash_equality(self):
        """Identical transactions should have equal hashes"""
        hash1 = TransactionHash(
            account_id=1,
            transaction_date=date(2026, 1, 15),
            description="amazon purchase",
            transaction_type="DEBIT",
            amount=-5000,
        )
        hash2 = TransactionHash(
            account_id=1,
            transaction_date=date(2026, 1, 15),
            description="amazon purchase",
            transaction_type="DEBIT",
            amount=-5000,
        )

        assert hash1 == hash2
        assert hash(hash1) == hash(hash2)

    def test_hash_inequality_different_amount(self):
        """Different amounts should produce different hashes"""
        hash1 = TransactionHash(
            account_id=1,
            transaction_date=date(2026, 1, 15),
            description="amazon purchase",
            transaction_type="DEBIT",
            amount=-5000,
        )
        hash2 = TransactionHash(
            account_id=1,
            transaction_date=date(2026, 1, 15),
            description="amazon purchase",
            transaction_type="DEBIT",
            amount=-5001,
        )

        assert hash1 != hash2

    def test_hash_inequality_different_date(self):
        """Different dates should produce different hashes"""
        hash1 = TransactionHash(
            account_id=1,
            transaction_date=date(2026, 1, 15),
            description="amazon purchase",
            transaction_type="DEBIT",
            amount=-5000,
        )
        hash2 = TransactionHash(
            account_id=1,
            transaction_date=date(2026, 1, 16),
            description="amazon purchase",
            transaction_type="DEBIT",
            amount=-5000,
        )

        assert hash1 != hash2

    def test_hash_inequality_different_account(self):
        """Different accounts should produce different hashes"""
        hash1 = TransactionHash(
            account_id=1,
            transaction_date=date(2026, 1, 15),
            description="amazon purchase",
            transaction_type="DEBIT",
            amount=-5000,
        )
        hash2 = TransactionHash(
            account_id=2,
            transaction_date=date(2026, 1, 15),
            description="amazon purchase",
            transaction_type="DEBIT",
            amount=-5000,
        )

        assert hash1 != hash2

    def test_from_parsed_row_normalizes_description(self):
        """from_parsed_row should normalize description"""
        hash1 = TransactionHash.from_parsed_row(
            account_id=1,
            transaction_date=date(2026, 1, 15),
            description="  AMAZON Purchase  ",
            transaction_type="DEBIT",
            amount=-5000,
        )
        hash2 = TransactionHash.from_parsed_row(
            account_id=1,
            transaction_date=date(2026, 1, 15),
            description="amazon purchase",
            transaction_type="DEBIT",
            amount=-5000,
        )

        assert hash1 == hash2


class TestDuplicateDetector:
    """Tests for DuplicateDetector service"""

    @pytest.fixture
    def setup_data(self, db_session):
        """Set up test data"""
        # Create institution
        institution = Institution(name="Test Bank")
        db_session.add(institution)
        db_session.commit()

        # Create category
        category = Category(name="Uncategorized")
        db_session.add(category)
        db_session.commit()

        # Create account
        account = Account(
            institution_id=institution.institution_id,
            account_name="Test Checking",
            account_type=AccountType.BANKING,
            tax_treatment=TaxTreatmentType.NOT_APPLICABLE,
            last_4_digits="1234",
            tracks_transactions=True,
        )
        db_session.add(account)
        db_session.commit()

        # Create existing transactions
        txn1 = Transaction(
            account_id=account.account_id,
            category_id=category.category_id,
            transaction_date=date(2026, 1, 15),
            posted_date=date(2026, 1, 15),
            amount=-5000,
            description="AMAZON PURCHASE",
            transaction_type=TransactionType.PURCHASE,
            notes="",
        )
        txn2 = Transaction(
            account_id=account.account_id,
            category_id=category.category_id,
            transaction_date=date(2026, 1, 16),
            posted_date=date(2026, 1, 16),
            amount=10000,
            description="PAYROLL DEPOSIT",
            transaction_type=TransactionType.DEPOSIT,
            notes="",
        )
        db_session.add_all([txn1, txn2])
        db_session.commit()

        return {"account": account, "category": category}

    def test_is_duplicate_true(self, db_session, setup_data):
        """Should detect existing transaction as duplicate"""
        detector = DuplicateDetector(db_session)
        account = setup_data["account"]

        is_dup = detector.is_duplicate(
            account_id=account.account_id,
            transaction_date=date(2026, 1, 15),
            description="amazon purchase",  # Different case
            transaction_type="DEBIT",
            amount=-5000,
        )

        assert is_dup is True

    def test_is_duplicate_false_different_amount(self, db_session, setup_data):
        """Should not detect as duplicate if amount differs"""
        detector = DuplicateDetector(db_session)
        account = setup_data["account"]

        is_dup = detector.is_duplicate(
            account_id=account.account_id,
            transaction_date=date(2026, 1, 15),
            description="amazon purchase",
            transaction_type="DEBIT",
            amount=-5001,  # Different amount
        )

        assert is_dup is False

    def test_is_duplicate_false_different_date(self, db_session, setup_data):
        """Should not detect as duplicate if date differs"""
        detector = DuplicateDetector(db_session)
        account = setup_data["account"]

        is_dup = detector.is_duplicate(
            account_id=account.account_id,
            transaction_date=date(2026, 1, 17),  # Different date
            description="amazon purchase",
            transaction_type="DEBIT",
            amount=-5000,
        )

        assert is_dup is False

    def test_check_duplicates_batch(self, db_session, setup_data):
        """Should check multiple transactions for duplicates"""
        detector = DuplicateDetector(db_session)
        account = setup_data["account"]

        parsed = [
            {
                "row_number": 1,
                "transaction_date": date(2026, 1, 15),
                "description": "AMAZON PURCHASE",
                "transaction_type": "DEBIT",
                "amount": -5000,
            },
            {
                "row_number": 2,
                "transaction_date": date(2026, 1, 17),
                "description": "NEW PURCHASE",
                "transaction_type": "DEBIT",
                "amount": -2500,
            },
        ]

        result = detector.check_duplicates(account.account_id, parsed)

        assert result[0]["is_duplicate"] is True
        assert result[1]["is_duplicate"] is False

    def test_check_duplicates_skips_null_dates(self, db_session, setup_data):
        """Should mark rows with null dates as not duplicate"""
        detector = DuplicateDetector(db_session)
        account = setup_data["account"]

        parsed = [
            {
                "row_number": 1,
                "transaction_date": None,
                "description": "NO DATE",
                "transaction_type": "DEBIT",
                "amount": -5000,
            },
        ]

        result = detector.check_duplicates(account.account_id, parsed)

        assert result[0]["is_duplicate"] is False

    def test_cache_is_used(self, db_session, setup_data):
        """Should cache hash set for same account"""
        detector = DuplicateDetector(db_session)
        account = setup_data["account"]

        # First call builds cache
        detector.build_hash_set(account.account_id)
        assert detector._cached_account_id == account.account_id

        # Second call should use cache (not rebuild)
        hash_set = detector.build_hash_set(account.account_id)
        assert len(hash_set) == 2

    def test_clear_cache(self, db_session, setup_data):
        """Should clear cache when requested"""
        detector = DuplicateDetector(db_session)
        account = setup_data["account"]

        detector.build_hash_set(account.account_id)
        assert detector._hash_cache is not None

        detector.clear_cache()
        assert detector._hash_cache is None
        assert detector._cached_account_id is None
