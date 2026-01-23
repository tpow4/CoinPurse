"""
Shared pytest fixtures for all tests
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models import Base, Category, Institution


@pytest.fixture(scope="session")
def engine():
    """Create an in-memory SQLite engine for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db_session(engine):
    """
    Create a new database session for each test function.
    Rolls back after each test to ensure isolation.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session")
def session_factory(engine):
    """Session factory for creating new sessions"""
    return sessionmaker(bind=engine)


@pytest.fixture
def uncategorized_category(db_session: Session) -> Category:
    """Create the Uncategorized category"""
    category = Category(name="Uncategorized")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def sample_categories(db_session: Session) -> list[Category]:
    """Create sample categories for testing"""
    categories = [
        Category(name="Uncategorized"),
        Category(name="Restaurants"),
        Category(name="Shopping"),
        Category(name="Entertainment"),
        Category(name="Payments"),
    ]
    for cat in categories:
        db_session.add(cat)
    db_session.commit()
    for cat in categories:
        db_session.refresh(cat)
    return categories


@pytest.fixture
def sample_institutions(db_session: Session) -> list[Institution]:
    """Create sample institutions for testing"""
    institutions = [
        Institution(name="Chase"),
        Institution(name="Discover"),
        Institution(name="Capital One"),
    ]
    for inst in institutions:
        db_session.add(inst)
    db_session.commit()
    for inst in institutions:
        db_session.refresh(inst)
    return institutions


# Template configurations for testing parsers
@pytest.fixture
def chase_template_config() -> dict:
    """Chase Credit Card template configuration"""
    return {
        "column_mappings": {
            "transaction_date": "Transaction Date",
            "posted_date": "Post Date",
            "description": "Description",
            "category": "Category",
            "amount": "Amount",
        },
        "amount_config": {
            "sign_convention": "bank_standard",
            "decimal_places": 2,
        },
        "date_format": "%m/%d/%Y",
        "header_row": 1,
        "skip_rows": 0,
    }


@pytest.fixture
def discover_template_config() -> dict:
    """Discover Credit Card template configuration"""
    return {
        "column_mappings": {
            "transaction_date": "Trans. Date",
            "posted_date": "Post Date",
            "description": "Description",
            "amount": "Amount",
            "category": "Category",
        },
        "amount_config": {
            "sign_convention": "inverted",
            "decimal_places": 2,
        },
        "date_format": "%m/%d/%Y",
        "header_row": 1,
        "skip_rows": 0,
    }


@pytest.fixture
def capital_one_template_config() -> dict:
    """Capital One Credit Card template configuration"""
    return {
        "column_mappings": {
            "transaction_date": "Transaction Date",
            "posted_date": "Posted Date",
            "description": "Description",
            "category": "Category",
            "debit": "Debit",
            "credit": "Credit",
        },
        "amount_config": {
            "sign_convention": "split_columns",
            "debit_column": "Debit",
            "credit_column": "Credit",
            "decimal_places": 2,
        },
        "date_format": "%m/%d/%Y",
        "header_row": 1,
        "skip_rows": 0,
    }
