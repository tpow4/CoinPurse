"""
Pydantic schemas for CategoryMapping API
These are DTOs (Data Transfer Objects) for request/response validation
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryMappingBase(BaseModel):
    """Shared fields"""

    institution_id: int
    bank_category_name: str = Field(..., min_length=1, max_length=100)
    coinpurse_category_id: int
    priority: int = Field(1, ge=1)
    is_active: bool = True


class CategoryMappingCreate(CategoryMappingBase):
    """Schema for creating a category mapping"""

    pass


class CategoryMappingUpdate(BaseModel):
    """Schema for updating a category mapping - all fields optional"""

    institution_id: int | None = None
    bank_category_name: str | None = Field(None, min_length=1, max_length=100)
    coinpurse_category_id: int | None = None
    priority: int | None = Field(None, ge=1)
    is_active: bool | None = None


class CategoryMappingResponse(CategoryMappingBase):
    """Schema for returning a category mapping"""

    # Allow pydantic to work with SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)

    mapping_id: int
    created_at: datetime
    modified_at: datetime


class CategoryMappingWithNames(CategoryMappingResponse):
    """Schema for returning a category mapping with resolved names"""

    institution_name: str | None = None
    coinpurse_category_name: str | None = None


class CategoryMappingGroupSave(BaseModel):
    """Schema for batch-saving a mapping group (all mappings for one bank category name)"""

    institution_id: int
    bank_category_name: str = Field(..., min_length=1, max_length=100)
    coinpurse_category_ids: list[int] = Field(..., min_length=1)
    old_bank_category_name: str | None = Field(
        None, min_length=1, max_length=100, description="Previous name if renaming"
    )


class CategoryMappingGroupDelete(BaseModel):
    """Schema for deleting all mappings in a group"""

    institution_id: int
    bank_category_name: str = Field(..., min_length=1, max_length=100)
