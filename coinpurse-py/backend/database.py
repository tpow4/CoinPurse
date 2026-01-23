from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from models import Base, Category

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
        # Seed "Uncategorized" category if it doesn't exist
        stmt = select(Category).where(Category.name == "Uncategorized")
        existing = db.scalar(stmt)
        if not existing:
            uncategorized = Category(name="Uncategorized")
            db.add(uncategorized)
            db.commit()
            print("Seeded 'Uncategorized' category.")
        else:
            print("'Uncategorized' category already exists.")
    finally:
        db.close()


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
