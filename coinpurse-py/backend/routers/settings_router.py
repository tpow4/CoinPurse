"""
Router for application settings and balance check-in reminders
"""

from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models.account import Account
from repositories.app_setting_repository import AppSettingRepository
from repositories.balance_repository import BalanceRepository
from schemas.app_setting import AccountDueForCheckin, AppSettingResponse, AppSettingUpdate

router = APIRouter(prefix="/settings", tags=["settings"])

DEFAULT_FREQUENCY_DAYS = 7


@router.get("/", response_model=list[AppSettingResponse])
def list_settings(db: Session = Depends(get_db)):
    """Get all application settings"""
    repo = AppSettingRepository(db)
    return repo.get_all()


@router.get("/balance-checkin/due", response_model=list[AccountDueForCheckin])
def get_accounts_due_for_checkin(db: Session = Depends(get_db)):
    """Get accounts that are due for a balance check-in"""
    settings_repo = AppSettingRepository(db)
    balance_repo = BalanceRepository(db)

    # Get frequency setting
    setting = settings_repo.get_by_key("balance_checkin_frequency_days")
    frequency_days = int(setting.setting_value) if setting else DEFAULT_FREQUENCY_DAYS

    # Query active accounts that track balances
    accounts_query = (
        select(Account)
        .options(joinedload(Account.institution))
        .where(Account.tracks_balances == True)
        .where(Account.active == True)
    )
    accounts = list(db.scalars(accounts_query))

    today = datetime.now(UTC).date()
    due_accounts: list[AccountDueForCheckin] = []

    for account in accounts:
        latest_balance = balance_repo.get_latest_by_account(account.account_id)
        institution_name = account.institution.name if account.institution else "Unknown"

        if latest_balance is None:
            # Never had a balance entered
            due_accounts.append(
                AccountDueForCheckin(
                    account_id=account.account_id,
                    account_name=account.account_name,
                    institution_name=institution_name,
                    last_balance_date=None,
                    days_since_last=None,
                )
            )
        else:
            balance_date = latest_balance.balance_date
            if isinstance(balance_date, datetime):
                balance_date = balance_date.date()
            days_since = (today - balance_date).days
            if days_since >= frequency_days:
                due_accounts.append(
                    AccountDueForCheckin(
                        account_id=account.account_id,
                        account_name=account.account_name,
                        institution_name=institution_name,
                        last_balance_date=balance_date.isoformat(),
                        days_since_last=days_since,
                    )
                )

    return due_accounts


@router.get("/{setting_key}", response_model=AppSettingResponse)
def get_setting(setting_key: str, db: Session = Depends(get_db)):
    """Get a specific setting by key"""
    repo = AppSettingRepository(db)
    setting = repo.get_by_key(setting_key)
    if not setting:
        raise HTTPException(status_code=404, detail=f"Setting '{setting_key}' not found")
    return setting


@router.put("/{setting_key}", response_model=AppSettingResponse)
def upsert_setting(
    setting_key: str, setting_data: AppSettingUpdate, db: Session = Depends(get_db)
):
    """Create or update a setting"""
    repo = AppSettingRepository(db)
    return repo.upsert(setting_key, setting_data.setting_value)
