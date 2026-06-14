from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.character import RoleEnum

class CharacterBase(BaseModel):
    name: str
    age: Optional[int] = None
    role: RoleEnum
    archetype: Optional[str] = None

class CharacterCreate(CharacterBase):
    pass

class CharacterUpdate(CharacterBase):
    name: Optional[str] = None
    role: Optional[RoleEnum] = None

class CharacterResponse(CharacterBase):
    id: UUID
    story_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
