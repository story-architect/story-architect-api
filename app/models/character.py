import enum
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
import uuid
from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.story import Story
    from app.models.discovery import DiscoveryAnswer
    from app.models.report import CharacterArchitectureReport

class RoleEnum(str, enum.Enum):
    MAIN_CHARACTER = "MAIN_CHARACTER"
    SUPPORTING_CHARACTER = "SUPPORTING_CHARACTER"

class Character(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "characters"

    story_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stories.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    role: Mapped[RoleEnum] = mapped_column(String(50))
    archetype: Mapped[str] = mapped_column(String(100), nullable=True)

    story: Mapped["Story"] = relationship(back_populates="characters")
    discovery_answers: Mapped[List["DiscoveryAnswer"]] = relationship(back_populates="character", cascade="all, delete-orphan")
    report: Mapped["CharacterArchitectureReport"] = relationship(back_populates="character", uselist=False, cascade="all, delete-orphan")
