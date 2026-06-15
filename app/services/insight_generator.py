from uuid import UUID
from sqlalchemy.orm import Session
from app.models import CharacterArchitectureReport, RelationshipArchitectureReport

def get_character_deterministic_fields(db: Session, character_id: UUID, answers: dict) -> dict:
    """
    Generate deterministic fields for a character based on their discovery answers.
    answers: dict mapping question_key -> answer_text
    """
    
    protective_lie = answers.get("char_lie", "Not discovered yet.").lower()
    
    # Defaults
    story_consequence = answers.get("char_consequence", "Not discovered yet.")
    relationship_pattern = answers.get("char_relationship_pattern", "Keeps people at a distance.")
    inciting_relationship = "Someone enters their life who refuses to leave."
    central_conflict = "They must choose between safety and connection."
    dramatic_potential = "Because this character fears their wound, they protect themselves. The more someone cares about them, the more likely they are to push them away. This creates the central emotional conflict of the story."
    
    # Keyword templates for protective lie
    if "don't need anyone" in protective_lie or "dont need anyone" in protective_lie or "do not need anyone" in protective_lie:
        story_consequence = "Every attempt to protect themselves creates the loneliness they fear."
        relationship_pattern = "Pushes away those who try to help."
        dramatic_potential = "Because this character fears abandonment, they protect themselves through independence. The more someone cares about them, the more likely they are to push them away. This creates the central emotional conflict of the story."
        inciting_relationship = "Someone enters their life who refuses to leave."
        central_conflict = "They must choose between safety and connection."
    elif "perfect" in protective_lie or "flawless" in protective_lie:
        story_consequence = "Every attempt to be flawless creates pressure they cannot survive."
        relationship_pattern = "Hides their true self to maintain an image."
        dramatic_potential = "Because this character fears judgment, they protect themselves through perfectionism. The closer someone gets, the harder they work to maintain the facade. This creates the central emotional conflict of the story."
        inciting_relationship = "Someone sees through their perfect facade and accepts their flaws."
        central_conflict = "They must choose between perfection and authenticity."
    elif "control" in protective_lie:
        story_consequence = "Every attempt to stay in control pushes them further from real connection."
        relationship_pattern = "Dictates terms of engagement to avoid vulnerability."
        dramatic_potential = "Because this character fears chaos, they protect themselves through control. The more they try to control their environment, the more chaotic their relationships become. This creates the central emotional conflict of the story."
        inciting_relationship = "An unpredictable element forces them to surrender control."
        central_conflict = "They must choose between control and trust."

    # For any answer that is "Not discovered yet.", keep the defaults or the original answer if provided.
    
    return {
        "story_consequence": story_consequence,
        "relationship_pattern": relationship_pattern,
        "dramatic_potential": dramatic_potential,
        "inciting_relationship": inciting_relationship,
        "central_conflict": central_conflict,
        "story_engine_summary": "This is not a character trait. This is a story waiting to happen.",
        "story_beginning_summary": "Because this character fears their deepest wound, they protect themselves through their lie."
    }

def get_relationship_deterministic_fields(db: Session, relationship_id: UUID, answers: dict) -> dict:
    
    protection_pattern = answers.get("rel_protect", "Not discovered yet.").lower()
    
    # Defaults
    consequence_summary = "The more they try to protect each other, the less they truly know each other."
    relationship_risk = "If neither speaks honestly, they may lose the relationship they are both trying to save."
    relationship_pattern = "Honesty is sacrificed for comfort."
    
    if "truth" in protection_pattern or "hide" in protection_pattern:
        consequence_summary = "The more they try to protect each other, the less they truly know each other."
        relationship_risk = "If neither speaks honestly, they may lose the relationship they are both trying to save."
        relationship_pattern = "Honesty is sacrificed for comfort."
    elif "distance" in protection_pattern or "space" in protection_pattern:
        consequence_summary = "Their attempts to give each other space has created an unbridgeable gulf."
        relationship_risk = "They may drift so far apart that the connection is completely severed."
        relationship_pattern = "Intimacy is replaced by polite distance."
    elif "fix" in protection_pattern or "help" in protection_pattern:
        consequence_summary = "Their need to fix each other prevents them from accepting each other."
        relationship_risk = "They may destroy the relationship by trying to perfect it."
        relationship_pattern = "Support has become a form of control."

    return {
        "consequence_summary": consequence_summary,
        "relationship_risk": relationship_risk,
        "relationship_pattern": relationship_pattern
    }

def get_pattern_emerging_fields(db: Session, character_id: UUID, answers: dict) -> dict:
    """
    Generate dynamic Pattern Emerging screen fields based on discovery answers.
    """
    protective_lie = answers.get("char_lie", "").lower()
    deepest_fear = answers.get("char_wound", "").lower()
    
    # Check protective_lie first
    if "don't need anyone" in protective_lie or "dont need anyone" in protective_lie or "do not need anyone" in protective_lie:
        return {
            "pattern_name": "Protective Independence",
            "insight": "Your answers suggest this character protects themselves by refusing to need anyone.",
            "supporting_text": "Their independence may look like strength, but it also keeps others at a distance.",
            "next_discovery_hint": "Next, discover what this protection costs them."
        }
    
    if "perfect" in protective_lie or "flawless" in protective_lie:
        return {
            "pattern_name": "Conditional Worth",
            "insight": "Your answers suggest this character believes they must be perfect to be safe or accepted.",
            "supporting_text": "Their need to perform strength may hide a deeper fear of rejection.",
            "next_discovery_hint": "Next, discover what pressure this creates."
        }
        
    if "control" in protective_lie:
        return {
            "pattern_name": "Protective Control",
            "insight": "Your answers suggest this character feels safest when they can control what happens.",
            "supporting_text": "Control may protect them from chaos, but it can also prevent trust.",
            "next_discovery_hint": "Next, discover what this control damages."
        }
        
    if "not be seen" in protective_lie or "invisible" in protective_lie:
        return {
            "pattern_name": "Protective Invisibility",
            "insight": "Your answers suggest this character believes staying unseen keeps them safe.",
            "supporting_text": "They may avoid attention, intimacy, or risk because being noticed feels dangerous.",
            "next_discovery_hint": "Next, discover what they lose by hiding."
        }
        
    # Check deepest fear
    if "alone" in deepest_fear or "abandon" in deepest_fear:
        return {
            "pattern_name": "Fear of Abandonment",
            "insight": "Your answers suggest this character is shaped by the fear of being left alone.",
            "supporting_text": "They may push people away before anyone has the chance to leave.",
            "next_discovery_hint": "Next, discover how this fear creates conflict."
        }
        
    if "intimacy" in deepest_fear or "known" in deepest_fear:
        return {
            "pattern_name": "Fear of Being Known",
            "insight": "Your answers suggest this character fears closeness because being known feels unsafe.",
            "supporting_text": "They may want connection while resisting the vulnerability connection requires.",
            "next_discovery_hint": "Next, discover what kind of relationship challenges this creates."
        }
        
    # Fallback
    return {
        "pattern_name": "Emotional Defense Emerging",
        "insight": "Your answers suggest this character's wound is beginning to shape how they protect themselves.",
        "supporting_text": "Look at the connection between their fear and the way they choose to survive.",
        "next_discovery_hint": "Next, discover what this protection costs them."
    }

