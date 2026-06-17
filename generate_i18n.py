import json
import os
from pathlib import Path

# Paths
BACKEND_DIR = Path("C:/Users/molk/Documents/projects/story_architect_backend")
FRONTEND_DIR = Path("C:/Users/molk/Documents/projects/story_architect_frontend")
PATTERN_LIB = BACKEND_DIR / "app" / "pattern_library"
EN_LOCALE = FRONTEND_DIR / "src" / "locales" / "en" / "insights.json"
FR_LOCALE = FRONTEND_DIR / "src" / "locales" / "fr" / "insights.json"


def get_nested_dict(d, keys):
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    return d, keys[-1]


def set_key(d, dot_notation_key, value):
    keys = dot_notation_key.split(".")
    # Drop the leading 'insights.' since the JSON file is already inside the insights namespace
    if keys[0] == "insights":
        keys = keys[1:]
    parent, final_key = get_nested_dict(d, keys)
    if final_key not in parent or parent[final_key] == "":
        parent[final_key] = value


def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    en_data = load_json(EN_LOCALE)
    fr_data = load_json(FR_LOCALE)

    # 1. Patterns
    patterns_dir = PATTERN_LIB / "patterns"
    for root, _, files in os.walk(patterns_dir):
        for f in files:
            if f.endswith(".json"):
                data = load_json(os.path.join(root, f))
                insight_keys = data.get("insight_keys", {})
                for field, dot_key in insight_keys.items():
                    # Generate a placeholder based on the key name
                    placeholder = f"[{field.replace('_', ' ').title()}]"
                    set_key(en_data, dot_key, placeholder)
                    set_key(fr_data, dot_key, f"[FR] {placeholder}")

    # 2. Compositions
    comps_dir = PATTERN_LIB / "compositions"
    for root, _, files in os.walk(comps_dir):
        for f in files:
            if f.endswith(".json"):
                data = load_json(os.path.join(root, f))
                dot_key = data.get("insight_key")
                if dot_key:
                    # Provide a better placeholder if possible
                    placeholder = f"[Composed Insight: {data.get('composition_key')}]"
                    set_key(en_data, dot_key, placeholder)
                    set_key(fr_data, dot_key, f"[FR] {placeholder}")

    save_json(EN_LOCALE, en_data)
    save_json(FR_LOCALE, fr_data)
    print("Successfully updated EN and FR insights.json with new pattern keys.")


if __name__ == "__main__":
    main()
