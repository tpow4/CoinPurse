"""
API endpoints for Transactions
Handles all HTTP routes for transaction management
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.transaction import Transaction
from repositories.account_repository import AccountRepository
from repositories.category_repository import CategoryRepository
from repositories.transaction_repository import TransactionRepository
from schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionResponse, status_code=201)
def create_transaction(
    transaction_data: TransactionCreate, db: Session = Depends(get_db)
):
    """
    Create a new transaction

    - **account_id**: ID of the account this transaction belongs to (required)
    - **category_id**: ID of the category for this transaction (required)
    - **transaction_date**: Date of the transaction (required)
    - **posted_date**: Date the transaction was posted (required)
    - **amount**: Transaction amount in cents (required)
    - **description**: Transaction description (required)
    - **transaction_type**: Type of transaction (purchase, payment, refund, etc.) (required)
    - **notes**: Optional notes about the transaction (default: empty string)
    - **is_active**: Whether the transaction is active (default: True)
    """
    repo = TransactionRepository(db)
    account_repo = AccountRepository(db)
    category_repo = CategoryRepository(db)

    # Validate account exists
    if not account_repo.exists(transaction_data.account_id):
        raise HTTPException(
            status_code=400,
            detail=f"Account with ID {transaction_data.account_id} not found",
        )

    # Validate category exists
    if not category_repo.exists(transaction_data.category_id):
        raise HTTPException(
            status_code=400,
            detail=f"Category with ID {transaction_data.category_id} not found",
        )

    db_transaction = Transaction(**transaction_data.model_dump())

    created = repo.create(db_transaction)

    return created


@router.get("/", response_model=list[TransactionResponse])
def list_transactions(
    account_id: int | None = Query(None, description="Filter by account ID"),
    category_id: int | None = Query(None, description="Filter by category ID"),
    start_date: date | None = Query(None, description="Start date (inclusive)"),
    end_date: date | None = Query(None, description="End date (inclusive)"),
    include_inactive: bool = Query(False, description="Include inactive transactions"),
    db: Session = Depends(get_db),
):
    """
    Get all transactions with optional filters

    - **account_id**: Optional filter by account ID
    - **category_id**: Optional filter by category ID
    - **start_date**: Optional start date filter (inclusive)
    - **end_date**: Optional end date filter (inclusive)
    - **include_inactive**: Set to true to include inactive transactions
    """
    repo = TransactionRepository(db)

    # If any filter specified, use filtered query
    if (
        account_id is not None
        or category_id is not None
        or start_date is not None
        or end_date is not None
    ):
        return repo.get_by_date_range(
            start_date=start_date,
            end_date=end_date,
            account_id=account_id,
            category_id=category_id,
            include_inactive=include_inactive,
        )

    return repo.get_all(include_inactive=include_inactive)


@router.get("/search", response_model=list[TransactionResponse])
def search_transactions(
    q: str = Query(..., min_length=1, description="Search term"),
    include_inactive: bool = Query(False, description="Include inactive transactions"),
    db: Session = Depends(get_db),
):
    """
    Search transactions by description (case-insensitive partial match)

    - **q**: Search term to match against transaction descriptions
    - **include_inactive**: Set to true to include inactive transactions
    """
    repo = TransactionRepository(db)
    return repo.search_by_description(q, include_inactive=include_inactive)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """
    Get a specific transaction by ID

    - **transaction_id**: The ID of the transaction to retrieve
    """
    repo = TransactionRepository(db)
    transaction = repo.get_by_id(transaction_id)

    if not transaction:
        raise HTTPException(
            status_code=404, detail=f"Transaction with ID {transaction_id} not found"
        )

    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a transaction

    - **transaction_id**: The ID of the transaction to update
    - **account_id**: New account ID (optional)
    - **category_id**: New category ID (optional)
    - **transaction_date**: New transaction date (optional)
    - **posted_date**: New posted date (optional)
    - **amount**: New amount in cents (optional)
    - **description**: New description (optional)
    - **transaction_type**: New transaction type (optional)
    - **notes**: New notes (optional)
    - **is_active**: New active status (optional)
    """
    repo = TransactionRepository(db)
    transaction = repo.get_by_id(transaction_id)

    if not transaction:
        raise HTTPException(
            status_code=404, detail=f"Transaction with ID {transaction_id} not found"
        )

    # Validate account exists if being updated
    if transaction_data.account_id is not None:
        account_repo = AccountRepository(db)
        if not account_repo.exists(transaction_data.account_id):
            raise HTTPException(
                status_code=400,
                detail=f"Account with ID {transaction_data.account_id} not found",
            )

    # Validate category exists if being updated
    if transaction_data.category_id is not None:
        category_repo = CategoryRepository(db)
        if not category_repo.exists(transaction_data.category_id):
            raise HTTPException(
                status_code=400,
                detail=f"Category with ID {transaction_data.category_id} not found",
            )

    # Update only provided fields
    update_data = transaction_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    return repo.update(transaction)


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    hard_delete: bool = Query(
        False, description="Permanently delete (use with caution)"
    ),
    db: Session = Depends(get_db),
):
    """
    Delete a transaction (soft delete by default)

    - **transaction_id**: The ID of the transaction to delete
    - **hard_delete**: If true, permanently deletes. Otherwise, soft deletes (sets is_active=False)
    """
    repo = TransactionRepository(db)
    transaction = repo.get_by_id(transaction_id)

    if not transaction:
        raise HTTPException(
            status_code=404, detail=f"Transaction with ID {transaction_id} not found"
        )

    if hard_delete:
        repo.hard_delete(transaction)
    else:
        repo.soft_delete(transaction)

    return None
