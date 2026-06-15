
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Character, DiscoveryAnswer, DiscoveryQuestion, Relationship, Story


def test_character_insights_missing_answers(client: TestClient, db: Session):
    # Setup
    story = Story(title="Test Story")
    db.add(story)
    db.commit()
    db.refresh(story)

    char = Character(name="John Doe", age=30, role="MAIN_CHARACTER", story_id=story.id)
    db.add(char)
    db.commit()
    db.refresh(char)

    # Missing answers should return 'Not discovered yet.'
    res = client.get(f"/api/v1/characters/{char.id}/story-engine")
    assert res.status_code == 200
    data = res.json()
    assert data["emotional_wound"] == "Not discovered yet."
    assert data["fear"] == "Not discovered yet."
    assert data["protective_lie"] == "Not discovered yet."


def test_character_insights_with_answers_and_custom(client: TestClient, db: Session):
    story = Story(title="Test Story")
    db.add(story)
    db.commit()

    char = Character(name="Jane Doe", age=25, role="MAIN_CHARACTER", story_id=story.id)
    db.add(char)
    db.commit()

    q_wound = DiscoveryQuestion(
        flow_type="CHARACTER", question_key="char_wound", question_text="What is the wound?", order_index=1
    )
    q_lie = DiscoveryQuestion(
        flow_type="CHARACTER", question_key="char_lie", question_text="What is the lie?", order_index=2
    )
    db.add_all([q_wound, q_lie])
    db.commit()

    # Custom answer should override selected_answer
    ans_wound = DiscoveryAnswer(
        story_id=story.id,
        character_id=char.id,
        question_id=q_wound.id,
        selected_answer="Ignored",
        custom_answer="Deep wound",
    )
    # Trigger the 'perfect' logic in insight_generator
    ans_lie = DiscoveryAnswer(
        story_id=story.id, character_id=char.id, question_id=q_lie.id, selected_answer="I must be perfect to be loved."
    )
    db.add_all([ans_wound, ans_lie])
    db.commit()

    res = client.get(f"/api/v1/characters/{char.id}/story-engine")
    assert res.status_code == 200
    data = res.json()
    assert data["emotional_wound"] == "Deep wound"  # Custom overridden
    assert data["protective_lie"] == "I must be perfect to be loved."

    # Check Why This Matters generated fields
    res = client.get(f"/api/v1/characters/{char.id}/why-this-matters")
    assert res.status_code == 200
    data = res.json()
    assert "perfectionism" in data["dramatic_potential"]  # From the 'perfect' keyword logic

    # Check Narrative Consequence
    res = client.get(f"/api/v1/characters/{char.id}/narrative-consequence")
    assert res.status_code == 200
    data = res.json()
    assert "flawless" in data["story_consequence"]
    assert "i must be perfect" in data["main_statement"]

    # Check Where Story Begins
    res = client.get(f"/api/v1/characters/{char.id}/where-story-begins")
    assert res.status_code == 200
    data = res.json()
    assert "perfection and authenticity" in data["central_conflict"]


def test_relationship_insights(client: TestClient, db: Session):
    story = Story(title="Test Story")
    db.add(story)
    db.commit()

    char_a = Character(name="Alice", age=30, role="MAIN_CHARACTER", story_id=story.id)
    char_b = Character(name="Bob", age=30, role="SUPPORTING_CHARACTER", story_id=story.id)
    db.add_all([char_a, char_b])
    db.commit()

    rel = Relationship(
        character_a_id=char_a.id, character_b_id=char_b.id, relationship_type="FRIENDSHIP", story_id=story.id
    )
    db.add(rel)
    db.commit()

    q_protect = DiscoveryQuestion(
        flow_type="RELATIONSHIP", question_key="rel_protect", question_text="Protection pattern?", order_index=1
    )
    db.add(q_protect)
    db.commit()

    # Trigger the 'distance' logic
    ans_protect = DiscoveryAnswer(
        story_id=story.id,
        relationship_id=rel.id,
        question_id=q_protect.id,
        selected_answer="We keep distance to avoid fights.",
    )
    db.add(ans_protect)
    db.commit()

    res = client.get(f"/api/v1/relationships/{rel.id}/consequence")
    assert res.status_code == 200
    data = res.json()
    assert data["story_consequence"] == "We keep distance to avoid fights."
    assert "gulf" in data["consequence_summary"]  # Generated from 'distance' logic
    assert "severed" in data["relationship_risk"]  # Generated from 'distance' logic


def test_existing_report_endpoints_still_work(client: TestClient, db: Session):
    story = Story(title="Test Story")
    db.add(story)
    db.commit()

    char = Character(name="Existing", age=30, role="MAIN_CHARACTER", story_id=story.id)
    db.add(char)
    db.commit()

    res = client.post(f"/api/v1/characters/{char.id}/generate-report")
    assert res.status_code == 200
    data = res.json()
    assert data["character_id"] == str(char.id)
    assert "dramatic_potential" in data

    res2 = client.get(f"/api/v1/characters/{char.id}/report")
    assert res2.status_code == 200
    assert res2.json()["id"] == data["id"]


def test_pattern_emerging_insights(client: TestClient, db: Session):
    story = Story(title="Pattern Story")
    db.add(story)
    db.commit()

    char = Character(name="Pattern Char", age=20, role="MAIN_CHARACTER", story_id=story.id)
    db.add(char)
    db.commit()

    q_fear = DiscoveryQuestion(flow_type="CHARACTER", question_key="char_fear", question_text="Fear?", order_index=1)
    q_lie = DiscoveryQuestion(flow_type="CHARACTER", question_key="char_lie", question_text="Lie?", order_index=2)
    db.add_all([q_fear, q_lie])
    db.commit()

    # Default fallback
    res = client.get(f"/api/v1/characters/{char.id}/pattern-emerging")
    assert res.status_code == 200
    assert res.json()["pattern_name"] == "Emotional Defense Emerging"

    # Match protective lie 'perfect'
    ans_lie = DiscoveryAnswer(
        story_id=story.id, character_id=char.id, question_id=q_lie.id, selected_answer="I must be perfect."
    )
    db.add(ans_lie)
    db.commit()

    from app.models import CharacterArchitectureReport

    db.query(CharacterArchitectureReport).filter(CharacterArchitectureReport.character_id == char.id).delete()
    db.commit()

    res = client.get(f"/api/v1/characters/{char.id}/pattern-emerging")
    assert res.status_code == 200
    assert res.json()["pattern_name"] == "Conditional Worth"

    # Custom answer overrides and matches 'abandon'
    ans_fear = DiscoveryAnswer(
        story_id=story.id,
        character_id=char.id,
        question_id=q_fear.id,
        selected_answer="Ignored",
        custom_answer="fear of abandonment",
    )
    db.add(ans_fear)

    # Let's change lie so it doesn't match first (protective lie takes precedence if it matches, but "I must be okay" won't match)
    ans_lie.selected_answer = "I must be okay."
    db.commit()

    # We need to recreate the report to pick up the new answers! Wait, the endpoint calls `generate_character_report` if NOT report.
    # Since we already generated it, we should delete the report or call generate directly to update.
    # We will test the endpoint by deleting the old report.
    from app.models import CharacterArchitectureReport

    db.query(CharacterArchitectureReport).filter(CharacterArchitectureReport.character_id == char.id).delete()
    db.commit()

    res = client.get(f"/api/v1/characters/{char.id}/pattern-emerging")
    assert res.status_code == 200
    assert res.json()["pattern_name"] == "Fear of Abandonment"
