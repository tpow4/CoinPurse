"""
API endpoints for Institutions
Handles all HTTP routes for institution management
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.institution import Institution
from respositories.institution_repository import InstitutionRepository
from schemas.institution import InstitutionCreate, InstitutionResponse, InstitutionUpdate

router = APIRouter(prefix="/institutions", tags=["institutions"])


@router.post("/", response_model=InstitutionResponse, status_code=201)
def create_institution(
    institution_data: InstitutionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new institution
    
    - **institution_name**: Name of the financial institution (required)
    """
    repo = InstitutionRepository(db)
    
    # Check if name already exists
    if repo.name_exists(institution_data.institution_name):
        raise HTTPException(
            status_code=400,
            detail=f"Institution with name '{institution_data.institution_name}' already exists"
        )
    
    db_institution = Institution(**institution_data.model_dump())
    
    created = repo.create(db_institution)
    
    return created


@router.get("/", response_model=List[InstitutionResponse])
def list_institutions(
    include_inactive: bool = Query(False, description="Include inactive institutions"),
    db: Session = Depends(get_db)
):
    """
    Get all institutions
    
    - **include_inactive**: Set to true to include inactive institutions
    """
    repo = InstitutionRepository(db)
    return repo.get_all(include_inactive=include_inactive)


@router.get("/search", response_model=List[InstitutionResponse])
def search_institutions(
    q: str = Query(..., min_length=1, description="Search term"),
    db: Session = Depends(get_db)
):
    """
    Search institutions by name (case-insensitive partial match)
    
    - **q**: Search term to match against institution names
    """
    repo = InstitutionRepository(db)
    return repo.search_by_name(q)


@router.get("/{institution_id}", response_model=InstitutionResponse)
def get_institution(
    institution_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific institution by ID
    
    - **institution_id**: The ID of the institution to retrieve
    """
    repo = InstitutionRepository(db)
    institution = repo.get_by_id(institution_id)
    
    if not institution:
        raise HTTPException(
            status_code=404,
            detail=f"Institution with ID {institution_id} not found"
        )
    
    return institution


@router.patch("/{institution_id}", response_model=InstitutionResponse)
def update_institution(
    institution_id: int,
    institution_data: InstitutionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an institution
    
    - **institution_id**: The ID of the institution to update
    - **name**: New name (optional)
    - **is_active**: New active status (optional)
    """
    repo = InstitutionRepository(db)
    institution = repo.get_by_id(institution_id)
    
    if not institution:
        raise HTTPException(
            status_code=404,
            detail=f"Institution with ID {institution_id} not found"
        )
    
    # Check if new name conflicts with existing institution
    if institution_data.name:
        if repo.name_exists(institution_data.name, exclude_id=institution_id):
            raise HTTPException(
                status_code=400,
                detail=f"Institution with name '{institution_data.institution_name}' already exists"
            )
    
    # Update only provided fields
    update_data = institution_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(institution, field, value)
    
    return repo.update(institution)


@router.delete("/{institution_id}", status_code=204)
def delete_institution(
    institution_id: int,
    hard_delete: bool = Query(False, description="Permanently delete (use with caution)"),
    db: Session = Depends(get_db)
):
    """
    Delete an institution (soft delete by default)
    
    - **institution_id**: The ID of the institution to delete
    - **hard_delete**: If true, permanently deletes. Otherwise, soft deletes (sets is_active=False)
    """
    repo = InstitutionRepository(db)
    institution = repo.get_by_id(institution_id)
    
    if not institution:
        raise HTTPException(
            status_code=404,
            detail=f"Institution with ID {institution_id} not found"
        )
    
    if hard_delete:
        repo.hard_delete(institution)
    else:
        repo.soft_delete(institution)
    
    return None