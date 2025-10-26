from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "sqlite:///./coinpurse.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}, # Sqlite specific option
    echo=True # log all SQL statements - TODO turn off in production
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all tables in the database"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Completed creating database tables.")

def get_session():
    """Get a new database session"""
    return SessionLocal()

if __name__ == "__main__":
    init_db()
