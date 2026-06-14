from app.models.base import Base
from app.models.story import Story
from app.models.character import Character, RoleEnum
from app.models.relationship import Relationship, RelationshipTypeEnum
from app.models.discovery import DiscoveryQuestion, DiscoveryAnswer, FlowTypeEnum
from app.models.report import CharacterArchitectureReport, RelationshipArchitectureReport

# This ensures all models are imported and known to SQLAlchemy's MetaData before migrations
