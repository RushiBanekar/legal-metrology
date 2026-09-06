from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_create_and_get_session_flow():
    # 1. Create Session
    create_res = client.post("/api/v1/sessions", json={"category": "packaged_food"})
    assert create_res.status_code == 201
    data = create_res.json()
    session_id = data["session_id"]
    assert session_id.startswith("sess_")

    # 2. Get Session Details
    get_res = client.get(f"/api/v1/sessions/{session_id}")
    assert get_res.status_code == 200
    assert get_res.json()["session_id"] == session_id

    # 3. Evaluate Session
    eval_res = client.post(f"/api/v1/sessions/{session_id}/evaluate")
    assert eval_res.status_code == 200
    assert "verdict" in eval_res.json()
