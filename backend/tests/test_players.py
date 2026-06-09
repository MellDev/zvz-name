from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_player_requires_body():
    response = client.post('/api/players', json={})
    assert response.status_code == 422
