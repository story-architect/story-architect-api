from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import Character, DiscoveryEvent, Relationship, Story
from app.schemas.discovery import DiscoveryEventResponse
from app.schemas.story import (
    ActivityFeedItemResponse,
    LatestDiscoveryResponse,
    NextDiscoveryResponse,
    StoryCreate,
    StoryResponse,
    StoryUpdate,
)

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


@router.get("/{story_id}/latest-discovery", response_model=LatestDiscoveryResponse)
def get_latest_discovery(story_id: UUID, db: Session = Depends(get_db)):
    event = (
        db.query(DiscoveryEvent)
        .filter(DiscoveryEvent.story_id == story_id)
        .order_by(DiscoveryEvent.created_at.desc())
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail="No discoveries found")
    return LatestDiscoveryResponse(title=event.title, summary=event.description, created_at=event.created_at)


@router.get("/{story_id}/discovery-journal", response_model=List[DiscoveryEventResponse])
def get_discovery_journal(story_id: UUID, db: Session = Depends(get_db)):
    events = (
        db.query(DiscoveryEvent)
        .filter(DiscoveryEvent.story_id == story_id)
        .order_by(DiscoveryEvent.created_at.desc())
        .limit(50)
        .all()
    )
    return events


@router.get("/{story_id}/activity-feed", response_model=List[ActivityFeedItemResponse])
def get_activity_feed(story_id: UUID, db: Session = Depends(get_db)):
    events = (
        db.query(DiscoveryEvent)
        .filter(DiscoveryEvent.story_id == story_id)
        .order_by(DiscoveryEvent.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        ActivityFeedItemResponse(
            title=e.title,
            description=e.description,
            event_type=e.event_type.value if hasattr(e.event_type, "value") else e.event_type,
            timestamp=e.created_at,
        )
        for e in events
    ]


@router.get("/{story_id}/next-discovery", response_model=NextDiscoveryResponse)
def get_next_discovery(story_id: UUID, db: Session = Depends(get_db)):
    # Calculate simple next discovery hint
    # For now, just a basic heuristic:
    chars = db.query(Character).filter(Character.story_id == story_id).count()
    rels = db.query(Relationship).filter(Relationship.story_id == story_id).count()
    events = db.query(DiscoveryEvent).filter(DiscoveryEvent.story_id == story_id).count()

    progress = min(100, int((events / 20) * 100)) if chars > 0 else 0

    if chars == 0:
        next_disc = "Create your first Character"
    elif rels == 0 and chars > 1:
        next_disc = "Form a Relationship"
    else:
        next_disc = "Continue Discovery Questions"

    return NextDiscoveryResponse(next_discovery=next_disc, progress=progress)
