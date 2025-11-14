"""
Pydantic schemas for Institution API
These are DTOs (Data Transfer Objects) for request/response validation
"""
from datetime import datetime
from pydantic import BaseModel, Field

class InstitutionBase(BaseModel):
    """Shared fields"""
    name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True

class InstitutionCreate(InstitutionBase):
    """Schema for creating an institution (what user sends)"""
    pass # No additional fields needed for creation


class InstitutionUpdate(BaseModel):
    """Schema for updating an institution - all fields optional"""
    name: str | None = Field(None, min_length=1, max_length=100)
    is_active: bool | None = None

class InstitutionResponse(InstitutionBase):
    """Schema for returning an institution (what API sends back)"""
    id: int
    created_at: datetime
    updated_at: datetime
    
class Config:
    """Pydantic configuration"""
    # Allows Pydantic to work with SQLAlchemy models
    from_attributes = True  