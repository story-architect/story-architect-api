from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CharacterArchitectureReportResponse(BaseModel):
    id: UUID
    character_id: UUID
    character_core: Optional[str] = None
    emotional_wound: Optional[str] = None
    deepest_fear: Optional[str] = None
    protective_lie: Optional[str] = None
    behavior: Optional[str] = None
    narrative_consequence: Optional[str] = None
    conflict_created: Optional[str] = None
    transformation: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RelationshipArchitectureReportResponse(BaseModel):
    id: UUID
    relationship_id: UUID
    current_result: Optional[str] = None
    emotional_effect: Optional[str] = None
    story_consequence: Optional[str] = None
    current_relationship_risk: Optional[str] = None
    turning_point: Optional[str] = None
    relationship_law: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
