"""
Pattern Engine
==============
Scores patterns against a set of discovery answers, evaluates composition
rules, and returns a structured PatternResult.

Engine Flow:
  answers
    → score all patterns (keyword weight accumulation across all trigger fields)
    → sort by score descending
    → check composition library for matching top patterns
    → return structured result

This module contains ZERO business logic about specific patterns.
All pattern and composition definitions live in JSON files under
app/pattern_library/patterns/ and app/pattern_library/compositions/.

To add new patterns: add JSON files. No code changes required.
"""

import logging
from dataclasses import dataclass, field

from app.pattern_library.loader import (
    get_character_compositions,
    get_character_patterns,
    get_relationship_compositions,
    get_relationship_patterns,
)

logger = logging.getLogger(__name__)

# Minimum score for a pattern to be considered detected
SCORE_THRESHOLD = 0.5

# Maximum number of top patterns passed to composition evaluation
TOP_N_FOR_COMPOSITION = 3

# Default fallback pattern keys
DEFAULT_CHARACTER_PATTERN_KEY = "character.default"
DEFAULT_RELATIONSHIP_PATTERN_KEY = "relationship.default"


@dataclass
class ScoredPattern:
    pattern_key: str
    score: float
    version: int
    family: str
    insight_keys: dict


@dataclass
class CompositionMatch:
    composition_key: str
    confidence: str
    insight_key: str  # the composed insight i18n key


@dataclass
class PatternResult:
    """
    Full output of the pattern engine for one character or relationship.

    pattern_detected:   The winning pattern key (e.g. "character.guilt.self_preservation_as_betrayal")
    pattern_version:    Version number of the winning pattern file
    pattern_family:     Family name (e.g. "guilt")
    insight_keys:       Dict of all i18n keys from the winning pattern
    patterns_scored:    Ordered list of all scored patterns (for debug / analytics)
    composition_detected: The winning composition, if any
    final_insight_keys: Merged insight_keys (composition overrides individual where applicable)
    """

    pattern_detected: str
    pattern_version: int
    pattern_family: str
    insight_keys: dict
    patterns_scored: list[ScoredPattern] = field(default_factory=list)
    composition_detected: CompositionMatch | None = None
    final_insight_keys: dict = field(default_factory=dict)


def _score_pattern(answers: dict, pattern: dict) -> float:
    """
    Compute a numeric score for a single pattern against the provided answers.

    Each rule in the pattern specifies:
      - field:    which answer key to inspect
      - keywords: list of substrings to look for (case-insensitive)
      - weight:   points awarded per keyword hit
    """
    rules = pattern.get("rules", [])
    total_score = 0.0

    for rule in rules:
        field_key = rule.get("field", "")
        keywords = rule.get("keywords", [])
        weight = float(rule.get("weight", 1.0))
        answer_text = answers.get(field_key, "").lower()

        if not answer_text:
            continue

        for kw in keywords:
            if kw.lower() in answer_text:
                total_score += weight
                break  # one keyword hit per rule is enough

    return round(total_score, 3)


def score_patterns(answers: dict, patterns: list[dict]) -> list[ScoredPattern]:
    """
    Score all patterns against the answers and return them sorted
    by score descending. Patterns below SCORE_THRESHOLD are excluded
    unless they are the fallback default.
    """
    scored = []
    fallback = None

    for pattern in patterns:
        key = pattern.get("pattern_key", "")
        is_default = key.endswith(".default")

        score = _score_pattern(answers, pattern)

        sp = ScoredPattern(
            pattern_key=key,
            score=score,
            version=int(pattern.get("version", 1)),
            family=pattern.get("family", "default"),
            insight_keys=pattern.get("insight_keys", {}),
        )

        if is_default:
            fallback = sp
        elif score >= SCORE_THRESHOLD:
            scored.append(sp)

    # Sort by score descending
    scored.sort(key=lambda x: x.score, reverse=True)

    # Always append fallback at the end so there is always a result
    if fallback:
        scored.append(fallback)

    return scored


def evaluate_composition(
    top_patterns: list[ScoredPattern],
    compositions: list[dict],
) -> CompositionMatch | None:
    """
    Check if any composition rule is satisfied by the top scored patterns.

    A composition matches when ALL of its required pattern keys appear
    in the top_patterns list AND all contributing patterns meet the
    min_pattern_score threshold defined in the composition.

    Returns the first matching composition (sorted by confidence: high > medium > low),
    or None if no composition matches.
    """
    if len(top_patterns) < 2:
        return None

    top_pattern_keys = {sp.pattern_key for sp in top_patterns}
    score_by_key = {sp.pattern_key: sp.score for sp in top_patterns}

    confidence_order = {"high": 0, "medium": 1, "low": 2}
    sorted_compositions = sorted(
        compositions,
        key=lambda c: confidence_order.get(c.get("confidence", "low"), 9),
    )

    for comp in sorted_compositions:
        required_patterns = set(comp.get("patterns", []))
        min_score = float(comp.get("min_pattern_score", SCORE_THRESHOLD))

        if not required_patterns.issubset(top_pattern_keys):
            continue

        # All required patterns must meet the min score
        if not all(score_by_key.get(pk, 0.0) >= min_score for pk in required_patterns):
            continue

        return CompositionMatch(
            composition_key=comp["composition_key"],
            confidence=comp.get("confidence", "medium"),
            insight_key=comp.get("insight_key", ""),
        )

    return None


def detect_character_pattern(answers: dict) -> PatternResult:
    """
    Run the full character pattern detection pipeline.

    answers should be a dict mapping question_key → answer_text:
      char_wound, char_fear, char_lie, char_behavior,
      char_consequence, char_conflict, char_transformation
    """
    patterns = get_character_patterns()
    compositions = get_character_compositions()
    return _run_pipeline(
        answers=answers,
        patterns=patterns,
        compositions=compositions,
        default_key=DEFAULT_CHARACTER_PATTERN_KEY,
    )


def detect_relationship_pattern(answers: dict) -> PatternResult:
    """
    Run the full relationship pattern detection pipeline.

    answers should be a dict mapping question_key → answer_text:
      rel_importance, rel_truth_a, rel_truth_b, rel_protect,
      rel_misunderstanding, rel_risk, rel_truth_demand
    """
    patterns = get_relationship_patterns()
    compositions = get_relationship_compositions()
    return _run_pipeline(
        answers=answers,
        patterns=patterns,
        compositions=compositions,
        default_key=DEFAULT_RELATIONSHIP_PATTERN_KEY,
    )


def _run_pipeline(
    answers: dict,
    patterns: list[dict],
    compositions: list[dict],
    default_key: str,
) -> PatternResult:
    """Internal pipeline shared by character and relationship detection."""

    # Step 1: Score all patterns
    scored = score_patterns(answers, patterns)

    if not scored:
        logger.warning("No patterns available. Returning empty result.")
        return PatternResult(
            pattern_detected=default_key,
            pattern_version=1,
            pattern_family="default",
            insight_keys={},
            patterns_scored=[],
            composition_detected=None,
            final_insight_keys={},
        )

    # Step 2: Select winning pattern
    winner = scored[0]

    # Step 3: Evaluate composition on top N patterns
    top_n = scored[:TOP_N_FOR_COMPOSITION]
    composition = evaluate_composition(top_n, compositions)

    # Step 4: Build final insight keys
    # Start with the winner's keys and optionally overlay the composed insight
    final_keys = dict(winner.insight_keys)
    if composition and composition.insight_key:
        # The composition provides a single composed insight key that
        # overrides the narrative_consequence field specifically.
        # All other insight fields remain from the dominant pattern.
        final_keys["composed_insight"] = composition.insight_key

    logger.debug(
        "Pattern detected: %s (score=%.2f), composition: %s",
        winner.pattern_key,
        winner.score,
        composition.composition_key if composition else "none",
    )

    return PatternResult(
        pattern_detected=winner.pattern_key,
        pattern_version=winner.version,
        pattern_family=winner.family,
        insight_keys=winner.insight_keys,
        patterns_scored=scored,
        composition_detected=composition,
        final_insight_keys=final_keys,
    )
