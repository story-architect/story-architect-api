"""
Pattern Library Loader
======================
Recursively loads all pattern and composition JSON files from the
pattern_library directory tree and caches them in memory.

Patterns live in:  app/pattern_library/patterns/character/
                   app/pattern_library/patterns/relationship/

Compositions live in: app/pattern_library/compositions/character/
                      app/pattern_library/compositions/relationship/

Adding new patterns or compositions requires ONLY adding a JSON file.
No engine code changes are needed.
"""

import json
import logging
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

LIBRARY_ROOT = Path(__file__).parent


def _load_json_files(directory: Path) -> list[dict]:
    """Recursively load all .json files from a directory."""
    results = []
    if not directory.exists():
        logger.warning("Pattern library directory not found: %s", directory)
        return results
    for path in sorted(directory.rglob("*.json")):
        try:
            with open(path, encoding="utf-8-sig") as f:
                data = json.load(f)
                data["_source_file"] = str(path.relative_to(LIBRARY_ROOT))
                results.append(data)
        except Exception as exc:
            logger.error("Failed to load pattern file %s: %s", path, exc)
    logger.info("Loaded %d files from %s", len(results), directory)
    return results


@lru_cache(maxsize=1)
def get_character_patterns() -> list[dict]:
    """Return all character pattern definitions (cached)."""
    return _load_json_files(LIBRARY_ROOT / "patterns" / "character")


@lru_cache(maxsize=1)
def get_relationship_patterns() -> list[dict]:
    """Return all relationship pattern definitions (cached)."""
    return _load_json_files(LIBRARY_ROOT / "patterns" / "relationship")


@lru_cache(maxsize=1)
def get_character_compositions() -> list[dict]:
    """Return all character composition rules (cached)."""
    return _load_json_files(LIBRARY_ROOT / "compositions" / "character")


@lru_cache(maxsize=1)
def get_relationship_compositions() -> list[dict]:
    """Return all relationship composition rules (cached)."""
    return _load_json_files(LIBRARY_ROOT / "compositions" / "relationship")


def reload_library() -> None:
    """Clear the cache and force a reload of all library files.
    Useful during testing or after hot-editing pattern files in development.
    """
    get_character_patterns.cache_clear()
    get_relationship_patterns.cache_clear()
    get_character_compositions.cache_clear()
    get_relationship_compositions.cache_clear()
    logger.info("Pattern library cache cleared and will reload on next access.")
