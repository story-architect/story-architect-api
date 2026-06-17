from app.models.base import Base
from app.models.character import Character, RoleEnum
from app.models.discovery import DiscoveryAnswer, DiscoveryEvent, DiscoveryQuestion, EventTypeEnum, FlowTypeEnum
from app.models.relationship import Relationship, RelationshipTypeEnum
from app.models.report import CharacterArchitectureReport, RelationshipArchitectureReport
from app.models.story import Story
from app.models.user import User

# This ensures all models are imported and known to SQLAlchemy's MetaData before migrations

__all__ = [
    "Base",
    "Character",
    "Story",
    "User",
    "Relationship",
    "DiscoveryQuestion",
    "DiscoveryAnswer",
    "FlowTypeEnum",
    "DiscoveryEvent",
    "EventTypeEnum",
    "CharacterArchitectureReport",
    "RelationshipArchitectureReport",
]
