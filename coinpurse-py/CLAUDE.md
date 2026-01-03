# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CoinPurse is a personal finance tracking application with a Python FastAPI backend and (presumably) a Svelte frontend. The backend uses SQLAlchemy ORM with SQLite database and follows a clean layered architecture pattern.

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source backend/venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Initialize database
python database.py
```

### Running the Application
```bash
# Run development server
cd backend
uvicorn main:app --reload --port 8000

# Alternative: Use VS Code debugger configuration
# The launch.json is configured for FastAPI debugging
```

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- Scalar API Reference: `http://localhost:8000/scalar`
- Health check: `http://localhost:8000/health`

## Architecture

### Layered Architecture Pattern
The backend follows a strict 3-layer architecture:

1. **Routers** (`routers/`) - HTTP endpoints and request handling
   - Handle HTTP requests/responses
   - Use FastAPI dependency injection for database sessions
   - Validate input using Pydantic schemas
   - Delegate business logic to repositories

2. **Repositories** (`repositories/`) - Data access layer
   - Encapsulate all database operations
   - Use SQLAlchemy ORM for queries
   - Each repository class takes a `Session` in `__init__`

3. **Models** (`models/`) - SQLAlchemy ORM models
   - Define database schema using SQLAlchemy 2.0 mapped columns
   - Use `Mapped[]` type hints with `mapped_column()`
   - Relationships defined using `relationship()` with `back_populates`

4. **Schemas** (`schemas/`) - Pydantic DTOs
   - Define request/response validation models
   - Separate schemas for Create, Update, and Response operations
   - Use `from_attributes = True` for SQLAlchemy compatibility

### Database Models

Core entities in order of dependency:
- `Institution` - Financial institutions (no dependencies)
- `Category` - Transaction categories (no dependencies)
- `Account` - User accounts (depends on Institution)
- `Transaction` - Financial transactions (depends on Account, Category)
- `AccountBalance` - Account balance snapshots (depends on Account)

### Import Order
Due to circular dependency concerns, models are imported in a specific order in `models/__init__.py`:
1. Base classes and enums (`Base`, `AccountType`, `TransactionType`)
2. Models with no foreign keys (`Institution`, `Category`)
3. Models with dependencies (`Account`)
4. Models with nested dependencies (`Transaction`, `AccountBalance`)

### Soft Delete Pattern
- Most models use soft deletion via `is_active` boolean field
- Repository methods support both soft delete (default) and hard delete
- `get_all()` methods typically have `include_inactive` parameter
- Search operations default to excluding inactive records

### Common Patterns

**Router Pattern:**
```python
from database import get_db
from repositories.foo_repository import FooRepository

@router.get("/")
def list_foos(db: Session = Depends(get_db)):
    repo = FooRepository(db)
    return repo.get_all()
```

**Repository Pattern:**
```python
class FooRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        stmt = select(Foo).order_by(Foo.name)
        return list(self.db.scalars(stmt))
```

**Model Pattern:**
```python
class Foo(Base):
    __tablename__ = 'foos'

    foo_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
```

## Key Configuration

- **Database:** SQLite at `backend/coinpurse.db`
- **CORS:** Configured for Svelte dev server at `http://localhost:5173`
- **API Prefix:** All routers use `/api` prefix
- **Echo SQL:** Database has `echo=True` - disable in production

## Important Notes

- Schema field should be the same as the model name.
- All models use `created_at` and `updated_at` timestamps with UTC timezone
- Primary keys follow pattern: `{table_name}_id` (e.g., `institution_id`, `account_id`)
