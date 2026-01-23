"""
Pydantic schemas for Institution API
These are DTOs (Data Transfer Objects) for request/response validation
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InstitutionBase(BaseModel):
    """Shared fields"""

    name: str = Field(..., min_length=1, max_length=100)


class InstitutionCreate(InstitutionBase):
    """Schema for creating an institution (what user sends)"""

    is_active: bool = True  # Optional with default value


class InstitutionUpdate(BaseModel):
    """Schema for updating an institution - all fields optional"""

    name: str | None = Field(None, min_length=1, max_length=100)
    is_active: bool | None = None


class InstitutionResponse(InstitutionBase):
    """Schema for returning an institution (what API sends back)"""

    # Allow pydantic to work with SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)

    institution_id: int
    is_active: bool
    created_at: datetime
    modified_at: datetime

