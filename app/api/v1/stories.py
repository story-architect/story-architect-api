from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.api.dependencies import get_db
from app.models import Story
from app.schemas.story import StoryCreate, StoryUpdate, StoryResponse

router = APIRouter()

@router.post("", response_model=StoryResponse)
def create_story(story_in: StoryCreate, db: Session = Depends(get_db)):
    story = Story(**story_in.model_dump())
    db.add(story)
    db.commit()
    db.refresh(story)
    return story

@router.get("", response_model=List[StoryResponse])
def get_stories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stories = db.query(Story).offset(skip).limit(limit).all()
    return stories

@router.get("/{story_id}", response_model=StoryResponse)
def get_story(story_id: UUID, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.put("/{story_id}", response_model=StoryResponse)
def update_story(story_id: UUID, story_in: StoryUpdate, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    update_data = story_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(story, field, value)
    db.commit()
    db.refresh(story)
    return story

@router.delete("/{story_id}", response_model=StoryResponse)
def delete_story(story_id: UUID, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    db.delete(story)
    db.commit()
    return story
