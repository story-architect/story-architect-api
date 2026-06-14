from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.dependencies import get_db
from app.models import Character, Relationship, CharacterArchitectureReport, RelationshipArchitectureReport
from app.schemas.report import CharacterArchitectureReportResponse, RelationshipArchitectureReportResponse
from app.services.report_builder import generate_character_report, generate_relationship_report

router = APIRouter()

@router.post("/characters/{character_id}/generate-report", response_model=CharacterArchitectureReportResponse)
def generate_report_for_character(character_id: UUID, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    report = generate_character_report(db, character_id)
    return report

@router.get("/characters/{character_id}/report", response_model=CharacterArchitectureReportResponse)
def get_character_report(character_id: UUID, db: Session = Depends(get_db)):
    report = db.query(CharacterArchitectureReport).filter(CharacterArchitectureReport.character_id == character_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this character")
    return report

@router.post("/relationships/{relationship_id}/generate-report", response_model=RelationshipArchitectureReportResponse)
def generate_report_for_relationship(relationship_id: UUID, db: Session = Depends(get_db)):
    relationship = db.query(Relationship).filter(Relationship.id == relationship_id).first()
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    report = generate_relationship_report(db, relationship_id)
    return report

@router.get("/relationships/{relationship_id}/report", response_model=RelationshipArchitectureReportResponse)
def get_relationship_report(relationship_id: UUID, db: Session = Depends(get_db)):
    report = db.query(RelationshipArchitectureReport).filter(RelationshipArchitectureReport.relationship_id == relationship_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this relationship")
    return report
