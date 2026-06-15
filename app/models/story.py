from typing import TYPE_CHECKING, List

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.character import Character
    from app.models.discovery import DiscoveryAnswer
    from app.models.relationship import Relationship


class Story(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "stories"

    title: Mapped[str] = mapped_column(String(255), index=True)
    genre: Mapped[str] = mapped_column(String(100), nullable=True)
    one_sentence_premise: Mapped[str] = mapped_column(Text, nullable=True)

    characters: Mapped[List["Character"]] = relationship(back_populates="story", cascade="all, delete-orphan")
    relationships: Mapped[List["Relationship"]] = relationship(back_populates="story", cascade="all, delete-orphan")
    discovery_answers: Mapped[List["DiscoveryAnswer"]] = relationship(
        back_populates="story", cascade="all, delete-orphan"
    )

    @property
    def character_count(self) -> int:
        return len(self.characters)

    @property
    def relationship_count(self) -> int:
        return len(self.relationships)

    @property
    def discovery_progress(self) -> int:
        total_questions = (len(self.characters) * 7) + (len(self.relationships) * 7)
        if total_questions == 0:
            return 0
        return int((len(self.discovery_answers) / total_questions) * 100)

    @property
    def next_insight(self) -> str | None:
        if len(self.characters) == 0 and len(self.relationships) == 0:
            return "Add Characters"

        char_insights = ["Wound", "Fear", "Lie", "Behavior", "Consequence", "Conflict", "Transformation"]
        rel_insights = ["Importance", "Hidden Truth A", "Hidden Truth B", "Protection", "Misunderstanding", "Relationship Risk", "Turning Point"]

        for char in self.characters:
            char_ans = [a for a in self.discovery_answers if a.character_id == char.id]
            if len(char_ans) < 7:
                return f"{char.name}'s {char_insights[len(char_ans)]}"

        for rel in self.relationships:
            rel_ans = [a for a in self.discovery_answers if a.relationship_id == rel.id]
            if len(rel_ans) < 7:
                return rel_insights[len(rel_ans)]

        return "Ready for Architecture"
