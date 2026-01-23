from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from models import Base, Category, FileFormat, ImportTemplate, Institution

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
        _seed_uncategorized_category(db)
        _seed_institutions(db)
        _seed_import_templates(db)
    finally:
        db.close()


def _seed_uncategorized_category(db):
    """Seed the Uncategorized category"""
    stmt = select(Category).where(Category.name == "Uncategorized")
    existing = db.scalar(stmt)
    if not existing:
        uncategorized = Category(name="Uncategorized")
        db.add(uncategorized)
        db.commit()
        print("Seeded 'Uncategorized' category.")
    else:
        print("'Uncategorized' category already exists.")


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
    """Seed the default import templates for each institution"""
    # Get institution IDs
    chase = db.scalar(select(Institution).where(Institution.name == "Chase"))
    discover = db.scalar(select(Institution).where(Institution.name == "Discover"))
    capital_one = db.scalar(select(Institution).where(Institution.name == "Capital One"))

    if not all([chase, discover, capital_one]):
        print("Warning: Not all institutions found. Skipping template seeding.")
        return

    templates = [
        # Chase Credit Card - bank_standard (signs already correct)
        {
            "template_name": "Chase Credit Card",
            "institution_id": chase.institution_id,
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
            "institution_id": discover.institution_id,
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
            "institution_id": capital_one.institution_id,
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
            "date_format": "%m/%d/%Y",
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
