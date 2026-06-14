from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.relationship import RelationshipTypeEnum

class RelationshipBase(BaseModel):
    character_a_id: UUID
    character_b_id: UUID
    relationship_type: RelationshipTypeEnum

class RelationshipCreate(RelationshipBase):
    pass

class RelationshipUpdate(BaseModel):
    relationship_type: Optional[RelationshipTypeEnum] = None

class RelationshipResponse(RelationshipBase):
    id: UUID
    story_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
