"""
API endpoints for Transaction Import
Handles file upload, preview, confirmation, and template/mapping management
"""

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from models import CategoryMapping, ImportTemplate
from repositories.category_mapping_repository import CategoryMappingRepository
from repositories.import_batch_repository import ImportBatchRepository
from repositories.import_template_repository import ImportTemplateRepository
from schemas.category_mapping import (
    CategoryMappingCreate,
    CategoryMappingResponse,
    CategoryMappingUpdate,
)
from schemas.import_batch import (
    ImportBatchDetailResponse,
    ImportBatchResponse,
    ImportConfirmRequest,
    ImportConfirmResponse,
    ImportPreviewResponse,
)
from schemas.import_template import (
    ImportTemplateCreate,
    ImportTemplateResponse,
    ImportTemplateUpdate,
)
from services import ImportService

router = APIRouter(prefix="/import", tags=["import"])


# =============================================================================
# Import Operations
# =============================================================================


@router.post("/upload", response_model=ImportPreviewResponse)
async def upload_and_preview(
    file: UploadFile = File(..., description="CSV or Excel file to import"),
    account_id: int = Form(..., description="Target account ID"),
    template_id: int = Form(..., description="Import template ID to use"),
    db: Session = Depends(get_db),
):
    """
    Upload a file and preview transactions before importing.

    - **file**: The CSV or Excel file to import
    - **account_id**: The account to import transactions into
    - **template_id**: The import template that defines how to parse the file

    Returns a preview with:
    - import_batch_id: Use this to confirm the import
    - summary: Counts of total, valid, duplicate, and error rows
    - transactions: List of parsed transactions with validation status
    """
    service = ImportService(db)

    try:
        # Read file contents
        contents = await file.read()
        import io

        file_obj = io.BytesIO(contents)

        result = service.upload_and_preview(
            file=file_obj,
            file_name=file.filename or "unknown",
            account_id=account_id,
            template_id=template_id,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/confirm", response_model=ImportConfirmResponse)
def confirm_import(
    request: ImportConfirmRequest,
    db: Session = Depends(get_db),
):
    """
    Confirm and execute an import for selected rows.

    - **import_batch_id**: The batch ID from the preview response
    - **selected_rows**: List of row numbers to import (from preview)

    Only rows that are valid and not duplicates will be imported.
    """
    service = ImportService(db)

    try:
        result = service.confirm_import(
            import_batch_id=request.import_batch_id,
            selected_rows=request.selected_rows,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error confirming import: {str(e)}")


# =============================================================================
# Import Batch History
# =============================================================================


@router.get("/batches", response_model=list[ImportBatchResponse])
def list_batches(
    account_id: int | None = Query(None, description="Filter by account ID"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of batches"),
    db: Session = Depends(get_db),
):
    """
    Get import batch history.

    - **account_id**: Optional filter by account
    - **limit**: Maximum number of batches to return (default: 100)
    """
    repo = ImportBatchRepository(db)

    if account_id:
        return repo.get_by_account(account_id, limit=limit)
    return repo.get_all(limit=limit)


@router.get("/batches/{import_batch_id}", response_model=ImportBatchDetailResponse)
def get_batch(import_batch_id: int, db: Session = Depends(get_db)):
    """
    Get details for a specific import batch.

    - **import_batch_id**: The batch ID to retrieve
    """
    repo = ImportBatchRepository(db)
    batch = repo.get_by_id(import_batch_id)

    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch {import_batch_id} not found")

    # Build response with related names
    response = ImportBatchDetailResponse(
        import_batch_id=batch.import_batch_id,
        account_id=batch.account_id,
        template_id=batch.template_id,
        file_name=batch.file_name,
        file_format=batch.file_format,
        total_rows=batch.total_rows,
        imported_count=batch.imported_count,
        skipped_count=batch.skipped_count,
        duplicate_count=batch.duplicate_count,
        status=batch.status,
        imported_at=batch.imported_at,
        created_at=batch.created_at,
        modified_at=batch.modified_at,
        account_name=batch.account.account_name if batch.account else None,
        template_name=batch.template.template_name if batch.template else None,
    )
    return response


# =============================================================================
# Import Templates
# =============================================================================


@router.get("/templates", response_model=list[ImportTemplateResponse])
def list_templates(
    institution_id: int | None = Query(None, description="Filter by institution ID"),
    include_inactive: bool = Query(False, description="Include inactive templates"),
    db: Session = Depends(get_db),
):
    """
    Get all import templates.

    - **institution_id**: Optional filter by institution
    - **include_inactive**: Include inactive templates
    """
    repo = ImportTemplateRepository(db)

    if institution_id:
        return repo.get_by_institution(institution_id, include_inactive=include_inactive)
    return repo.get_all(include_inactive=include_inactive)


@router.get("/templates/{template_id}", response_model=ImportTemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """
    Get a specific import template.

    - **template_id**: The template ID to retrieve
    """
    repo = ImportTemplateRepository(db)
    template = repo.get_by_id(template_id)

    if not template:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")

    return template


@router.post("/templates", response_model=ImportTemplateResponse, status_code=201)
def create_template(
    template_data: ImportTemplateCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new import template.

    - **template_name**: Name for the template
    - **institution_id**: Associated institution ID
    - **file_format**: CSV or EXCEL
    - **column_mappings**: JSON mapping internal fields to file columns
    - **amount_config**: JSON config for amount parsing
    - **date_format**: strptime format string (default: %m/%d/%Y)
    - **header_row**: Row number where headers are (1-indexed)
    - **skip_rows**: Rows to skip after header
    """
    repo = ImportTemplateRepository(db)

    # Check for duplicate name
    if repo.name_exists(template_data.template_name):
        raise HTTPException(
            status_code=400,
            detail=f"Template '{template_data.template_name}' already exists",
        )

    template = ImportTemplate(**template_data.model_dump())
    return repo.create(template)


@router.patch("/templates/{template_id}", response_model=ImportTemplateResponse)
def update_template(
    template_id: int,
    template_data: ImportTemplateUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an import template.

    - **template_id**: The template ID to update
    - All fields are optional
    """
    repo = ImportTemplateRepository(db)
    template = repo.get_by_id(template_id)

    if not template:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")

    # Check for name conflict
    if template_data.template_name:
        if repo.name_exists(template_data.template_name, exclude_id=template_id):
            raise HTTPException(
                status_code=400,
                detail=f"Template '{template_data.template_name}' already exists",
            )

    # Update only provided fields
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    return repo.update(template)


@router.delete("/templates/{template_id}", status_code=204)
def delete_template(
    template_id: int,
    hard_delete: bool = Query(False, description="Permanently delete"),
    db: Session = Depends(get_db),
):
    """
    Delete an import template (soft delete by default).

    - **template_id**: The template ID to delete
    - **hard_delete**: If true, permanently deletes
    """
    repo = ImportTemplateRepository(db)
    template = repo.get_by_id(template_id)

    if not template:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")

    if hard_delete:
        repo.hard_delete(template)
    else:
        repo.soft_delete(template)

    return None


# =============================================================================
# Category Mappings
# =============================================================================


@router.get("/category-mappings", response_model=list[CategoryMappingResponse])
def list_category_mappings(
    institution_id: int | None = Query(None, description="Filter by institution ID"),
    include_inactive: bool = Query(False, description="Include inactive mappings"),
    db: Session = Depends(get_db),
):
    """
    Get all category mappings.

    - **institution_id**: Optional filter by institution
    - **include_inactive**: Include inactive mappings
    """
    repo = CategoryMappingRepository(db)

    if institution_id:
        return repo.get_by_institution(institution_id, include_inactive=include_inactive)
    return repo.get_all(include_inactive=include_inactive)


@router.get("/category-mappings/{mapping_id}", response_model=CategoryMappingResponse)
def get_category_mapping(mapping_id: int, db: Session = Depends(get_db)):
    """
    Get a specific category mapping.

    - **mapping_id**: The mapping ID to retrieve
    """
    repo = CategoryMappingRepository(db)
    mapping = repo.get_by_id(mapping_id)

    if not mapping:
        raise HTTPException(status_code=404, detail=f"Mapping {mapping_id} not found")

    return mapping


@router.post("/category-mappings", response_model=CategoryMappingResponse, status_code=201)
def create_category_mapping(
    mapping_data: CategoryMappingCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new category mapping.

    - **institution_id**: The institution this mapping applies to
    - **bank_category_name**: The category name as it appears in bank exports
    - **coinpurse_category_id**: The CoinPurse category to map to
    - **priority**: Higher priority mappings take precedence (default: 1)
    """
    repo = CategoryMappingRepository(db)

    # Check for duplicate mapping
    if repo.mapping_exists(mapping_data.institution_id, mapping_data.bank_category_name):
        raise HTTPException(
            status_code=400,
            detail=f"Mapping for '{mapping_data.bank_category_name}' already exists for this institution",
        )

    mapping = CategoryMapping(**mapping_data.model_dump())
    return repo.create(mapping)


@router.patch("/category-mappings/{mapping_id}", response_model=CategoryMappingResponse)
def update_category_mapping(
    mapping_id: int,
    mapping_data: CategoryMappingUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a category mapping.

    - **mapping_id**: The mapping ID to update
    - All fields are optional
    """
    repo = CategoryMappingRepository(db)
    mapping = repo.get_by_id(mapping_id)

    if not mapping:
        raise HTTPException(status_code=404, detail=f"Mapping {mapping_id} not found")

    # Check for conflict if bank_category_name is being updated
    if mapping_data.bank_category_name:
        institution_id = mapping_data.institution_id or mapping.institution_id
        if repo.mapping_exists(institution_id, mapping_data.bank_category_name, exclude_id=mapping_id):
            raise HTTPException(
                status_code=400,
                detail=f"Mapping for '{mapping_data.bank_category_name}' already exists",
            )

    # Update only provided fields
    update_data = mapping_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mapping, field, value)

    return repo.update(mapping)


@router.delete("/category-mappings/{mapping_id}", status_code=204)
def delete_category_mapping(
    mapping_id: int,
    hard_delete: bool = Query(False, description="Permanently delete"),
    db: Session = Depends(get_db),
):
    """
    Delete a category mapping (soft delete by default).

    - **mapping_id**: The mapping ID to delete
    - **hard_delete**: If true, permanently deletes
    """
    repo = CategoryMappingRepository(db)
    mapping = repo.get_by_id(mapping_id)

    if not mapping:
        raise HTTPException(status_code=404, detail=f"Mapping {mapping_id} not found")

    if hard_delete:
        repo.hard_delete(mapping)
    else:
        repo.soft_delete(mapping)

    return None
