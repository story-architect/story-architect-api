from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import Character, CharacterArchitectureReport, Relationship, RelationshipArchitectureReport
from app.schemas.report import CharacterArchitectureReportResponse, RelationshipArchitectureReportResponse
from app.services.event_service import handle_report_generated
from app.services.report_builder import generate_character_report, generate_relationship_report

router = APIRouter()


@router.post("/characters/{character_id}/generate-report", response_model=CharacterArchitectureReportResponse)
def generate_report_for_character(character_id: UUID, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    report = generate_character_report(db, character_id)
    handle_report_generated(
        db,
        story_id=character.story_id,
        event_metadata={"name": character.name, "report_type": "character"},
        character_id=character_id,
    )
    return report


@router.get("/characters/{character_id}/report", response_model=CharacterArchitectureReportResponse)
def get_character_report(character_id: UUID, db: Session = Depends(get_db)):
    report = (
        db.query(CharacterArchitectureReport).filter(CharacterArchitectureReport.character_id == character_id).first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this character")
    return report


@router.post("/relationships/{relationship_id}/generate-report", response_model=RelationshipArchitectureReportResponse)
def generate_report_for_relationship(relationship_id: UUID, db: Session = Depends(get_db)):
    relationship = db.query(Relationship).filter(Relationship.id == relationship_id).first()
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")

    report = generate_relationship_report(db, relationship_id)

    char_a = db.query(Character).filter(Character.id == relationship.character_a_id).first()
    char_b = db.query(Character).filter(Character.id == relationship.character_b_id).first()
    rel_name = f"{char_a.name} & {char_b.name}" if char_a and char_b else "Relationship"

    handle_report_generated(
        db,
        story_id=relationship.story_id,
        event_metadata={"name": rel_name, "report_type": "relationship"},
        relationship_id=relationship_id,
    )
    return report


@router.get("/relationships/{relationship_id}/report", response_model=RelationshipArchitectureReportResponse)
def get_relationship_report(relationship_id: UUID, db: Session = Depends(get_db)):
    report = (
        db.query(RelationshipArchitectureReport)
        .filter(RelationshipArchitectureReport.relationship_id == relationship_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this relationship")
    return report
