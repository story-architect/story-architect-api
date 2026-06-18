from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.api.dependencies import get_db, get_current_user
from app.models import Character, CharacterArchitectureReport, Relationship, RelationshipArchitectureReport, Story, User
from app.schemas.report import (
    CharacterArchitectureReportResponse,
    RelationshipArchitectureReportResponse,
    ReportInterpretationUpdate,
)
from app.services.event_service import (
    handle_dramatic_architecture_discovered,
    handle_interpretation_revised,
    handle_report_generated,
)
from app.services.report_builder import generate_character_report, generate_relationship_report

router = APIRouter()


@router.post("/characters/{character_id}/generate-report", response_model=CharacterArchitectureReportResponse)
def generate_report_for_character(
    character_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    character = (
        db.query(Character).join(Story).filter(Character.id == character_id, Story.user_id == current_user.id).first()
    )
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    report = generate_character_report(db, character_id)
    handle_report_generated(
        db,
        story_id=character.story_id,
        event_metadata={"name": character.name, "report_type": "character"},
        character_id=character_id,
    )
    handle_dramatic_architecture_discovered(
        db,
        story_id=character.story_id,
        event_metadata={"name": character.name},
        character_id=character_id,
    )
    return report


@router.get("/characters/{character_id}/report", response_model=CharacterArchitectureReportResponse)
def get_character_report(
    character_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    report = (
        db.query(CharacterArchitectureReport)
        .join(Character)
        .join(Story)
        .filter(CharacterArchitectureReport.character_id == character_id, Story.user_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this character")
    return report


@router.patch("/characters/{report_id}/interpretations", response_model=CharacterArchitectureReportResponse)
def update_character_interpretations(
    report_id: UUID,
    interpretations: ReportInterpretationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = (
        db.query(CharacterArchitectureReport)
        .join(Character)
        .join(Story)
        .filter(CharacterArchitectureReport.id == report_id, Story.user_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    outdated_fields = report.custom_outdated_fields or {}

    if interpretations.narrative_consequence_custom is not None:
        report.narrative_consequence_custom = (
            interpretations.narrative_consequence_custom if interpretations.narrative_consequence_custom else None
        )
        outdated_fields.pop("narrative_consequence_custom", None)

    if interpretations.conflict_created_custom is not None:
        report.conflict_created_custom = (
            interpretations.conflict_created_custom if interpretations.conflict_created_custom else None
        )
        outdated_fields.pop("conflict_created_custom", None)

    if interpretations.pressure_point_custom is not None:
        report.pressure_point_custom = (
            interpretations.pressure_point_custom if interpretations.pressure_point_custom else None
        )
        outdated_fields.pop("pressure_point_custom", None)

    if interpretations.transformation_path_custom is not None:
        report.transformation_path_custom = (
            interpretations.transformation_path_custom if interpretations.transformation_path_custom else None
        )
        outdated_fields.pop("transformation_path_custom", None)

    if interpretations.clear_outdated:
        for field in interpretations.clear_outdated:
            outdated_fields.pop(field, None)

    report.custom_outdated_fields = outdated_fields
    flag_modified(report, "custom_outdated_fields")
    db.commit()
    db.refresh(report)

    character = db.query(Character).filter(Character.id == report.character_id).first()
    if character:
        handle_interpretation_revised(
            db,
            story_id=character.story_id,
            event_metadata={"name": character.name, "report_type": "character"},
            character_id=character.id,
        )

    return report


@router.post("/relationships/{relationship_id}/generate-report", response_model=RelationshipArchitectureReportResponse)
def generate_report_for_relationship(
    relationship_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    relationship = (
        db.query(Relationship)
        .join(Story)
        .filter(Relationship.id == relationship_id, Story.user_id == current_user.id)
        .first()
    )
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
def get_relationship_report(
    relationship_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    report = (
        db.query(RelationshipArchitectureReport)
        .join(Relationship)
        .join(Story)
        .filter(RelationshipArchitectureReport.relationship_id == relationship_id, Story.user_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this relationship")
    return report
