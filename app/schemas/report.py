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
    relationship_pattern: Optional[str] = None
    story_engine_summary: Optional[str] = None
    dramatic_potential: Optional[str] = None
    inciting_relationship: Optional[str] = None
    central_conflict: Optional[str] = None
    story_beginning_summary: Optional[str] = None
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
    relationship_risk: Optional[str] = None
    relationship_pattern: Optional[str] = None
    consequence_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StoryEngineResponse(BaseModel):
    emotional_wound: str
    fear: str
    protective_lie: str
    relationship_pattern: str
    story_conflict: str
    transformation: str


class WhyThisMattersResponse(BaseModel):
    main_statement: str
    relationships: str
    choices: str
    conflict: str
    dramatic_potential: str


class NarrativeConsequenceResponse(BaseModel):
    main_statement: str
    protective_lie: str
    behavior: str
    story_consequence: str
    conflict_created: str


class WhereStoryBeginsResponse(BaseModel):
    key_insight: str
    inciting_relationship: str
    central_conflict: str
    transformation: str
    final_statement: str


class RelationshipConsequenceResponse(BaseModel):
    current_result: str
    emotional_effect: str
    story_consequence: str
    current_relationship_risk: str
    turning_point: str
    relationship_law: str
    relationship_risk: str
    relationship_pattern: str
    consequence_summary: str

class PatternEmergingResponse(BaseModel):
    title: str
    pattern_name: str
    insight: str
    supporting_text: str
    next_discovery_hint: str

