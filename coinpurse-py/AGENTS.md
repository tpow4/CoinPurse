# AGENTS.md

This file provides guidance to AI tools when working with code in this repository.

## Project Overview

CoinPurse is a personal finance tracking application with a Python 3.13+ FastAPI backend and a Svelte frontend (`coinpurse-client/`). The backend uses SQLAlchemy ORM with SQLite and follows a layered architecture.

## Development Commands

### Environment Setup

```bash
source backend/venv/bin/activate
cd backend && pip install -r requirements.txt
python database.py  # creates tables AND seeds default data (categories, institutions, import templates, category mappings, app settings)
```

### Running

```bash
cd backend && uvicorn main:app --reload --port 8000
```

### Testing

```bash
cd backend && pytest                # all tests
pytest tests/unit                   # unit only
pytest tests/integration            # integration only
pytest --cov                        # with coverage
```

Tests use in-memory SQLite with per-test transaction rollback for isolation.

### Linting/Formatting

```bash
cd backend && ruff check .          # lint
ruff check --fix .                  # lint + autofix
ruff format .                       # format
```

Config in `pyproject.toml`: line-length 88, double quotes, LF endings, B008 ignored (FastAPI `Depends`).

### API Docs

- Swagger UI: `http://localhost:8000/docs`
- Scalar: `http://localhost:8000/scalar`
- Health: `http://localhost:8000/health`

## Architecture

### Layers

1. **Routers** (`routers/`) - HTTP endpoints, FastAPI dependency injection, Pydantic validation. Some delegate to services, others go directly to repositories.
2. **Services** (`services/`) - Business logic orchestration (see Import System below).
3. **Repositories** (`repositories/`) - Data access via SQLAlchemy ORM. Each takes a `Session` in `__init__`.
4. **Models** (`models/`) - SQLAlchemy 2.0 models using `Mapped[]` + `mapped_column()`. Relationships use `relationship()` with `back_populates`.
5. **Schemas** (`schemas/`) - Pydantic DTOs with separate Create/Update/Response variants. Use `from_attributes = True`.

### Database Models

Entities in dependency order:

- No FK: `AppSetting`, `Category`, `ImportTemplate`, `Institution`
- Depends on Institution: `CategoryMapping`
- Depends on Institution + ImportTemplate: `Account`, `AccountBalance`, `Transaction`
- Depends on Account + ImportTemplate: `ImportBatch`

Enums: `AccountType`, `TaxTreatmentType`, `TransactionType`, `FileFormat`, `ImportStatus`

### Model Import Order (`models/__init__.py`)

1. `Base` + all enums
2. No-FK models: `AppSetting`, `Category`, `ImportTemplate`, `Institution`
3. `CategoryMapping` (depends on Institution)
4. `Account`, `AccountBalance`, `Transaction` (depend on Institution + ImportTemplate)
5. `ImportBatch` (depends on Account + ImportTemplate)

### Import System

Services in `services/`:

- `ImportService` - orchestrates file import (parse, deduplicate, map categories, create transactions)
- `BalanceAggregationService` - monthly balance snapshots with forward-fill
- `CategoryMapper` - maps bank categories to CoinPurse categories via `CategoryMapping`
- `DuplicateDetector` - hash-based duplicate transaction detection
- `parsers/` - `CsvParser`, `ExcelParser` extending `BaseParser` (uses pandas)

Workflow: Upload CSV/Excel -> parse with `ImportTemplate` -> detect duplicates -> map categories -> preview -> confirm -> create transactions.

### Soft Delete

- Most models use `is_active` boolean field for soft deletion
- Repository `get_all()` methods have `include_inactive` parameter
- Repositories support both soft delete (default) and hard delete

### Conventions

- Schema module name matches model name (e.g., `schemas/account.py` for `Account` model)
- All models use `created_at` and `modified_at` timestamps (UTC)
- Primary keys: `{table_name}_id` (e.g., `institution_id`, `account_id`)
- Routers instantiate repositories per-request: `repo = FooRepository(db)`

## Key Configuration

- **Python:** 3.13+ (from `pyproject.toml`)
- **Database:** SQLite at `backend/coinpurse.db`
- **CORS:** Svelte dev server at `http://localhost:5173`
- **API Prefix:** All routers use `/api`
- **Echo SQL:** `echo=True` in `database.py` - disable in production
