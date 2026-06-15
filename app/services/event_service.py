import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.discovery import DiscoveryEvent, EventTypeEnum
from app.services.insight_generator import get_character_deterministic_fields, get_pattern_emerging_fields


def create_event(
    db: Session,
    story_id: uuid.UUID,
    event_type: EventTypeEnum,
    title: str,
    description: str,
    character_id: Optional[uuid.UUID] = None,
    relationship_id: Optional[uuid.UUID] = None,
):
    event = DiscoveryEvent(
        story_id=story_id,
        character_id=character_id,
        relationship_id=relationship_id,
        event_type=event_type,
        title=title,
        description=description,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def handle_character_created(db: Session, story_id: uuid.UUID, character_id: uuid.UUID, character_name: str):
    create_event(
        db,
        story_id=story_id,
        character_id=character_id,
        event_type=EventTypeEnum.CHARACTER_CREATED,
        title="Character Discovered",
        description=f"You added {character_name} to the story.",
    )


def handle_relationship_created(
    db: Session, story_id: uuid.UUID, relationship_id: uuid.UUID, char_a_name: str, char_b_name: str
):
    create_event(
        db,
        story_id=story_id,
        relationship_id=relationship_id,
        event_type=EventTypeEnum.RELATIONSHIP_CREATED,
        title="Relationship Formed",
        description=f"A connection between {char_a_name} and {char_b_name} was established.",
    )


def handle_report_generated(
    db: Session,
    story_id: uuid.UUID,
    title: str,
    description: str,
    character_id: Optional[uuid.UUID] = None,
    relationship_id: Optional[uuid.UUID] = None,
):
    create_event(
        db,
        story_id=story_id,
        character_id=character_id,
        relationship_id=relationship_id,
        event_type=EventTypeEnum.REPORT_GENERATED,
        title=title,
        description=description,
    )


def handle_question_answered(
    db: Session,
    story_id: uuid.UUID,
    question_text: str,
    answer_text: str,
    character_id: Optional[uuid.UUID] = None,
    relationship_id: Optional[uuid.UUID] = None,
):
    # Truncate answer for feed
    short_answer = answer_text if len(answer_text) < 50 else answer_text[:47] + "..."
    create_event(
        db,
        story_id=story_id,
        character_id=character_id,
        relationship_id=relationship_id,
        event_type=EventTypeEnum.QUESTION_ANSWERED,
        title="Discovery Answered",
        description=f"{question_text} - {short_answer}",
    )

    unlocked_events = []

    # Evaluate patterns and insights proactively if it's a character answer
    if character_id:
        from app.services.report_builder import get_answer_text

        answers = {
            "char_lie": get_answer_text(db, "char_lie", character_id=character_id),
            "char_wound": get_answer_text(db, "char_wound", character_id=character_id),
            "char_fear": get_answer_text(db, "char_fear", character_id=character_id),
            "char_consequence": get_answer_text(db, "char_consequence", character_id=character_id),
            "char_relationship_pattern": get_answer_text(db, "char_relationship_pattern", character_id=character_id),
        }

        # Check pattern emerging
        pattern_fields = get_pattern_emerging_fields(db, character_id, answers)
        if pattern_fields["pattern_name"] != "Emotional Defense Emerging":
            # Check if this exact pattern was already recorded
            existing = (
                db.query(DiscoveryEvent)
                .filter(
                    DiscoveryEvent.character_id == character_id,
                    DiscoveryEvent.event_type == EventTypeEnum.PATTERN_EMERGING,
                    DiscoveryEvent.title == f"Pattern: {pattern_fields['pattern_name']}",
                )
                .first()
            )
            if not existing:
                new_event = create_event(
                    db,
                    story_id=story_id,
                    character_id=character_id,
                    event_type=EventTypeEnum.PATTERN_EMERGING,
                    title=f"Pattern: {pattern_fields['pattern_name']}",
                    description=pattern_fields["insight"],
                )
                unlocked_events.append(new_event)

        # Check insights
        insight_fields = get_character_deterministic_fields(db, character_id, answers)

        # Example insight: Central Conflict
        if (
            insight_fields["central_conflict"] != "Not discovered yet."
            and "need" not in insight_fields["central_conflict"].lower()
        ):
            # A valid insight has been generated
            insight_title = "Insight Unlocked: Central Conflict"
            existing = (
                db.query(DiscoveryEvent)
                .filter(
                    DiscoveryEvent.character_id == character_id,
                    DiscoveryEvent.event_type == EventTypeEnum.INSIGHT_UNLOCKED,
                    DiscoveryEvent.title == insight_title,
                )
                .first()
            )
            if not existing:
                new_event = create_event(
                    db,
                    story_id=story_id,
                    character_id=character_id,
                    event_type=EventTypeEnum.INSIGHT_UNLOCKED,
                    title=insight_title,
                    description=insight_fields["central_conflict"],
                )
                unlocked_events.append(new_event)

    return unlocked_events
