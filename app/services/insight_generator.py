from uuid import UUID

from sqlalchemy.orm import Session


def get_character_deterministic_fields(db: Session, character_id: UUID, answers: dict) -> dict:
    """
    Generate deterministic fields for a character based on their discovery answers.
    answers: dict mapping question_key -> answer_text
    """

    protective_lie = answers.get("char_lie", "Not discovered yet.").lower()

    # Defaults
    story_consequence = "insights.character.default.consequence"
    relationship_pattern = "insights.character.default.relationship_pattern"
    inciting_relationship = "insights.character.default.inciting_relationship"
    central_conflict = "insights.character.default.central_conflict"
    dramatic_potential = "insights.character.default.dramatic_potential"

    narrative_consequence = "insights.character.default.narrative_consequence"
    conflict_created = "insights.character.default.conflict_created"
    pressure_point = "insights.character.default.pressure_point"
    transformation_path = "insights.character.default.transformation_path"

    # Keyword templates for protective lie
    if (
        "don't need anyone" in protective_lie
        or "dont need anyone" in protective_lie
        or "do not need anyone" in protective_lie
    ):
        story_consequence = "insights.character.independence.consequence"
        relationship_pattern = "insights.character.independence.relationship_pattern"
        dramatic_potential = "insights.character.independence.dramatic_potential"
        inciting_relationship = "insights.character.independence.inciting_relationship"
        central_conflict = "insights.character.independence.central_conflict"
        narrative_consequence = "insights.character.independence.narrative_consequence"
        conflict_created = "insights.character.independence.conflict_created"
        pressure_point = "insights.character.independence.pressure_point"
        transformation_path = "insights.character.independence.transformation_path"
    elif "perfect" in protective_lie or "flawless" in protective_lie:
        story_consequence = "insights.character.perfection.consequence"
        relationship_pattern = "insights.character.perfection.relationship_pattern"
        dramatic_potential = "insights.character.perfection.dramatic_potential"
        inciting_relationship = "insights.character.perfection.inciting_relationship"
        central_conflict = "insights.character.perfection.central_conflict"
        narrative_consequence = "insights.character.perfection.narrative_consequence"
        conflict_created = "insights.character.perfection.conflict_created"
        pressure_point = "insights.character.perfection.pressure_point"
        transformation_path = "insights.character.perfection.transformation_path"
    elif "control" in protective_lie:
        story_consequence = "insights.character.control.consequence"
        relationship_pattern = "insights.character.control.relationship_pattern"
        dramatic_potential = "insights.character.control.dramatic_potential"
        inciting_relationship = "insights.character.control.inciting_relationship"
        central_conflict = "insights.character.control.central_conflict"
        narrative_consequence = "insights.character.control.narrative_consequence"
        conflict_created = "insights.character.control.conflict_created"
        pressure_point = "insights.character.control.pressure_point"
        transformation_path = "insights.character.control.transformation_path"

    # For any answer that is "Not discovered yet.", keep the defaults or the original answer if provided.

    return {
        "story_consequence": story_consequence,
        "relationship_pattern": relationship_pattern,
        "dramatic_potential": dramatic_potential,
        "inciting_relationship": inciting_relationship,
        "central_conflict": central_conflict,
        "narrative_consequence": narrative_consequence,
        "conflict_created": conflict_created,
        "pressure_point": pressure_point,
        "transformation_path": transformation_path,
        "story_engine_summary": "insights.character.summary.story_engine",
        "story_beginning_summary": "insights.character.summary.story_beginning",
    }


def get_relationship_deterministic_fields(db: Session, relationship_id: UUID, answers: dict) -> dict:

    protection_pattern = answers.get("rel_protect", "Not discovered yet.").lower()

    # Defaults
    consequence_summary = "insights.relationship.default.consequence"
    relationship_risk = "insights.relationship.default.risk"
    relationship_pattern = "insights.relationship.default.pattern"

    if "truth" in protection_pattern or "hide" in protection_pattern:
        consequence_summary = "insights.relationship.hiding.consequence"
        relationship_risk = "insights.relationship.hiding.risk"
        relationship_pattern = "insights.relationship.hiding.pattern"
    elif "distance" in protection_pattern or "space" in protection_pattern:
        consequence_summary = "insights.relationship.distance.consequence"
        relationship_risk = "insights.relationship.distance.risk"
        relationship_pattern = "insights.relationship.distance.pattern"
    elif "fix" in protection_pattern or "help" in protection_pattern:
        consequence_summary = "insights.relationship.fixing.consequence"
        relationship_risk = "insights.relationship.fixing.risk"
        relationship_pattern = "insights.relationship.fixing.pattern"

    return {
        "consequence_summary": consequence_summary,
        "relationship_risk": relationship_risk,
        "relationship_pattern": relationship_pattern,
    }


def get_pattern_emerging_fields(db: Session, character_id: UUID, answers: dict) -> dict:
    """
    Generate dynamic Pattern Emerging screen fields based on discovery answers.
    """
    protective_lie = answers.get("char_lie", "").lower()
    deepest_fear = answers.get("char_wound", "").lower()

    # Check protective_lie first
    if (
        "don't need anyone" in protective_lie
        or "dont need anyone" in protective_lie
        or "do not need anyone" in protective_lie
    ):
        return {
            "pattern_name": "insights.patterns.protective_independence.name",
            "insight": "insights.patterns.protective_independence.insight",
            "supporting_text": "insights.patterns.protective_independence.supporting_text",
            "next_discovery_hint": "insights.patterns.protective_independence.next_discovery_hint",
        }

    if "perfect" in protective_lie or "flawless" in protective_lie:
        return {
            "pattern_name": "insights.patterns.conditional_worth.name",
            "insight": "insights.patterns.conditional_worth.insight",
            "supporting_text": "insights.patterns.conditional_worth.supporting_text",
            "next_discovery_hint": "insights.patterns.conditional_worth.next_discovery_hint",
        }

    if "control" in protective_lie:
        return {
            "pattern_name": "insights.patterns.protective_control.name",
            "insight": "insights.patterns.protective_control.insight",
            "supporting_text": "insights.patterns.protective_control.supporting_text",
            "next_discovery_hint": "insights.patterns.protective_control.next_discovery_hint",
        }

    if "not be seen" in protective_lie or "invisible" in protective_lie:
        return {
            "pattern_name": "insights.patterns.protective_invisibility.name",
            "insight": "insights.patterns.protective_invisibility.insight",
            "supporting_text": "insights.patterns.protective_invisibility.supporting_text",
            "next_discovery_hint": "insights.patterns.protective_invisibility.next_discovery_hint",
        }

    # Check deepest fear
    if "alone" in deepest_fear or "abandon" in deepest_fear:
        return {
            "pattern_name": "insights.patterns.fear_abandonment.name",
            "insight": "insights.patterns.fear_abandonment.insight",
            "supporting_text": "insights.patterns.fear_abandonment.supporting_text",
            "next_discovery_hint": "insights.patterns.fear_abandonment.next_discovery_hint",
        }

    if "intimacy" in deepest_fear or "known" in deepest_fear:
        return {
            "pattern_name": "insights.patterns.fear_being_known.name",
            "insight": "insights.patterns.fear_being_known.insight",
            "supporting_text": "insights.patterns.fear_being_known.supporting_text",
            "next_discovery_hint": "insights.patterns.fear_being_known.next_discovery_hint",
        }

    # Fallback
    return {
        "pattern_name": "insights.patterns.emotional_defense.name",
        "insight": "insights.patterns.emotional_defense.insight",
        "supporting_text": "insights.patterns.emotional_defense.supporting_text",
        "next_discovery_hint": "insights.patterns.emotional_defense.next_discovery_hint",
    }
