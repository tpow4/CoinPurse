"""
Pydantic schemas for ImportBatch API
These are DTOs (Data Transfer Objects) for request/response validation
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from models.base import FileFormat, ImportStatus


class ParsedTransaction(BaseModel):
    """Schema for a single parsed transaction in preview"""

    row_number: int
    transaction_date: date | None = None
    posted_date: date | None = None
    description: str
    amount: int  # Amount in cents
    transaction_type: str  # CREDIT or DEBIT
    category_name: str | None = None
    coinpurse_category_id: int | None = None
    candidate_category_ids: list[int] = Field(default_factory=list)
    is_duplicate: bool = False
    validation_errors: list[str] = Field(default_factory=list)


class ImportPreviewSummary(BaseModel):
    """Summary statistics for import preview"""

    total_rows: int
    valid_rows: int
    duplicate_count: int
    validation_errors: int


class ImportPreviewResponse(BaseModel):
    """Response from upload/preview endpoint"""

    # Allow pydantic to work with SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)

    import_batch_id: int
    summary: ImportPreviewSummary
    transactions: list[ParsedTransaction]


class ImportConfirmRequest(BaseModel):
    """Request to confirm an import"""

    import_batch_id: int
    selected_rows: list[int] = Field(..., description="Row numbers to import")
    category_overrides: dict[int, int] = Field(
        default_factory=dict,
        description="Map of row_number -> coinpurse_category_id",
    )


class ImportConfirmResponse(BaseModel):
    """Response from confirm endpoint"""

    # Allow pydantic to work with SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)

    import_batch_id: int
    imported_count: int
    skipped_count: int
    duplicate_count: int
    status: ImportStatus


class ImportBatchBase(BaseModel):
    """Shared fields"""

    account_id: int
    template_id: int | None = None
    file_name: str = Field(..., max_length=255)
    file_format: FileFormat


class ImportBatchResponse(ImportBatchBase):
    """Schema for returning an import batch"""

    # Allow pydantic to work with SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)

    import_batch_id: int
    total_rows: int
    imported_count: int
    skipped_count: int
    duplicate_count: int
    status: ImportStatus
    imported_at: datetime | None = None
    created_at: datetime
    modified_at: datetime


class ImportBatchDetailResponse(ImportBatchResponse):
    """Schema for returning an import batch with account/template names"""

    account_name: str | None = None
    template_name: str | None = None
