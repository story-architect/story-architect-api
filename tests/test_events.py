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
    q_wound = DiscoveryQuestion(flow_type="CHARACTER", question_key="char_wound", question_text="Wound?", order_index=1)
    q_fear = DiscoveryQuestion(flow_type="CHARACTER", question_key="char_fear", question_text="Fear?", order_index=2)
    q_lie = DiscoveryQuestion(flow_type="CHARACTER", question_key="char_lie", question_text="Lie?", order_index=3)
    db.add_all([q_wound, q_fear, q_lie])
    db.commit()

    # 4. Early answers should not interrupt the flow with a pattern milestone yet.
    res = client.post(
        "/api/v1/discovery/answers",
        json={
            "story_id": story_id,
            "character_id": char_id,
            "question_id": str(q_wound.id),
            "selected_answer": "They were valued only when they succeeded.",
        },
    )
    assert res.status_code == 200

    res = client.post(
        "/api/v1/discovery/answers",
        json={
            "story_id": story_id,
            "character_id": char_id,
            "question_id": str(q_fear.id),
            "selected_answer": "They fear becoming worthless if they fail.",
        },
    )
    assert res.status_code == 200

    res = client.get(f"/api/v1/stories/{story_id}/activity-feed")
    assert res.status_code == 200
    event_types = [item["event_type"] for item in res.json()]
    assert "PATTERN_EMERGING" not in event_types

    # 5. Answering the protective lie completes the synthesis inputs and can unlock a pattern.
    res = client.post(
        "/api/v1/discovery/answers",
        json={
            "story_id": story_id,
            "character_id": char_id,
            "question_id": str(q_lie.id),
            "selected_answer": "I must prove myself to be loved.",
        },
    )
    assert res.status_code == 200

    events = (
        db.query(DiscoveryEvent)
        .filter(DiscoveryEvent.story_id == uuid.UUID(story_id))
        .order_by(DiscoveryEvent.created_at)
        .all()
    )

    # Let's verify the feed endpoint
    res = client.get(f"/api/v1/stories/{story_id}/activity-feed")
    assert res.status_code == 200
    feed = res.json()
    assert len(feed) >= 5  # Character created + Questions + Pattern

    event_types = [item["event_type"] for item in feed]
    assert "CHARACTER_CREATED" in event_types
    assert "QUESTION_ANSWERED" in event_types
    assert "PATTERN_EMERGING" in event_types

    # Check Pulse
    res = client.get(f"/api/v1/characters/{char_id}/pulse")
    assert res.status_code == 200
    pulse = res.json()
    assert pulse["lie"] == "I must prove myself to be loved."
    assert pulse["progress"] > 0
