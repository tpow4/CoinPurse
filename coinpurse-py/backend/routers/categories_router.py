"""
API endpoints for Categories
Handles all HTTP routes for category management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.category import Category
from repositories.category_repository import CategoryRepository
from schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    """
    Create a new category

    - **name**: Name of the category (required)
    - **is_active**: Whether the category is active (default: True)
    """
    repo = CategoryRepository(db)

    # Check if name already exists
    if repo.name_exists(category_data.name):
        raise HTTPException(
            status_code=400,
            detail=f"Category with name '{category_data.name}' already exists",
        )

    db_category = Category(**category_data.model_dump())

    created = repo.create(db_category)

    return created


@router.get("/", response_model=list[CategoryResponse])
def list_categories(
    include_inactive: bool = Query(False, description="Include inactive categories"),
    db: Session = Depends(get_db),
):
    """
    Get all categories

    - **include_inactive**: Set to true to include inactive categories
    """
    repo = CategoryRepository(db)
    return repo.get_all(include_inactive=include_inactive)


@router.get("/search", response_model=list[CategoryResponse])
def search_categories(
    q: str = Query(..., min_length=1, description="Search term"),
    include_inactive: bool = Query(False, description="Include inactive categories"),
    db: Session = Depends(get_db),
):
    """
    Search categories by name (case-insensitive partial match)

    - **q**: Search term to match against category names
    - **include_inactive**: Set to true to include inactive categories
    """
    repo = CategoryRepository(db)
    return repo.search_by_name(q, include_inactive=include_inactive)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Get a specific category by ID

    - **category_id**: The ID of the category to retrieve
    """
    repo = CategoryRepository(db)
    category = repo.get_by_id(category_id)

    if not category:
        raise HTTPException(
            status_code=404, detail=f"Category with ID {category_id} not found"
        )

    return category


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int, category_data: CategoryUpdate, db: Session = Depends(get_db)
):
    """
    Update a category

    - **category_id**: The ID of the category to update
    - **name**: New name (optional)
    - **is_active**: New active status (optional)
    """
    repo = CategoryRepository(db)
    category = repo.get_by_id(category_id)

    if not category:
        raise HTTPException(
            status_code=404, detail=f"Category with ID {category_id} not found"
        )

    # Check if new name conflicts with existing category
    if category_data.name:
        if repo.name_exists(category_data.name, exclude_id=category_id):
            raise HTTPException(
                status_code=400,
                detail=f"Category with name '{category_data.name}' already exists",
            )

    # Update only provided fields
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    return repo.update(category)


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    hard_delete: bool = Query(
        False, description="Permanently delete (use with caution)"
    ),
    db: Session = Depends(get_db),
):
    """
    Delete a category (soft delete by default)

    - **category_id**: The ID of the category to delete
    - **hard_delete**: If true, permanently deletes. Otherwise, soft deletes (sets is_active=False)
    """
    repo = CategoryRepository(db)
    category = repo.get_by_id(category_id)

    if not category:
        raise HTTPException(
            status_code=404, detail=f"Category with ID {category_id} not found"
        )

    if hard_delete:
        repo.hard_delete(category)
    else:
        repo.soft_delete(category)

    return None
