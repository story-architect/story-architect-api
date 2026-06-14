from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import Character, Story
from app.schemas.character import CharacterCreate, CharacterResponse, CharacterUpdate

router = APIRouter()


@router.post("/stories/{story_id}/characters", response_model=CharacterResponse)
def create_character_for_story(story_id: UUID, character_in: CharacterCreate, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    character = Character(**character_in.model_dump(), story_id=story_id)
    db.add(character)
    db.commit()
    db.refresh(character)
    return character


@router.get("/stories/{story_id}/characters", response_model=List[CharacterResponse])
def get_characters_for_story(story_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    characters = db.query(Character).filter(Character.story_id == story_id).offset(skip).limit(limit).all()
    return characters


@router.get("/characters/{character_id}", response_model=CharacterResponse)
def get_character(character_id: UUID, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.put("/characters/{character_id}", response_model=CharacterResponse)
def update_character(character_id: UUID, character_in: CharacterUpdate, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    update_data = character_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(character, field, value)
    db.commit()
    db.refresh(character)
    return character


@router.delete("/characters/{character_id}", response_model=CharacterResponse)
def delete_character(character_id: UUID, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    db.delete(character)
    db.commit()
    return character
