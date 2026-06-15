from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.discovery import EventTypeEnum, FlowTypeEnum


class DiscoveryQuestionResponse(BaseModel):
    id: UUID
    flow_type: FlowTypeEnum
    question_key: str
    question_text: str
    order_index: int
    suggested_answers: List[Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DiscoveryAnswerBase(BaseModel):
    story_id: UUID
    character_id: Optional[UUID] = None
    relationship_id: Optional[UUID] = None
    question_id: UUID
    selected_answer: Optional[str] = None
    custom_answer: Optional[str] = None


class DiscoveryAnswerCreate(DiscoveryAnswerBase):
    pass


class DiscoveryAnswerUpdate(BaseModel):
    selected_answer: Optional[str] = None
    custom_answer: Optional[str] = None


class DiscoveryAnswerResponse(DiscoveryAnswerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    unlocked_events: Optional[List["DiscoveryEventResponse"]] = None

    model_config = ConfigDict(from_attributes=True)


class DiscoveryEventResponse(BaseModel):
    id: UUID
    story_id: UUID
    character_id: Optional[UUID] = None
    relationship_id: Optional[UUID] = None
    event_type: EventTypeEnum
    title: Optional[str] = None
    description: Optional[str] = None
    event_metadata: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
