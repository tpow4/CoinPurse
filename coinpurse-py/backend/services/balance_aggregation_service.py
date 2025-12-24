"""
Balance Aggregation Service
Handles normalization of balance data into monthly snapshots with forward-fill
"""
from datetime import date, datetime, timezone
from calendar import monthrange
from typing import List, Dict, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from models.account import Account
from models.balance import AccountBalance
from repositories.balance_repository import BalanceRepository


def get_last_day_of_month(d: date) -> date:
    """Get the last day of the month for a given date."""
    last_day = monthrange(d.year, d.month)[1]
    return date(d.year, d.month, last_day)


def generate_month_end_dates(start_date: date, end_date: date) -> List[date]:
    """
    Generate a list of end-of-month dates between start_date and end_date (inclusive).

    Args:
        start_date: The starting date
        end_date: The ending date

    Returns:
        List of end-of-month dates
    """
    if start_date > end_date:
        return []

    month_ends = []
    current = get_last_day_of_month(start_date)
    end = get_last_day_of_month(end_date)

    while current <= end:
        month_ends.append(current)

        # Move to next month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

        current = get_last_day_of_month(current)

    return month_ends


def forward_fill_monthly_balances(
    balances: List[AccountBalance],
    month_dates: List[date]
) -> List[Dict]:
    """
    Apply forward-fill algorithm to create monthly balance snapshots.

    For each month:
    - Use the latest balance from that month if available
    - Otherwise, forward-fill from the previous month
    - If before first balance, return None (account didn't exist yet)

    Args:
        balances: List of AccountBalance records sorted by balance_date
        month_dates: List of end-of-month dates to generate snapshots for

    Returns:
        List of dicts with 'balance_date' and 'balance' keys
    """
    if not balances:
        return []

    # Sort balances by date to ensure correct order
    sorted_balances = sorted(balances, key=lambda b: b.balance_date)

    result = []
    last_known_balance = None
    balance_idx = 0

    for month_end in month_dates:
        # Advance through balances until we've seen all balances up to and including this month
        while balance_idx < len(sorted_balances) and sorted_balances[balance_idx].balance_date <= month_end:
            last_known_balance = sorted_balances[balance_idx].balance
            balance_idx += 1

        # If we have a known balance at this point, use it (forward-filled if necessary)
        if last_known_balance is not None:
            result.append({
                'balance_date': month_end,
                'balance': last_known_balance
            })

    return result


def get_aggregated_monthly_data(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    include_inactive_accounts: bool = False
) -> Dict:
    """
    Get aggregated monthly balance data for all accounts.

    Returns data in format:
    {
        'month_end_dates': [list of end-of-month dates],
        'series': [
            {
                'account_id': int,
                'account_name': str,
                'institution_name': str,
                'account_type': str,
                'data': [{'balance_date': date, 'balance': int}, ...]
            },
            ...
        ]
    }

    Args:
        db: Database session
        start_date: Optional start date (defaults to earliest balance date)
        end_date: Optional end date (defaults to end of current month)
        include_inactive_accounts: Whether to include inactive accounts

    Returns:
        Dictionary with 'month_end_dates' and 'series' keys
    """
    balance_repo = BalanceRepository(db)

    # Query accounts that track balances (with institution eagerly loaded)
    accounts_query = (
        select(Account)
        .options(joinedload(Account.institution))
        .where(Account.tracks_balances == True)
    )
    if not include_inactive_accounts:
        accounts_query = accounts_query.where(Account.active == True)
    accounts = list(db.scalars(accounts_query))

    if not accounts:
        return {'month_end_dates': [], 'series': []}

    # Get all balances for these accounts
    account_ids = [acc.account_id for acc in accounts]
    all_balances = balance_repo.get_all(include_inactive=False)

    # Filter balances to only those belonging to our accounts
    account_balances = [b for b in all_balances if b.account_id in account_ids]

    # Determine date range
    if not account_balances:
        return {'month_end_dates': [], 'series': []}

    if start_date is None:
        start_date = min(b.balance_date for b in account_balances)

    if end_date is None:
        today = datetime.now(timezone.utc).date()
        end_date = get_last_day_of_month(today)

    # Generate month-end dates
    month_dates = generate_month_end_dates(start_date, end_date)

    if not month_dates:
        return {'month_end_dates': [], 'series': []}

    # Group balances by account
    balances_by_account: Dict[int, List[AccountBalance]] = {}
    for balance in account_balances:
        balances_by_account.setdefault(balance.account_id, []).append(balance)

    # Build series data for each account
    series = []
    for account in accounts:
        account_balance_list = balances_by_account.get(account.account_id, [])

        # Apply forward-fill to get monthly snapshots
        monthly_data = forward_fill_monthly_balances(account_balance_list, month_dates)

        # Only include accounts that have at least one data point
        if monthly_data:
            series.append({
                'account_id': account.account_id,
                'account_name': account.account_name,
                'institution_name': account.institution.name if account.institution else 'Unknown',
                'account_type': account.account_type.value,
                'data': monthly_data
            })

    return {
        'month_end_dates': month_dates,
        'series': series
    }
