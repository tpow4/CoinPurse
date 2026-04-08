"""
Integration tests for Transactions Router filtering.
"""

from datetime import date

from models import (
    Account,
    AccountType,
    Category,
    Institution,
    TaxTreatmentType,
    Transaction,
    TransactionType,
)
from routers.transactions_router import (
    list_transactions,
    list_transactions_with_names,
)


class TestTransactionListEndpoints:
    def test_list_transactions_with_multiple_account_and_category_filters(
        self, db_session
    ):
        institution = Institution(name="Test Bank")
        accounts = [
            Account(
                institution_id=1,
                account_name="Checking",
                account_type=AccountType.BANKING,
                tax_treatment=TaxTreatmentType.NOT_APPLICABLE,
                last_4_digits="1111",
            ),
            Account(
                institution_id=1,
                account_name="Card",
                account_type=AccountType.CREDIT_CARD,
                tax_treatment=TaxTreatmentType.NOT_APPLICABLE,
                last_4_digits="2222",
            ),
        ]
        categories = [
            Category(name="Groceries"),
            Category(name="Dining"),
            Category(name="Travel"),
        ]

        db_session.add(institution)
        db_session.flush()
        for account in accounts:
            account.institution_id = institution.institution_id
        db_session.add_all(accounts + categories)
        db_session.flush()

        transactions = [
            Transaction(
                account_id=accounts[0].account_id,
                category_id=categories[0].category_id,
                transaction_date=date(2026, 1, 15),
                posted_date=date(2026, 1, 16),
                amount=-2500,
                description="Groceries A",
                transaction_type=TransactionType.PURCHASE,
                notes="",
            ),
            Transaction(
                account_id=accounts[1].account_id,
                category_id=categories[1].category_id,
                transaction_date=date(2026, 1, 20),
                posted_date=date(2026, 1, 21),
                amount=-4200,
                description="Dining B",
                transaction_type=TransactionType.PURCHASE,
                notes="",
            ),
            Transaction(
                account_id=accounts[1].account_id,
                category_id=categories[2].category_id,
                transaction_date=date(2026, 1, 22),
                posted_date=date(2026, 1, 23),
                amount=-9900,
                description="Travel C",
                transaction_type=TransactionType.PURCHASE,
                notes="",
            ),
        ]
        db_session.add_all(transactions)
        db_session.commit()

        data = list_transactions_with_names(
            account_ids=[accounts[0].account_id, accounts[1].account_id],
            category_ids=[categories[0].category_id, categories[1].category_id],
            start_date=None,
            end_date=None,
            include_inactive=False,
            db=db_session,
        )

        descriptions = {row.description for row in data}
        assert descriptions == {"Groceries A", "Dining B"}

    def test_list_transactions_ignores_empty_multi_filters_and_still_applies_date_range(
        self, db_session
    ):
        institution = Institution(name="Date Range Bank")
        category = Category(name="Utilities")
        account = Account(
            institution_id=1,
            account_name="Checking",
            account_type=AccountType.BANKING,
            tax_treatment=TaxTreatmentType.NOT_APPLICABLE,
            last_4_digits="3333",
        )

        db_session.add_all([institution, category])
        db_session.flush()
        account.institution_id = institution.institution_id
        db_session.add(account)
        db_session.flush()

        transactions = [
            Transaction(
                account_id=account.account_id,
                category_id=category.category_id,
                transaction_date=date(2026, 2, 1),
                posted_date=date(2026, 2, 2),
                amount=-1000,
                description="Inside Range",
                transaction_type=TransactionType.PURCHASE,
                notes="",
            ),
            Transaction(
                account_id=account.account_id,
                category_id=category.category_id,
                transaction_date=date(2026, 3, 1),
                posted_date=date(2026, 3, 2),
                amount=-1500,
                description="Outside Range",
                transaction_type=TransactionType.PURCHASE,
                notes="",
            ),
        ]
        db_session.add_all(transactions)
        db_session.commit()

        data = list_transactions(
            account_ids=None,
            category_ids=None,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 28),
            include_inactive=False,
            db=db_session,
        )

        assert [row.description for row in data] == ["Inside Range"]
