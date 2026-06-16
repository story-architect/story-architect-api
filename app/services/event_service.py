import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.discovery import DiscoveryEvent, EventTypeEnum
from app.services.insight_generator import get_character_deterministic_fields, get_pattern_emerging_fields


def create_event(
    db: Session,
    story_id: uuid.UUID,
    event_type: EventTypeEnum,
    event_metadata: dict,
    character_id: Optional[uuid.UUID] = None,
    relationship_id: Optional[uuid.UUID] = None,
):
    event = DiscoveryEvent(
        story_id=story_id,
        character_id=character_id,
        relationship_id=relationship_id,
        event_type=event_type,
        event_metadata=event_metadata,
        title=None,
        description=None,
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
        event_metadata={"name": character_name},
    )


def handle_relationship_created(
    db: Session, story_id: uuid.UUID, relationship_id: uuid.UUID, char_a_name: str, char_b_name: str
):
    create_event(
        db,
        story_id=story_id,
        relationship_id=relationship_id,
        event_type=EventTypeEnum.RELATIONSHIP_CREATED,
        event_metadata={"charA": char_a_name, "charB": char_b_name},
    )


def handle_report_generated(
    db: Session,
    story_id: uuid.UUID,
    event_metadata: dict,
    character_id: Optional[uuid.UUID] = None,
    relationship_id: Optional[uuid.UUID] = None,
):
    create_event(
        db,
        story_id=story_id,
        character_id=character_id,
        relationship_id=relationship_id,
        event_type=EventTypeEnum.REPORT_GENERATED,
        event_metadata=event_metadata,
    )

def handle_dramatic_architecture_discovered(
    db: Session,
    story_id: uuid.UUID,
    event_metadata: dict,
    character_id: Optional[uuid.UUID] = None,
):
    create_event(
        db,
        story_id=story_id,
        character_id=character_id,
        event_type=EventTypeEnum.DRAMATIC_ARCHITECTURE_DISCOVERED,
        event_metadata=event_metadata,
    )

def handle_interpretation_revised(
    db: Session,
    story_id: uuid.UUID,
    event_metadata: dict,
    character_id: Optional[uuid.UUID] = None,
):
    create_event(
        db,
        story_id=story_id,
        character_id=character_id,
        event_type=EventTypeEnum.INTERPRETATION_REVISED,
        event_metadata=event_metadata,
    )


def handle_question_answered(
    db: Session,
    story_id: uuid.UUID,
    question_text: str,
    answer_text: str,
    character_id: Optional[uuid.UUID] = None,
    relationship_id: Optional[uuid.UUID] = None,
):
    create_event(
        db,
        story_id=story_id,
        character_id=character_id,
        relationship_id=relationship_id,
        event_type=EventTypeEnum.QUESTION_ANSWERED,
        event_metadata={
            "question": question_text,
            "answer": answer_text,
        },
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
        # Note: 'insights.patterns.emotional_defense.name' is the fallback pattern key
        if pattern_fields["pattern_name"] != "insights.patterns.emotional_defense.name":
            # Check if this exact pattern was already recorded
            existing_patterns = (
                db.query(DiscoveryEvent)
                .filter(
                    DiscoveryEvent.character_id == character_id,
                    DiscoveryEvent.event_type == EventTypeEnum.PATTERN_EMERGING,
                )
                .all()
            )
            already_recorded = any(
                e.event_metadata.get("pattern_key") == pattern_fields["pattern_name"] for e in existing_patterns
            )
            if not already_recorded:
                new_event = create_event(
                    db,
                    story_id=story_id,
                    character_id=character_id,
                    event_type=EventTypeEnum.PATTERN_EMERGING,
                    event_metadata={
                        "pattern_key": pattern_fields["pattern_name"],
                        "insight_key": pattern_fields["insight"],
                    },
                )
                unlocked_events.append(new_event)

        # Check insights
        insight_fields = get_character_deterministic_fields(db, character_id, answers)

        # Example insight: Central Conflict
        # Note: default central conflict key is "insights.character.default.central_conflict"
        if insight_fields["central_conflict"] != "insights.character.default.central_conflict":
            # A valid insight has been generated
            existing_insights = (
                db.query(DiscoveryEvent)
                .filter(
                    DiscoveryEvent.character_id == character_id,
                    DiscoveryEvent.event_type == EventTypeEnum.INSIGHT_UNLOCKED,
                )
                .all()
            )
            already_recorded = any(
                e.event_metadata.get("insight_key") == insight_fields["central_conflict"] for e in existing_insights
            )
            if not already_recorded:
                new_event = create_event(
                    db,
                    story_id=story_id,
                    character_id=character_id,
                    event_type=EventTypeEnum.INSIGHT_UNLOCKED,
                    event_metadata={
                        "insight_key": insight_fields["central_conflict"],
                    },
                )
                unlocked_events.append(new_event)

    return unlocked_events
