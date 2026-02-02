from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from models import (
    Base,
    Category,
    CategoryMapping,
    FileFormat,
    ImportTemplate,
    Institution,
)

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "coinpurse.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Sqlite specific option
    echo=True,  # log all SQL statements - TODO turn off in production
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables in the database"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Completed creating database tables.")
    seed_data()


def seed_data():
    """Seed initial data into the database"""
    db = SessionLocal()
    try:
        _seed_categories(db)
        _seed_institutions(db)
        _seed_import_templates(db)
        _seed_category_mappings(db)
    finally:
        db.close()


def _seed_categories(db):
    """Seed the default categories"""
    categories = [
        "Uncategorized",
        "Automotive",
        "Bills & utilities",
        "Education",
        "Entertainment",
        "Fees & adjustments",
        "Food & drink",
        "Gas",
        "Gifts & donations",
        "Groceries",
        "Health",
        "Home improvement",
        "Miscellaneous",
        "Payment services",
        "Professional services",
        "Shopping",
        "Travel",
    ]

    for name in categories:
        stmt = select(Category).where(Category.name == name)
        existing = db.scalar(stmt)
        if existing is None:
            db.add(Category(name=name))
            print(f"Seeded '{name}' category.")
        elif not existing.is_active:
            existing.is_active = True
            print(f"Re-activated '{name}' category.")
        else:
            print(f"'{name}' category already exists.")

    db.commit()


def _seed_institutions(db):
    """Seed the default institutions"""
    institutions = ["Chase", "Discover", "Capital One"]

    for name in institutions:
        stmt = select(Institution).where(Institution.name == name)
        existing = db.scalar(stmt)
        if not existing:
            institution = Institution(name=name)
            db.add(institution)
            print(f"Seeded '{name}' institution.")

    db.commit()


def _seed_import_templates(db):
    """Seed the default import templates"""
    templates = [
        # Chase Credit Card - bank_standard (signs already correct)
        {
            "template_name": "Chase Credit Card",
            "file_format": FileFormat.CSV,
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
        },
        # Discover Credit Card - inverted (multiply by -1)
        {
            "template_name": "Discover Credit Card",
            "file_format": FileFormat.CSV,
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
        },
        # Capital One Credit Card - split_columns (Debit/Credit columns)
        {
            "template_name": "Capital One Credit Card",
            "file_format": FileFormat.CSV,
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
            "date_format": "%y/%m/%d",
            "header_row": 1,
            "skip_rows": 0,
        },
    ]

    for template_data in templates:
        stmt = select(ImportTemplate).where(
            ImportTemplate.template_name == template_data["template_name"]
        )
        existing = db.scalar(stmt)
        if not existing:
            template = ImportTemplate(**template_data)
            db.add(template)
            print(f"Seeded '{template_data['template_name']}' template.")
        else:
            print(f"'{template_data['template_name']}' template already exists.")

    db.commit()


def _seed_category_mappings(db):
    """Seed category mappings for institutions"""
    # bank_category_name -> list of coinpurse_category_ids
    institution_mappings = {
        "Chase": [
            ("Automotive", [2]),
            ("Bills & utilities", [3]),
            ("Education", [4]),
            ("Entertainment", [5]),
            ("Fees & adjustments", [6]),
            ("Food & drink", [7]),
            ("Gas", [8]),
            ("Gifts & donations", [9]),
            ("Groceries", [10]),
            ("Health & wellness", [11]),
            ("Home", [12]),
            ("Miscellaneous", [13]),
            ("Personal", [14]),
            ("Professional services", [15]),
            ("Shopping", [16]),
            ("Travel", [17]),
        ],
        "Discover": [
            ("Automotive", [2]),
            ("Department stores", [16]),
            ("Education", [4]),
            ("Gasoline", [8]),
            ("Government services", [15]),
            ("Home improvement", [12]),
            ("Medical services", [11]),
            ("Merchandise", [16]),
            ("Restaurants", [7]),
            ("Services", [15]),
            ("Supermarkets", [10]),
            ("Travel / Entertainment", [5, 17]),
            ("Wholesale clubs", [16]),
        ],
        "Capital One": [
            ("Dining", [7]),
            ("Entertainment", [5]),
            ("Gas/Automotive", [2, 8]),
            ("Grocery", [10]),
            ("Healthcare", [11]),
            ("Internet", [3]),
            ("Other", [13]),
            ("Other services", [15]),
            ("Other Travel", [17]),
            ("Phone/cable", [3]),
        ],
    }

    for institution_name, mappings in institution_mappings.items():
        institution = db.scalar(
            select(Institution).where(Institution.name == institution_name)
        )
        if not institution:
            print(
                f"{institution_name} institution not found, skipping category mappings."
            )
            continue

        for bank_category, category_ids in mappings:
            for priority, category_id in enumerate(category_ids, start=1):
                stmt = select(CategoryMapping).where(
                    CategoryMapping.institution_id == institution.institution_id,
                    CategoryMapping.bank_category_name == bank_category,
                    CategoryMapping.coinpurse_category_id == category_id,
                )
                existing = db.scalar(stmt)
                if not existing:
                    db.add(
                        CategoryMapping(
                            institution_id=institution.institution_id,
                            bank_category_name=bank_category,
                            coinpurse_category_id=category_id,
                            priority=priority,
                        )
                    )
                    print(
                        f"Seeded {institution_name} mapping: "
                        f"'{bank_category}' -> category {category_id} (priority {priority})."
                    )
                else:
                    print(
                        f"{institution_name} mapping '{bank_category}' -> {category_id} already exists."
                    )

        db.commit()


def get_session():
    """Get a new database session"""
    return SessionLocal()


def get_db():
    """FastAPI dependency that provides a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
