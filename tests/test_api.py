from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.discovery import DiscoveryEvent, EventTypeEnum, FlowTypeEnum
from app.models.report import CharacterArchitectureReport


def test_root_health_check(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Story Architect API"}


def test_create_and_get_story(client: TestClient):
    # Test Create
    story_data = {"title": "Test Story", "genre": "Sci-Fi", "one_sentence_premise": "A test premise."}
    response = client.post("/api/v1/stories", json=story_data)
    assert response.status_code == 200
    created_story = response.json()
    assert created_story["title"] == "Test Story"
    assert "id" in created_story

    # Test Get
    story_id = created_story["id"]
    response = client.get(f"/api/v1/stories/{story_id}")
    assert response.status_code == 200
    fetched_story = response.json()
    assert fetched_story["id"] == story_id
    assert fetched_story["title"] == "Test Story"




def test_update_answer_marks_report_stale_and_generates_event(client: TestClient, db: Session):
    response = client.post("/api/v1/stories", json={"title": "Revision Story", "genre": "Sci-Fi"})
    story_id = response.json()["id"]

    response = client.post(f"/api/v1/stories/{story_id}/characters", json={"name": "Alice", "role": "MAIN_CHARACTER"})
    assert response.status_code == 200, response.json()
    character_id = response.json()["id"]

    from app.models import DiscoveryQuestion

    # Create Discovery Question
    q = DiscoveryQuestion(
        flow_type=FlowTypeEnum.CHARACTER_DISCOVERY.value, question_key="char_test", question_text="Test?", order_index=1
    )
    db.add(q)
    db.commit()

    questions_response = client.get(f"/api/v1/discovery/questions?flow_type={FlowTypeEnum.CHARACTER_DISCOVERY.value}")
    assert questions_response.status_code == 200, questions_response.json()
    question_id = questions_response.json()[0]["id"]

    answer_response = client.post(
        "/api/v1/discovery/answers",
        json={
            "story_id": story_id,
            "character_id": character_id,
            "question_id": question_id,
            "selected_answer": "Initial answer",
        },
    )
    assert answer_response.status_code == 200, answer_response.json()
    answer_id = answer_response.json()["id"]

    report_response = client.post(f"/api/v1/characters/{character_id}/generate-report")
    assert report_response.status_code == 200

    import uuid

    report = (
        db.query(CharacterArchitectureReport)
        .filter(CharacterArchitectureReport.character_id == uuid.UUID(character_id))
        .first()
    )
    assert report.is_stale is False

    update_response = client.put(
        f"/api/v1/discovery/answers/{answer_id}", json={"custom_answer": "Updated custom answer"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["custom_answer"] == "Updated custom answer"

    events = (
        db.query(DiscoveryEvent)
        .filter(
            DiscoveryEvent.character_id == uuid.UUID(character_id),
            DiscoveryEvent.event_type == EventTypeEnum.ANSWER_UPDATED,
        )
        .all()
    )
    assert len(events) > 0

    db.refresh(report)
    assert report.is_stale is True
    assert report.stale_reason == "answer_updated"

    report_response_2 = client.post(f"/api/v1/characters/{character_id}/generate-report")
    assert report_response_2.status_code == 200
    db.refresh(report)
    assert report.is_stale is False
    assert report.stale_reason is None
