from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StoryBase(BaseModel):
    title: str
    genre: Optional[str] = None
    one_sentence_premise: Optional[str] = None


class StoryCreate(StoryBase):
    pass


class StoryUpdate(StoryBase):
    title: Optional[str] = None


class StoryResponse(StoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    character_count: Optional[int] = 0
    relationship_count: Optional[int] = 0
    discovery_progress: Optional[int] = 0
    next_insight: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class LatestDiscoveryResponse(BaseModel):
    title: str
    summary: str
    created_at: datetime

class ActivityFeedItemResponse(BaseModel):
    title: str
    description: str
    event_type: str
    timestamp: datetime

class NextDiscoveryResponse(BaseModel):
    next_discovery: str
    progress: int

