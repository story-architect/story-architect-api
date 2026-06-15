from app.models.base import Base
from app.models.character import Character, RoleEnum
from app.models.discovery import DiscoveryAnswer, DiscoveryQuestion, FlowTypeEnum, DiscoveryEvent, EventTypeEnum
from app.models.relationship import Relationship, RelationshipTypeEnum
from app.models.report import CharacterArchitectureReport, RelationshipArchitectureReport
from app.models.story import Story

# This ensures all models are imported and known to SQLAlchemy's MetaData before migrations

__all__ = [
    "Base",
    "Character",
    "Story",
    "Relationship",
    "DiscoveryQuestion",
    "DiscoveryAnswer",
    "FlowTypeEnum",
    "DiscoveryEvent",
    "EventTypeEnum",
    "CharacterArchitectureReport",
    "RelationshipArchitectureReport",
]
