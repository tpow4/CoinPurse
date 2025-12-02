"""
API endpoints for Accounts
Handles all HTTP routes for account management
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.account import Account
from repositories.account_repository import AccountRepository
from repositories.institution_repository import InstitutionRepository
from schemas.account import AccountCreate, AccountResponse, AccountUpdate

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=AccountResponse, status_code=201)
def create_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new account

    - **account_name**: Name of the account (required)
    - **institution_id**: ID of the institution this account belongs to (required)
    - **account_type**: Type of account (checking, credit_card, savings, etc.) (required)
    - **account_subtype**: Subtype of account (optional)
    - **last_4_digits**: Last 4 digits of the account number (required)
    - **tracks_transactions**: Whether this account tracks transactions (default: False)
    - **tracks_balances**: Whether this account tracks balances (default: False)
    - **active**: Whether the account is active (default: True)
    - **display_order**: Display order for sorting (default: 0)
    """
    repo = AccountRepository(db)
    institution_repo = InstitutionRepository(db)

    # Validate institution exists
    if not institution_repo.exists(account_data.institution_id):
        raise HTTPException(
            status_code=400,
            detail=f"Institution with ID {account_data.institution_id} not found"
        )

    # Check if name already exists
    if repo.name_exists(account_data.account_name):
        raise HTTPException(
            status_code=400,
            detail=f"Account with name '{account_data.account_name}' already exists"
        )

    db_account = Account(**account_data.model_dump())

    created = repo.create(db_account)

    return created


@router.get("/", response_model=List[AccountResponse])
def list_accounts(
    include_inactive: bool = Query(False, description="Include inactive accounts"),
    institution_id: int | None = Query(None, description="Filter by institution ID"),
    db: Session = Depends(get_db)
):
    """
    Get all accounts

    - **include_inactive**: Set to true to include inactive accounts
    - **institution_id**: Optional filter by institution ID
    """
    repo = AccountRepository(db)

    if institution_id is not None:
        return repo.get_by_institution(institution_id, include_inactive=include_inactive)

    return repo.get_all(include_inactive=include_inactive)


@router.get("/search", response_model=List[AccountResponse])
def search_accounts(
    q: str = Query(..., min_length=1, description="Search term"),
    db: Session = Depends(get_db)
):
    """
    Search accounts by name (case-insensitive partial match)

    - **q**: Search term to match against account names
    """
    repo = AccountRepository(db)
    return repo.search_by_name(q)


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific account by ID

    - **account_id**: The ID of the account to retrieve
    """
    repo = AccountRepository(db)
    account = repo.get_by_id(account_id)

    if not account:
        raise HTTPException(
            status_code=404,
            detail=f"Account with ID {account_id} not found"
        )

    return account


@router.patch("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    account_data: AccountUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an account

    - **account_id**: The ID of the account to update
    - **account_name**: New name (optional)
    - **institution_id**: New institution ID (optional)
    - **account_type**: New account type (optional)
    - **account_subtype**: New account subtype (optional)
    - **last_4_digits**: New last 4 digits (optional)
    - **tracks_transactions**: New tracks_transactions value (optional)
    - **tracks_balances**: New tracks_balances value (optional)
    - **active**: New active status (optional)
    - **display_order**: New display order (optional)
    """
    repo = AccountRepository(db)
    account = repo.get_by_id(account_id)

    if not account:
        raise HTTPException(
            status_code=404,
            detail=f"Account with ID {account_id} not found"
        )

    # Validate institution exists if being updated
    if account_data.institution_id is not None:
        institution_repo = InstitutionRepository(db)
        if not institution_repo.exists(account_data.institution_id):
            raise HTTPException(
                status_code=400,
                detail=f"Institution with ID {account_data.institution_id} not found"
            )

    # Check if new name conflicts with existing account
    if account_data.account_name:
        if repo.name_exists(account_data.account_name, exclude_id=account_id):
            raise HTTPException(
                status_code=400,
                detail=f"Account with name '{account_data.account_name}' already exists"
            )

    # Update only provided fields
    update_data = account_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)

    return repo.update(account)


@router.delete("/{account_id}", status_code=204)
def delete_account(
    account_id: int,
    hard_delete: bool = Query(False, description="Permanently delete (use with caution)"),
    db: Session = Depends(get_db)
):
    """
    Delete an account (soft delete by default)

    - **account_id**: The ID of the account to delete
    - **hard_delete**: If true, permanently deletes. Otherwise, soft deletes (sets active=False)
    """
    repo = AccountRepository(db)
    account = repo.get_by_id(account_id)

    if not account:
        raise HTTPException(
            status_code=404,
            detail=f"Account with ID {account_id} not found"
        )

    if hard_delete:
        repo.hard_delete(account)
    else:
        repo.soft_delete(account)

    return None
