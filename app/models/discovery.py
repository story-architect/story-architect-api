import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

CustomJSON = JSON().with_variant(JSONB, "postgresql")

if TYPE_CHECKING:
    from app.models.character import Character
    from app.models.relationship import Relationship
    from app.models.story import Story


class FlowTypeEnum(str, enum.Enum):
    CHARACTER_DISCOVERY = "CHARACTER_DISCOVERY"
    RELATIONSHIP_DISCOVERY = "RELATIONSHIP_DISCOVERY"


class DiscoveryQuestion(Base, UUIDMixin):
    __tablename__ = "discovery_questions"

    flow_type: Mapped[FlowTypeEnum] = mapped_column(String(50), index=True)
    question_key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    question_text: Mapped[str] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer)
    suggested_answers: Mapped[List[Any]] = mapped_column(CustomJSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DiscoveryAnswer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "discovery_answers"

    story_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stories.id", ondelete="CASCADE"), index=True)
    character_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=True, index=True
    )
    relationship_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("relationships.id", ondelete="CASCADE"), nullable=True, index=True
    )
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("discovery_questions.id", ondelete="CASCADE"), index=True)

    selected_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    story: Mapped["Story"] = relationship(back_populates="discovery_answers")
    character: Mapped[Optional["Character"]] = relationship(back_populates="discovery_answers")
    relationship_: Mapped[Optional["Relationship"]] = relationship("Relationship", back_populates="discovery_answers")
    question: Mapped["DiscoveryQuestion"] = relationship()
