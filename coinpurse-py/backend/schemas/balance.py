"""
Pydantic schemas for AccountBalance API
These are DTOs (Data Transfer Objects) for request/response validation
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

BALANCE_DESCRIPTION = "Balance in cents"


class BalanceBase(BaseModel):
    """Shared fields"""

    account_id: int
    balance: int = Field(..., description=BALANCE_DESCRIPTION)
    balance_date: date
    notes: str | None = None
    is_active: bool = True


class BalanceCreate(BalanceBase):
    """Schema for creating a balance (what user sends)"""

    pass  # No additional fields needed for creation


class BalanceUpdate(BaseModel):
    """Schema for updating a balance - all fields optional"""

    account_id: int | None = None
    balance: int | None = Field(None, description=BALANCE_DESCRIPTION)
    balance_date: date | None = None
    notes: str | None = None
    is_active: bool | None = None


class BalanceResponse(BalanceBase):
    """Schema for returning a balance (what API sends back)"""

    # Allow pydantic to work with SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)

    balance_id: int
    created_at: datetime
    modified_at: datetime


class MonthlyBalancePoint(BaseModel):
    """Single month/balance data point"""

    balance_date: date = Field(..., description="End of month date")
    balance: int = Field(..., description=BALANCE_DESCRIPTION)


class AccountBalanceSeries(BaseModel):
    """Time series of monthly balances for one account"""

    account_id: int
    account_name: str
    institution_name: str
    account_type: str
    tax_treatment: str
    data: list[MonthlyBalancePoint]


class MonthlyBalanceAggregateResponse(BaseModel):
    """Aggregated monthly balance data for all accounts"""

    month_end_dates: list[date] = Field(
        ..., description="All end-of-month dates in the range"
    )
    series: list[AccountBalanceSeries] = Field(
        ..., description="Balance time series for each account"
    )


class BalanceEntry(BaseModel):
    """Single balance entry for batch operations"""

    balance_date: date
    balance: int = Field(..., description=BALANCE_DESCRIPTION)


class BalanceBatchCreate(BaseModel):
    """Schema for batch creating/updating balances"""

    account_id: int
    balances: list[BalanceEntry]


class BalanceBatchResponse(BaseModel):
    """Response from batch balance operation"""

    created: int
    updated: int
    balances: list[BalanceResponse]
