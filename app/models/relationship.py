import enum
import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.character import Character
    from app.models.discovery import DiscoveryAnswer
    from app.models.report import RelationshipArchitectureReport
    from app.models.story import Story


class RelationshipTypeEnum(str, enum.Enum):
    ROMANCE = "ROMANCE"
    FRIENDSHIP = "FRIENDSHIP"
    FAMILY = "FAMILY"
    RIVALRY = "RIVALRY"
    MENTOR = "MENTOR"
    OTHER = "OTHER"


class Relationship(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "relationships"

    story_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stories.id", ondelete="CASCADE"), index=True)
    character_a_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("characters.id", ondelete="CASCADE"), index=True)
    character_b_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("characters.id", ondelete="CASCADE"), index=True)
    relationship_type: Mapped[RelationshipTypeEnum] = mapped_column(String(50))

    story: Mapped["Story"] = relationship(back_populates="relationships")

    character_a: Mapped["Character"] = relationship(foreign_keys=[character_a_id])
    character_b: Mapped["Character"] = relationship(foreign_keys=[character_b_id])

    discovery_answers: Mapped[List["DiscoveryAnswer"]] = relationship(
        back_populates="relationship_", cascade="all, delete-orphan"
    )
    report: Mapped["RelationshipArchitectureReport"] = relationship(
        back_populates="relationship_", uselist=False, cascade="all, delete-orphan"
    )
