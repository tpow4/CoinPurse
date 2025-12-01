"""
API endpoints for Account Balances
Handles all HTTP routes for balance management
"""
from typing import List
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.balance import AccountBalance
from repositories.balance_repository import BalanceRepository
from repositories.account_repository import AccountRepository
from schemas.balance import BalanceCreate, BalanceResponse, BalanceUpdate

router = APIRouter(prefix="/balances", tags=["balances"])


@router.post("/", response_model=BalanceResponse, status_code=201)
def create_balance(
    balance_data: BalanceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new balance record

    - **account_id**: ID of the account this balance belongs to (required)
    - **balance**: Balance amount in cents (required)
    - **balance_date**: Date of the balance snapshot (required)
    - **notes**: Optional notes about this balance
    - **is_active**: Whether the balance is active (default: True)
    """
    repo = BalanceRepository(db)
    account_repo = AccountRepository(db)

    # Validate account exists
    if not account_repo.exists(balance_data.account_id):
        raise HTTPException(
            status_code=400,
            detail=f"Account with ID {balance_data.account_id} not found"
        )

    # Check if balance already exists for this account and date (unique constraint)
    if repo.exists_for_account_and_date(balance_data.account_id, balance_data.balance_date):
        raise HTTPException(
            status_code=400,
            detail=f"Balance for account {balance_data.account_id} on date {balance_data.balance_date} already exists"
        )

    db_balance = AccountBalance(**balance_data.model_dump())

    created = repo.create(db_balance)

    return created


@router.get("/", response_model=List[BalanceResponse])
def list_balances(
    account_id: int | None = Query(None, description="Filter by account ID"),
    start_date: date | None = Query(None, description="Start date (inclusive)"),
    end_date: date | None = Query(None, description="End date (inclusive)"),
    include_inactive: bool = Query(False, description="Include inactive balances"),
    db: Session = Depends(get_db)
):
    """
    Get all balances with optional filters

    - **account_id**: Optional filter by account ID
    - **start_date**: Optional start date filter (inclusive)
    - **end_date**: Optional end date filter (inclusive)
    - **include_inactive**: Set to true to include inactive balances
    """
    repo = BalanceRepository(db)

    # If date range or account filter specified, use filtered query
    if account_id is not None or start_date is not None or end_date is not None:
        return repo.get_by_date_range(
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
            include_inactive=include_inactive
        )

    return repo.get_all(include_inactive=include_inactive)


@router.get("/latest/{account_id}", response_model=BalanceResponse)
def get_latest_balance(
    account_id: int,
    include_inactive: bool = Query(False, description="Include inactive balances"),
    db: Session = Depends(get_db)
):
    """
    Get the most recent balance for a specific account

    - **account_id**: The ID of the account
    - **include_inactive**: Set to true to include inactive balances
    """
    repo = BalanceRepository(db)
    balance = repo.get_latest_by_account(account_id, include_inactive=include_inactive)

    if not balance:
        raise HTTPException(
            status_code=404,
            detail=f"No balances found for account with ID {account_id}"
        )

    return balance


@router.get("/{balance_id}", response_model=BalanceResponse)
def get_balance(
    balance_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific balance by ID

    - **balance_id**: The ID of the balance to retrieve
    """
    repo = BalanceRepository(db)
    balance = repo.get_by_id(balance_id)

    if not balance:
        raise HTTPException(
            status_code=404,
            detail=f"Balance with ID {balance_id} not found"
        )

    return balance


@router.patch("/{balance_id}", response_model=BalanceResponse)
def update_balance(
    balance_id: int,
    balance_data: BalanceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a balance

    - **balance_id**: The ID of the balance to update
    - **account_id**: New account ID (optional)
    - **balance**: New balance amount in cents (optional)
    - **balance_date**: New date (optional)
    - **notes**: New notes (optional)
    - **is_active**: New active status (optional)
    """
    repo = BalanceRepository(db)
    balance = repo.get_by_id(balance_id)

    if not balance:
        raise HTTPException(
            status_code=404,
            detail=f"Balance with ID {balance_id} not found"
        )

    # Validate account exists if being updated
    if balance_data.account_id is not None:
        account_repo = AccountRepository(db)
        if not account_repo.exists(balance_data.account_id):
            raise HTTPException(
                status_code=400,
                detail=f"Account with ID {balance_data.account_id} not found"
            )

    # Check unique constraint if account_id or balance_date is being updated
    check_account_id = balance_data.account_id if balance_data.account_id is not None else balance.account_id
    check_date = balance_data.balance_date if balance_data.balance_date is not None else balance.balance_date

    if repo.exists_for_account_and_date(check_account_id, check_date, exclude_id=balance_id):
        raise HTTPException(
            status_code=400,
            detail=f"Balance for account {check_account_id} on date {check_date} already exists"
        )

    # Update only provided fields
    update_data = balance_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(balance, field, value)

    return repo.update(balance)


@router.delete("/{balance_id}", status_code=204)
def delete_balance(
    balance_id: int,
    hard_delete: bool = Query(False, description="Permanently delete (use with caution)"),
    db: Session = Depends(get_db)
):
    """
    Delete a balance (soft delete by default)

    - **balance_id**: The ID of the balance to delete
    - **hard_delete**: If true, permanently deletes. Otherwise, soft deletes (sets is_active=False)
    """
    repo = BalanceRepository(db)
    balance = repo.get_by_id(balance_id)

    if not balance:
        raise HTTPException(
            status_code=404,
            detail=f"Balance with ID {balance_id} not found"
        )

    if hard_delete:
        repo.hard_delete(balance)
    else:
        repo.soft_delete(balance)

    return None
