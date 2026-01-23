"""
Pydantic schemas for Account API
These are DTOs (Data Transfer Objects) for request/response validation
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.base import AccountType, TaxTreatmentType


class AccountBase(BaseModel):
    """Shared fields"""

    account_name: str = Field(..., min_length=1, max_length=100)
    institution_id: int
    account_type: AccountType
    tax_treatment: TaxTreatmentType
    last_4_digits: str = Field(..., min_length=4, max_length=4, pattern=r"^\d{4}$")
    tracks_transactions: bool = False
    tracks_balances: bool = False
    active: bool = True
    display_order: int = 0


class AccountCreate(AccountBase):
    """Schema for creating an account (what user sends)"""

    pass  # No additional fields needed for creation


class AccountUpdate(BaseModel):
    """Schema for updating an account - all fields optional"""

    account_name: str | None = Field(None, min_length=1, max_length=100)
    institution_id: int | None = None
    account_type: AccountType | None = None
    tax_treatment: TaxTreatmentType | None = None
    last_4_digits: str | None = Field(
        None, min_length=4, max_length=4, pattern=r"^\d{4}$"
    )
    tracks_transactions: bool | None = None
    tracks_balances: bool | None = None
    active: bool | None = None
    display_order: int | None = None


class AccountResponse(AccountBase):
    """Schema for returning an account (what API sends back)"""

    # Allow pydantic to work with SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    created_at: datetime
    modified_at: datetime

