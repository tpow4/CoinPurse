"""
Pydantic schemas for Category API
These are DTOs (Data Transfer Objects) for request/response validation
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """Shared fields"""

    name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class CategoryCreate(CategoryBase):
    """Schema for creating a category (what user sends)"""

    pass  # No additional fields needed for creation


class CategoryUpdate(BaseModel):
    """Schema for updating a category - all fields optional"""

    name: str | None = Field(None, min_length=1, max_length=100)
    is_active: bool | None = None


class CategoryResponse(CategoryBase):
    """Schema for returning a category (what API sends back)"""

    # Allow pydantic to work with SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    created_at: datetime

