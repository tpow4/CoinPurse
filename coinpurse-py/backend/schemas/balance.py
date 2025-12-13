"""
Pydantic schemas for AccountBalance API
These are DTOs (Data Transfer Objects) for request/response validation
"""
from datetime import datetime, date
from pydantic import BaseModel, Field


class BalanceBase(BaseModel):
    """Shared fields"""
    account_id: int
    balance: int = Field(..., description="Balance in cents")
    balance_date: date
    notes: str | None = None
    is_active: bool = True


class BalanceCreate(BalanceBase):
    """Schema for creating a balance (what user sends)"""
    pass  # No additional fields needed for creation


class BalanceUpdate(BaseModel):
    """Schema for updating a balance - all fields optional"""
    account_id: int | None = None
    balance: int | None = Field(None, description="Balance in cents")
    balance_date: date | None = None
    notes: str | None = None
    is_active: bool | None = None


class BalanceResponse(BalanceBase):
    """Schema for returning a balance (what API sends back)"""
    balance_id: int
    created_at: datetime
    modified_at: datetime

    class Config:
        """Pydantic configuration"""
        # Allows Pydantic to work with SQLAlchemy models
        from_attributes = True
