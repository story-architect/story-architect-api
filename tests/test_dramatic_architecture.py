from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.models import Character, DiscoveryAnswer, DiscoveryQuestion, Story


def test_dramatic_architecture_overrides_and_regeneration(client: TestClient, db: Session):
    story = Story(title="Dramatic Story")
    db.add(story)
    db.commit()

    char = Character(name="Dramatic Character", age=30, role="MAIN_CHARACTER", story_id=story.id)
    db.add(char)
    db.commit()

    q_lie = DiscoveryQuestion(
        flow_type="CHARACTER", question_key="char_lie", question_text="What is the lie?", order_index=1
    )
    db.add(q_lie)
    db.commit()

    ans_lie = DiscoveryAnswer(
        story_id=story.id, character_id=char.id, question_id=q_lie.id, selected_answer="If I am perfect, nothing can go wrong."
    )
    db.add(ans_lie)
    db.commit()

    # Generate the initial report
    res = client.post(f"/api/v1/characters/{char.id}/generate-report")
    assert res.status_code == 200
    report_data = res.json()
    report_id = report_data["id"]

    # Verify generated fields
    assert report_data["narrative_consequence"] == "insights.character.perfection.narrative_consequence"

    # Step 1: Add custom overrides
    res = client.patch(
        f"/api/v1/characters/{report_id}/interpretations",
        json={
            "narrative_consequence_custom": "They alienate themselves custom.",
            "transformation_path_custom": "Must learn custom.",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["narrative_consequence_custom"] == "They alienate themselves custom."

    # Step 2: Test that custom overrides survive regeneration
    res = client.post(f"/api/v1/characters/{char.id}/generate-report")
    assert res.status_code == 200
    data = res.json()
    assert data["narrative_consequence_custom"] == "They alienate themselves custom."
    assert not data["custom_outdated_fields"]  # Should be empty because the upstream answer didn't change

    # Step 3: Change upstream answer and verify outdated marking
    ans_lie.selected_answer = "I don't need anyone."
    db.commit()

    res = client.post(f"/api/v1/characters/{char.id}/generate-report")
    assert res.status_code == 200
    data = res.json()
    assert data["narrative_consequence_custom"] == "They alienate themselves custom."  # Survived
    assert data["custom_outdated_fields"]["narrative_consequence_custom"] is True  # Marked outdated
    assert data["custom_outdated_fields"]["transformation_path_custom"] is True  # Marked outdated

    # Step 4: Clear outdated interpretations
    res = client.patch(
        f"/api/v1/characters/{report_id}/interpretations", json={"clear_outdated": ["narrative_consequence_custom"]}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["narrative_consequence_custom"] == "They alienate themselves custom."
    assert "narrative_consequence_custom" not in data["custom_outdated_fields"]
    assert data["custom_outdated_fields"]["transformation_path_custom"] is True  # Still outdated

    # Step 5: Replace an interpretation
    res = client.patch(
        f"/api/v1/characters/{report_id}/interpretations",
        json={"transformation_path_custom": "New custom after refresh"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["transformation_path_custom"] == "New custom after refresh"
    assert "transformation_path_custom" not in data["custom_outdated_fields"]  # Automatically cleared outdated flag

    # Step 6: Verify transformation backward compatibility
    # Ensure transformation is preserved in the schema
    assert "transformation" in data
