"""
Repository layer for ImportTemplate model
Handles all database operations for import templates
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.import_template import ImportTemplate


class ImportTemplateRepository:
    """Repository for ImportTemplate database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, template_id: int) -> ImportTemplate | None:
        """Get import template by ID"""
        return self.db.get(ImportTemplate, template_id)

    def get_all(self, include_inactive: bool = False) -> list[ImportTemplate]:
        """
        Get all import templates

        Args:
            include_inactive: If True, includes inactive templates
        """
        stmt = select(ImportTemplate)
        if not include_inactive:
            stmt = stmt.where(ImportTemplate.is_active)
        stmt = stmt.order_by(ImportTemplate.template_name)
        return list(self.db.scalars(stmt))

    def get_by_name(self, name: str) -> ImportTemplate | None:
        """Get template by exact name"""
        stmt = select(ImportTemplate).where(ImportTemplate.template_name == name)
        return self.db.scalar(stmt)

    def create(self, template: ImportTemplate) -> ImportTemplate:
        """Create a new import template"""
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def update(self, template: ImportTemplate) -> ImportTemplate:
        """Update an existing import template"""
        self.db.commit()
        self.db.refresh(template)
        return template

    def soft_delete(self, template: ImportTemplate) -> ImportTemplate:
        """Soft delete a template by setting is_active to False"""
        template.is_active = False
        return self.update(template)

    def hard_delete(self, template: ImportTemplate) -> None:
        """Permanently delete a template (use with caution!)"""
        self.db.delete(template)
        self.db.commit()

    def exists(self, template_id: int) -> bool:
        """Check if a template exists"""
        return self.get_by_id(template_id) is not None

    def name_exists(self, name: str, exclude_id: int | None = None) -> bool:
        """
        Check if a template name already exists (among active templates)

        Args:
            name: Template name to check
            exclude_id: Optional ID to exclude (for updates)
        """
        stmt = select(ImportTemplate).where(
            ImportTemplate.template_name == name, ImportTemplate.is_active
        )
        if exclude_id:
            stmt = stmt.where(ImportTemplate.template_id != exclude_id)
        return self.db.scalar(stmt) is not None
