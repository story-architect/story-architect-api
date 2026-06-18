from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import Character, Relationship, RelationshipArchitectureReport, Story, User
from app.schemas.relationship import RelationshipCreate, RelationshipResponse, RelationshipUpdate
from app.schemas.report import RelationshipConsequenceResponse
from app.services.event_service import handle_relationship_created
from app.services.report_builder import generate_relationship_report

router = APIRouter()


@router.post("/stories/{story_id}/relationships", response_model=RelationshipResponse)
def create_relationship(
    story_id: UUID,
    relationship_in: RelationshipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    story = db.query(Story).filter(Story.id == story_id, Story.user_id == current_user.id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    char_a = (
        db.query(Character)
        .filter(Character.id == relationship_in.character_a_id, Character.story_id == story_id)
        .first()
    )
    char_b = (
        db.query(Character)
        .filter(Character.id == relationship_in.character_b_id, Character.story_id == story_id)
        .first()
    )
    if not char_a or not char_b:
        raise HTTPException(status_code=400, detail="One or both characters not found in this story")

    relationship = Relationship(**relationship_in.model_dump(), story_id=story_id)
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    handle_relationship_created(db, story_id, relationship.id, char_a.name, char_b.name)
    return relationship


@router.get("/stories/{story_id}/relationships", response_model=List[RelationshipResponse])
def get_relationships_for_story(
    story_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    story = db.query(Story).filter(Story.id == story_id, Story.user_id == current_user.id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    relationships = (
        db.query(Relationship)
        .filter(Relationship.story_id == story_id)
        .order_by(Relationship.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return relationships


@router.get("/relationships/{relationship_id}", response_model=RelationshipResponse)
def get_relationship(
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
    return relationship


@router.put("/relationships/{relationship_id}", response_model=RelationshipResponse)
def update_relationship(
    relationship_id: UUID,
    relationship_in: RelationshipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    relationship = (
        db.query(Relationship)
        .join(Story)
        .filter(Relationship.id == relationship_id, Story.user_id == current_user.id)
        .first()
    )
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")
    update_data = relationship_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(relationship, field, value)
    db.commit()
    db.refresh(relationship)
    return relationship


@router.delete("/relationships/{relationship_id}", response_model=RelationshipResponse)
def delete_relationship(
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
    db.delete(relationship)
    db.commit()
    return relationship


@router.get("/relationships/{relationship_id}/consequence", response_model=RelationshipConsequenceResponse)
def get_relationship_consequence(
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

    report = (
        db.query(RelationshipArchitectureReport)
        .filter(RelationshipArchitectureReport.relationship_id == relationship_id)
        .first()
    )
    if not report:
        report = generate_relationship_report(db, relationship_id)
    return RelationshipConsequenceResponse(
        current_result=report.current_result or "Not discovered yet.",
        emotional_effect=report.emotional_effect or "Not discovered yet.",
        story_consequence=report.story_consequence or "Not discovered yet.",
        current_relationship_risk=report.current_relationship_risk or "Not discovered yet.",
        turning_point=report.turning_point or "Not discovered yet.",
        relationship_law=report.relationship_law or "Not discovered yet.",
        relationship_risk=report.relationship_risk or "Not discovered yet.",
        relationship_pattern=report.relationship_pattern or "Not discovered yet.",
        consequence_summary=report.consequence_summary or "Not discovered yet.",
    )
