"""
Pydantic schemas for ImportTemplate API
These are DTOs (Data Transfer Objects) for request/response validation
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from models.base import FileFormat


class ColumnMappings(BaseModel):
    """Schema for column mappings configuration"""

    transaction_date: str | None = Field(None, description="Column name for transaction date")
    posted_date: str | None = Field(None, description="Column name for posted date")
    description: str | None = Field(None, description="Column name for description")
    amount: str | None = Field(None, description="Column name for amount (single column)")
    category: str | None = Field(None, description="Column name for bank category")
    debit: str | None = Field(None, description="Column name for debit amount (split columns)")
    credit: str | None = Field(None, description="Column name for credit amount (split columns)")


class AmountConfig(BaseModel):
    """Schema for amount configuration"""

    sign_convention: str = Field(
        ...,
        description="Sign convention: bank_standard, inverted, split_columns, amount_with_type_column",
    )
    debit_column: str | None = Field(None, description="Column name for debit (split_columns)")
    credit_column: str | None = Field(None, description="Column name for credit (split_columns)")
    debit_indicator: str | None = Field(
        None, description="Value indicating debit (amount_with_type_column)"
    )
    credit_indicator: str | None = Field(
        None, description="Value indicating credit (amount_with_type_column)"
    )
    decimal_places: int = Field(2, description="Number of decimal places in source data")


class ImportTemplateBase(BaseModel):
    """Shared fields"""

    template_name: str = Field(..., min_length=1, max_length=100)
    institution_id: int
    file_format: FileFormat
    column_mappings: dict[str, Any]
    amount_config: dict[str, Any]
    header_row: int = Field(1, ge=1)
    skip_rows: int = Field(0, ge=0)
    date_format: str = Field("%m/%d/%Y", max_length=50)
    is_active: bool = True


class ImportTemplateCreate(ImportTemplateBase):
    """Schema for creating an import template"""

    pass


class ImportTemplateUpdate(BaseModel):
    """Schema for updating an import template - all fields optional"""

    template_name: str | None = Field(None, min_length=1, max_length=100)
    institution_id: int | None = None
    file_format: FileFormat | None = None
    column_mappings: dict[str, Any] | None = None
    amount_config: dict[str, Any] | None = None
    header_row: int | None = Field(None, ge=1)
    skip_rows: int | None = Field(None, ge=0)
    date_format: str | None = Field(None, max_length=50)
    is_active: bool | None = None


class ImportTemplateResponse(ImportTemplateBase):
    """Schema for returning an import template"""

    template_id: int
    created_at: datetime
    modified_at: datetime

    class Config:
        from_attributes = True
