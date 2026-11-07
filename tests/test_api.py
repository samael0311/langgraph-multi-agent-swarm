from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)


def test_api_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "service" in data


def test_api_swarm_execute_endpoint():
    payload = {
        "user_query": "Autonomous research swarm performance analysis",
        "constraints": ["Verify all citations", "Zero hallucinations"],
        "max_revisions": 2,
        "thread_id": "api_test_thread_01"
    }
    response = client.post("/swarm/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["hitl_approved"] is True
    assert data["final_report"] is not None
    assert "Executive Intelligence Dossier" in data["final_report"]["title"]


def test_api_get_thread_state():
    # First invoke a request to seed the thread
    thread_id = "api_seeded_thread_99"
    client.post("/swarm/execute", json={"user_query": "Seeded thread test", "thread_id": thread_id})

    # Retrieve checkpoint
    response = client.get(f"/swarm/state/{thread_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["thread_id"] == thread_id
    assert "values" in data
    assert data["values"]["user_query"] == "Seeded thread test"
