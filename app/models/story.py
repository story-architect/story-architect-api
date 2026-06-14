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
