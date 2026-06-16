from uuid import UUID

from sqlalchemy.orm import Session

from app.models import (
    Character,
    CharacterArchitectureReport,
    DiscoveryAnswer,
    DiscoveryQuestion,
    Relationship,
    RelationshipArchitectureReport,
)
from app.services.insight_generator import get_character_deterministic_fields, get_relationship_deterministic_fields


def get_answer_text(db: Session, question_key: str, character_id: UUID = None, relationship_id: UUID = None) -> str:
    query = db.query(DiscoveryAnswer).join(DiscoveryQuestion).filter(DiscoveryQuestion.question_key == question_key)

    if character_id:
        query = query.filter(DiscoveryAnswer.character_id == character_id)
    elif relationship_id:
        query = query.filter(DiscoveryAnswer.relationship_id == relationship_id)

    answer = query.first()

    if not answer:
        return "Not discovered yet."

    # Prioritize custom answer over selected answer
    if answer.custom_answer:
        return answer.custom_answer
    elif answer.selected_answer:
        return answer.selected_answer
    else:
        return "Not discovered yet."


def generate_character_report(db: Session, character_id: UUID) -> CharacterArchitectureReport:
    character = db.query(Character).filter(Character.id == character_id).first()

    role_str = character.role.value if hasattr(character.role, "value") else character.role
    character_core = f"{character.name}, {character.age} - {role_str.replace('_', ' ').title()}" + (
        f" ({character.archetype})" if character.archetype else ""
    )

    emotional_wound = get_answer_text(db, "char_wound", character_id=character_id)
    deepest_fear = get_answer_text(db, "char_fear", character_id=character_id)
    protective_lie = get_answer_text(db, "char_lie", character_id=character_id)
    behavior = get_answer_text(db, "char_behavior", character_id=character_id)
    narrative_consequence = get_answer_text(db, "char_consequence", character_id=character_id)
    conflict_created = get_answer_text(db, "char_conflict", character_id=character_id)
    transformation = get_answer_text(db, "char_transformation", character_id=character_id)

    answers = {
        "char_lie": protective_lie,
        "char_consequence": narrative_consequence,
        "char_relationship_pattern": get_answer_text(db, "char_relationship_pattern", character_id=character_id),
    }
    insights = get_character_deterministic_fields(db, character_id, answers)

    # Check if report already exists
    report = (
        db.query(CharacterArchitectureReport).filter(CharacterArchitectureReport.character_id == character_id).first()
    )

    if report:
        outdated_fields = report.custom_outdated_fields or {}

        if report.narrative_consequence_custom and report.narrative_consequence != insights["narrative_consequence"]:
            outdated_fields["narrative_consequence_custom"] = True
        if report.conflict_created_custom and report.conflict_created != insights["conflict_created"]:
            outdated_fields["conflict_created_custom"] = True
        if report.pressure_point_custom and report.pressure_point != insights["pressure_point"]:
            outdated_fields["pressure_point_custom"] = True
        if report.transformation_path_custom and report.transformation_path != insights["transformation_path"]:
            outdated_fields["transformation_path_custom"] = True

        report.custom_outdated_fields = outdated_fields

        report.character_core = character_core
        report.emotional_wound = emotional_wound
        report.deepest_fear = deepest_fear
        report.protective_lie = protective_lie
        report.behavior = behavior
        report.narrative_consequence = insights["narrative_consequence"]
        report.conflict_created = insights["conflict_created"]
        report.pressure_point = insights["pressure_point"]
        report.transformation = transformation
        report.transformation_path = insights["transformation_path"]
        report.relationship_pattern = insights["relationship_pattern"]
        report.story_engine_summary = insights["story_engine_summary"]
        report.dramatic_potential = insights["dramatic_potential"]
        report.inciting_relationship = insights["inciting_relationship"]
        report.central_conflict = insights["central_conflict"]
        report.story_beginning_summary = insights["story_beginning_summary"]
        report.is_stale = False
        report.stale_reason = None
    else:
        report = CharacterArchitectureReport(
            character_id=character_id,
            character_core=character_core,
            emotional_wound=emotional_wound,
            deepest_fear=deepest_fear,
            protective_lie=protective_lie,
            behavior=behavior,
            narrative_consequence=insights["narrative_consequence"],
            conflict_created=insights["conflict_created"],
            pressure_point=insights["pressure_point"],
            transformation=transformation,
            transformation_path=insights["transformation_path"],
            relationship_pattern=insights["relationship_pattern"],
            story_engine_summary=insights["story_engine_summary"],
            dramatic_potential=insights["dramatic_potential"],
            inciting_relationship=insights["inciting_relationship"],
            central_conflict=insights["central_conflict"],
            story_beginning_summary=insights["story_beginning_summary"],
            is_stale=False,
            stale_reason=None,
            custom_outdated_fields={},
        )
        db.add(report)

    db.commit()
    db.refresh(report)
    return report


def generate_relationship_report(db: Session, relationship_id: UUID) -> RelationshipArchitectureReport:
    # Check if relationship exists
    relationship = db.query(Relationship).filter(Relationship.id == relationship_id).first()
    if not relationship:
        return None

    # Defaulting the emotional_effect to combine answers from both A -> B and B -> A truth.
    truth_a_b = get_answer_text(db, "rel_truth_a", relationship_id=relationship_id)
    truth_b_a = get_answer_text(db, "rel_truth_b", relationship_id=relationship_id)
    char_a_name = relationship.character_a.name if relationship.character_a else "Character A"
    char_b_name = relationship.character_b.name if relationship.character_b else "Character B"
    combined_emotional_effect = f"Truth {char_a_name} hides: {truth_a_b}\nTruth {char_b_name} hides: {truth_b_a}"
    if truth_a_b == "Not discovered yet." and truth_b_a == "Not discovered yet.":
        combined_emotional_effect = "Not discovered yet."

    current_result = get_answer_text(db, "rel_importance", relationship_id=relationship_id)
    story_consequence = get_answer_text(db, "rel_protect", relationship_id=relationship_id)
    relationship_law = get_answer_text(db, "rel_misunderstanding", relationship_id=relationship_id)
    current_relationship_risk = get_answer_text(db, "rel_risk", relationship_id=relationship_id)
    turning_point = get_answer_text(db, "rel_truth_demand", relationship_id=relationship_id)

    answers = {"rel_protect": story_consequence}
    insights = get_relationship_deterministic_fields(db, relationship_id, answers)

    report = (
        db.query(RelationshipArchitectureReport)
        .filter(RelationshipArchitectureReport.relationship_id == relationship_id)
        .first()
    )

    if report:
        report.current_result = current_result
        report.emotional_effect = combined_emotional_effect
        report.story_consequence = story_consequence
        report.current_relationship_risk = current_relationship_risk
        report.turning_point = turning_point
        report.relationship_law = relationship_law
        report.relationship_risk = insights["relationship_risk"]
        report.relationship_pattern = insights["relationship_pattern"]
        report.consequence_summary = insights["consequence_summary"]
        report.is_stale = False
        report.stale_reason = None
    else:
        report = RelationshipArchitectureReport(
            relationship_id=relationship_id,
            current_result=current_result,
            emotional_effect=combined_emotional_effect,
            story_consequence=story_consequence,
            current_relationship_risk=current_relationship_risk,
            turning_point=turning_point,
            relationship_law=relationship_law,
            relationship_risk=insights["relationship_risk"],
            relationship_pattern=insights["relationship_pattern"],
            consequence_summary=insights["consequence_summary"],
            is_stale=False,
            stale_reason=None,
        )
        db.add(report)

    db.commit()
    db.refresh(report)
    return report
