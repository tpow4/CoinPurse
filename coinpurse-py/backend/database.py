from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from models import Base, Category, CategoryMapping, FileFormat, ImportTemplate, Institution

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
            ("Automotive", [1]),
            ("Bills & utilities", [2]),
            ("Education", [3]),
            ("Entertainment", [4]),
            ("Fees & adjustments", [5]),
            ("Food & drink", [6]),
            ("Gas", [7]),
            ("Gifts & donations", [8]),
            ("Groceries", [9]),
            ("Health & wellness", [10]),
            ("Home", [11]),
            ("Miscellaneous", [12]),
            ("Personal", [13]),
            ("Professional services", [14]),
            ("Shopping", [15]),
            ("Travel", [16]),
        ],
        "Discover": [
            ("Automotive", [1]),
            ("Department stores", [15]),
            ("Education", [3]),
            ("Gasoline", [7]),
            ("Government services", [14]),
            ("Home improvement", [11]),
            ("Medical services", [10]),
            ("Merchandise", [15]),
            ("Restaurants", [6]),
            ("Services", [14]),
            ("Supermarkets", [9]),
            ("Travel / Entertainment", [4, 16]),
            ("Wholesale clubs", [15]),
        ],
        "Capital One": [
            ("Dining", [6]),
            ("Entertainment", [4]),
            ("Gas/Automotive", [1, 7]),
            ("Grocery", [9]),
            ("Healthcare", [10]),
            ("Internet", [2]),
            ("Other", [12]),
            ("Other services", [14]),
            ("Other Travel", [16]),
            ("Phone/cable", [2]),
        ],
    }

    for institution_name, mappings in institution_mappings.items():
        institution = db.scalar(
            select(Institution).where(Institution.name == institution_name)
        )
        if not institution:
            print(f"{institution_name} institution not found, skipping category mappings.")
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
                    print(f"{institution_name} mapping '{bank_category}' -> {category_id} already exists.")

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
