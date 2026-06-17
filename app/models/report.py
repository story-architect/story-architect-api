import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.character import Character
    from app.models.relationship import Relationship


class CharacterArchitectureReport(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "character_architecture_reports"

    character_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("characters.id", ondelete="CASCADE"), unique=True)

    character_core: Mapped[str] = mapped_column(Text, nullable=True)  # Usually basic info
    emotional_wound: Mapped[str] = mapped_column(Text, nullable=True)
    deepest_fear: Mapped[str] = mapped_column(Text, nullable=True)
    protective_lie: Mapped[str] = mapped_column(Text, nullable=True)
    behavior: Mapped[str] = mapped_column(Text, nullable=True)
    narrative_consequence: Mapped[str] = mapped_column(Text, nullable=True)
    narrative_consequence_custom: Mapped[str] = mapped_column(Text, nullable=True)

    conflict_created: Mapped[str] = mapped_column(Text, nullable=True)
    conflict_created_custom: Mapped[str] = mapped_column(Text, nullable=True)

    pressure_point: Mapped[str] = mapped_column(Text, nullable=True)
    pressure_point_custom: Mapped[str] = mapped_column(Text, nullable=True)

    transformation: Mapped[str] = mapped_column(Text, nullable=True)

    transformation_path: Mapped[str] = mapped_column(Text, nullable=True)
    transformation_path_custom: Mapped[str] = mapped_column(Text, nullable=True)

    custom_outdated_fields: Mapped[dict] = mapped_column(JSON, nullable=True)

    relationship_pattern: Mapped[str] = mapped_column(Text, nullable=True)
    story_engine_summary: Mapped[str] = mapped_column(Text, nullable=True)
    dramatic_potential: Mapped[str] = mapped_column(Text, nullable=True)
    inciting_relationship: Mapped[str] = mapped_column(Text, nullable=True)
    central_conflict: Mapped[str] = mapped_column(Text, nullable=True)
    story_beginning_summary: Mapped[str] = mapped_column(Text, nullable=True)

    is_stale: Mapped[bool] = mapped_column(default=False)
    stale_reason: Mapped[str] = mapped_column(Text, nullable=True)

    # Pattern engine metadata
    pattern_detected: Mapped[str] = mapped_column(Text, nullable=True)
    pattern_version: Mapped[int] = mapped_column(nullable=True)
    composition_detected: Mapped[str] = mapped_column(Text, nullable=True)

    character: Mapped["Character"] = relationship(back_populates="report")


class RelationshipArchitectureReport(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "relationship_architecture_reports"

    relationship_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("relationships.id", ondelete="CASCADE"), unique=True)

    current_result: Mapped[str] = mapped_column(Text, nullable=True)
    emotional_effect: Mapped[str] = mapped_column(Text, nullable=True)
    story_consequence: Mapped[str] = mapped_column(Text, nullable=True)
    current_relationship_risk: Mapped[str] = mapped_column(Text, nullable=True)
    turning_point: Mapped[str] = mapped_column(Text, nullable=True)
    relationship_law: Mapped[str] = mapped_column(Text, nullable=True)

    relationship_risk: Mapped[str] = mapped_column(Text, nullable=True)
    relationship_pattern: Mapped[str] = mapped_column(Text, nullable=True)
    consequence_summary: Mapped[str] = mapped_column(Text, nullable=True)

    is_stale: Mapped[bool] = mapped_column(default=False)
    stale_reason: Mapped[str] = mapped_column(Text, nullable=True)

    # Pattern engine metadata
    pattern_detected: Mapped[str] = mapped_column(Text, nullable=True)
    pattern_version: Mapped[int] = mapped_column(nullable=True)
    composition_detected: Mapped[str] = mapped_column(Text, nullable=True)

    relationship_: Mapped["Relationship"] = relationship(back_populates="report")
