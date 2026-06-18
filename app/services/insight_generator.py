"""
Insight Generator
=================
Thin adapter layer between the report builder and the Pattern Engine.

This module no longer contains any pattern definitions or keyword matching.
All pattern logic lives in app/pattern_library/.

The functions in this module preserve the same return dict shape as before
so that report_builder.py requires minimal changes.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.pattern_library.engine import (
    PatternResult,
    detect_character_pattern,
    detect_relationship_pattern,
)

UNDISCOVERED_VALUES = {"", "Not discovered yet."}


def _clean_answers(answers: dict) -> dict:
    return {
        key: "" if not isinstance(value, str) or value.strip() in UNDISCOVERED_VALUES else value
        for key, value in answers.items()
    }


def get_character_deterministic_fields(db: Session, character_id: UUID, answers: dict) -> dict:
    """
    Generate deterministic fields for a character based on their discovery answers.

    answers: dict mapping question_key -> answer_text
    e.g. {"char_lie": "...", "char_fear": "...", "char_wound": "..."}

    Returns a dict of i18n key strings plus pattern metadata.
    """
    result: PatternResult = detect_character_pattern(_clean_answers(answers))

    keys = result.final_insight_keys

    return {
        # Report fields (i18n key strings)
        "story_consequence": keys.get("consequence", "insights.character.default.consequence"),
        "relationship_pattern": keys.get(
            "relationship_pattern",
            "insights.character.default.relationship_pattern",
        ),
        "dramatic_potential": keys.get("dramatic_potential", "insights.character.default.dramatic_potential"),
        "inciting_relationship": keys.get(
            "inciting_relationship",
            "insights.character.default.inciting_relationship",
        ),
        "central_conflict": keys.get("central_conflict", "insights.character.default.central_conflict"),
        "narrative_consequence": keys.get(
            "narrative_consequence",
            "insights.character.default.narrative_consequence",
        ),
        "conflict_created": keys.get("conflict_created", "insights.character.default.conflict_created"),
        "pressure_point": keys.get("pressure_point", "insights.character.default.pressure_point"),
        "transformation_path": keys.get(
            "transformation_path",
            "insights.character.default.transformation_path",
        ),
        # Static summary keys (same for all patterns)
        "story_engine_summary": "insights.character.summary.story_engine",
        "story_beginning_summary": "insights.character.summary.story_beginning",
        # Pattern metadata (new fields — stored in report)
        "pattern_detected": result.pattern_detected,
        "pattern_version": result.pattern_version,
        "composition_detected": (result.composition_detected.composition_key if result.composition_detected else None),
    }


def get_relationship_deterministic_fields(db: Session, relationship_id: UUID, answers: dict) -> dict:
    """
    Generate deterministic fields for a relationship based on discovery answers.

    answers: dict mapping question_key -> answer_text
    """
    result: PatternResult = detect_relationship_pattern(_clean_answers(answers))

    keys = result.final_insight_keys

    return {
        # Report fields
        "consequence_summary": keys.get("consequence", "insights.relationship.default.consequence"),
        "relationship_risk": keys.get("risk", "insights.relationship.default.risk"),
        "relationship_pattern": keys.get("pattern", "insights.relationship.default.pattern"),
        # Pattern metadata
        "pattern_detected": result.pattern_detected,
        "pattern_version": result.pattern_version,
        "composition_detected": (result.composition_detected.composition_key if result.composition_detected else None),
    }


def get_pattern_emerging_fields(db: Session, character_id: UUID, answers: dict) -> dict:
    """
    Generate Pattern Emerging screen fields based on discovery answers.
    Uses the same pattern engine — returns the pattern_name, insight, etc.
    from the detected pattern's insight_keys.
    """
    result: PatternResult = detect_character_pattern(_clean_answers(answers))
    keys = result.final_insight_keys

    return {
        "pattern_name": keys.get("pattern_name", "insights.patterns.emotional_defense.name"),
        "insight": keys.get("pattern_insight", "insights.patterns.emotional_defense.insight"),
        "supporting_text": keys.get(
            "pattern_supporting_text",
            "insights.patterns.emotional_defense.supporting_text",
        ),
        "next_discovery_hint": keys.get(
            "pattern_next_hint",
            "insights.patterns.emotional_defense.next_discovery_hint",
        ),
    }
