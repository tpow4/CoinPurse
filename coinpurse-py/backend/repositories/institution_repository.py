"""
Repository layer for Institution model
Handles all database operations for institutions
"""
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from models.institution import Institution


class InstitutionRepository:
    """Repository for Institution database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, institution_id: int) -> Optional[Institution]:
        """Get institution by ID"""
        return self.db.get(Institution, institution_id)
    
    def get_all(self, include_inactive: bool = False) -> List[Institution]:
        """
        Get all institutions
        
        Args:
            include_inactive: If True, includes inactive institutions
        """
        stmt = select(Institution)
        if not include_inactive:
            stmt = stmt.where(Institution.is_active)
        stmt = stmt.order_by(Institution.name)
        return list(self.db.scalars(stmt))
    
    def get_by_name(self, name: str) -> Optional[Institution]:
        """Get institution by exact name"""
        stmt = select(Institution).where(Institution.name == name)
        return self.db.scalar(stmt)
    
    def search_by_name(self, search_term: str, include_inactive: bool = False) -> List[Institution]:
        """
        Search institutions by partial name match

        Args:
            search_term: The term to search for in institution names
            include_inactive: If True, includes inactive institutions
        """
        stmt = select(Institution).where(
            Institution.name.ilike(f"%{search_term}%")
        )
        if not include_inactive:
            stmt = stmt.where(Institution.is_active)
        stmt = stmt.order_by(Institution.name)
        return list(self.db.scalars(stmt))
    
    def create(self, institution: Institution) -> Institution:
        """Create a new institution"""
        self.db.add(institution)
        self.db.commit()
        self.db.refresh(institution)
        return institution
    
    def update(self, institution: Institution) -> Institution:
        """Update an existing institution"""
        self.db.commit()
        self.db.refresh(institution)
        return institution
    
    def soft_delete(self, institution: Institution) -> Institution:
        """Soft delete an institution by setting is_active to False"""
        institution.is_active = False
        return self.update(institution)
    
    def hard_delete(self, institution: Institution) -> None:
        """Permanently delete an institution (use with caution!)"""
        self.db.delete(institution)
        self.db.commit()
    
    def exists(self, institution_id: int) -> bool:
        """Check if an institution exists"""
        return self.get_by_id(institution_id) is not None
    
    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if an institution name already exists
        
        Args:
            name: Institution name to check
            exclude_id: Optional ID to exclude (for updates)
        """
        stmt = select(Institution).where(Institution.name == name)
        if exclude_id:
            stmt = stmt.where(Institution.institution_id != exclude_id)
        return self.db.scalar(stmt) is not None