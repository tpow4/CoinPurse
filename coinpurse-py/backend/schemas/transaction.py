"""
Pydantic schemas for Transaction API
These are DTOs (Data Transfer Objects) for request/response validation
"""

from datetime import date, datetime

from pydantic import BaseModel, Field

from models.base import TransactionType


class TransactionBase(BaseModel):
    """Shared fields"""

    account_id: int
    category_id: int
    transaction_date: date
    posted_date: date
    amount: int = Field(..., description="Transaction amount in cents")
    description: str = Field(..., min_length=1, max_length=500)
    transaction_type: TransactionType
    notes: str = ""
    is_active: bool = True


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction (what user sends)"""

    pass  # No additional fields needed for creation


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction - all fields optional"""

    account_id: int | None = None
    category_id: int | None = None
    transaction_date: date | None = None
    posted_date: date | None = None
    amount: int | None = Field(None, description="Transaction amount in cents")
    description: str | None = Field(None, min_length=1, max_length=500)
    transaction_type: TransactionType | None = None
    notes: str | None = None
    is_active: bool | None = None


class TransactionResponse(TransactionBase):
    """Schema for returning a transaction (what API sends back)"""

    transaction_id: int
    created_at: datetime
    modified_at: datetime

    class Config:
        """Pydantic configuration"""

        # Allows Pydantic to work with SQLAlchemy models
        from_attributes = True
