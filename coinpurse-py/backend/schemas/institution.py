from pydantic import BaseModel, Field
from datetime import datetime

class InstitutionBase(BaseModel):
    """Shared fields"""
    name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True

class InstitutionCreate(InstitutionBase):
    """Schema for creating an institution (what user sends)"""
    pass

class InstitutionResponse(InstitutionBase):
    """Schema for returning an institution (what API sends back)"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        # Allows Pydantic to work with SQLAlchemy models
        from_attributes = True  