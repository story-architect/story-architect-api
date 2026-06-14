from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.api.dependencies import get_db
from app.models import Relationship, Story, Character
from app.schemas.relationship import RelationshipCreate, RelationshipUpdate, RelationshipResponse

router = APIRouter()

@router.post("/stories/{story_id}/relationships", response_model=RelationshipResponse)
def create_relationship(story_id: UUID, relationship_in: RelationshipCreate, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
        
    char_a = db.query(Character).filter(Character.id == relationship_in.character_a_id, Character.story_id == story_id).first()
    char_b = db.query(Character).filter(Character.id == relationship_in.character_b_id, Character.story_id == story_id).first()
    if not char_a or not char_b:
        raise HTTPException(status_code=400, detail="One or both characters not found in this story")

    relationship = Relationship(**relationship_in.model_dump(), story_id=story_id)
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    return relationship

@router.get("/stories/{story_id}/relationships", response_model=List[RelationshipResponse])
def get_relationships_for_story(story_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
        
    relationships = db.query(Relationship).filter(Relationship.story_id == story_id).offset(skip).limit(limit).all()
    return relationships

@router.get("/relationships/{relationship_id}", response_model=RelationshipResponse)
def get_relationship(relationship_id: UUID, db: Session = Depends(get_db)):
    relationship = db.query(Relationship).filter(Relationship.id == relationship_id).first()
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return relationship

@router.put("/relationships/{relationship_id}", response_model=RelationshipResponse)
def update_relationship(relationship_id: UUID, relationship_in: RelationshipUpdate, db: Session = Depends(get_db)):
    relationship = db.query(Relationship).filter(Relationship.id == relationship_id).first()
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")
    update_data = relationship_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(relationship, field, value)
    db.commit()
    db.refresh(relationship)
    return relationship

@router.delete("/relationships/{relationship_id}", response_model=RelationshipResponse)
def delete_relationship(relationship_id: UUID, db: Session = Depends(get_db)):
    relationship = db.query(Relationship).filter(Relationship.id == relationship_id).first()
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")
    db.delete(relationship)
    db.commit()
    return relationship
