from fastapi.testclient import TestClient

def test_root_health_check(client: TestClient):
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Story Architect API"}

def test_create_and_get_story(client: TestClient):
    # Test Create
    story_data = {
        "title": "Test Story",
        "genre": "Sci-Fi",
        "one_sentence_premise": "A test premise."
    }
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
