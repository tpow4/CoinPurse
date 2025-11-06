from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Institution

class InstitutionRepository: 
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Institution]:
        """Get all institutions"""
        query = select(Institution).order_by(Institution.name)
        return list(self.db.scalars(query))

    def get_all_active(self) -> list[Institution]:
        """Get all active institutions"""
        query = select(Institution).where(
            Institution.is_active is True
            ).order_by(Institution.display_order)
        return list(self.db.scalars(query))
    
    def get_by_id(self, institution_id: int) -> Institution | None:
        """Get an institution by its ID"""
        return self.db.get(Institution, institution_id)
    
    def create(self, institution: Institution) -> Institution:
        """create a new institution"""
        self.db.add(institution)
        self.db.commit()
        self.db.refresh(institution)
        return institution
    