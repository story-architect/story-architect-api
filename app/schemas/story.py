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

    model_config = ConfigDict(from_attributes=True)
