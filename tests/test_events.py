from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import DiscoveryEvent, DiscoveryQuestion


def test_discovery_events_and_feed(client: TestClient, db: Session):
    # 1. Create Story
    res = client.post("/api/v1/stories", json={"title": "Event Story"})
    assert res.status_code == 200
    story_id = res.json()["id"]

    # 2. Create Character -> should trigger CHARACTER_CREATED
    res = client.post(f"/api/v1/stories/{story_id}/characters", json={"name": "Event Char", "role": "MAIN_CHARACTER"})
    assert res.status_code == 200
    char_id = res.json()["id"]

    import uuid

    # Verify event
    events = db.query(DiscoveryEvent).filter(DiscoveryEvent.story_id == uuid.UUID(story_id)).all()
    assert len(events) == 1
    assert events[0].event_type == "CHARACTER_CREATED"

    # 3. Create Discovery Questions
    q_lie = DiscoveryQuestion(flow_type="CHARACTER", question_key="char_lie", question_text="Lie?", order_index=1)
    db.add(q_lie)
    db.commit()

    # 4. Answer Question -> should trigger QUESTION_ANSWERED and PATTERN_EMERGING (if keyword matches)
    # Using 'perfect' keyword to trigger "Conditional Worth" pattern
    res = client.post(
        "/api/v1/discovery/answers",
        json={
            "story_id": story_id,
            "character_id": char_id,
            "question_id": str(q_lie.id),
            "selected_answer": "I must be perfect to be loved.",
        },
    )
    assert res.status_code == 200

    events = (
        db.query(DiscoveryEvent)
        .filter(DiscoveryEvent.story_id == uuid.UUID(story_id))
        .order_by(DiscoveryEvent.created_at)
        .all()
    )

    # We expect 3 events total: CHARACTER_CREATED, QUESTION_ANSWERED, PATTERN_EMERGING
    # Let's verify the feed endpoint
    res = client.get(f"/api/v1/stories/{story_id}/activity-feed")
    assert res.status_code == 200
    feed = res.json()
    assert len(feed) >= 3  # Character created + Question + Pattern

    event_types = [item["event_type"] for item in feed]
    assert "CHARACTER_CREATED" in event_types
    assert "QUESTION_ANSWERED" in event_types
    assert "PATTERN_EMERGING" in event_types

    # Check Pulse
    res = client.get(f"/api/v1/characters/{char_id}/pulse")
    assert res.status_code == 200
    pulse = res.json()
    assert pulse["lie"] == "I must be perfect to be loved."
    assert pulse["progress"] > 0
