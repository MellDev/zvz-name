from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_event_publishes_to_discord_when_service_is_enabled():
    fake_user = type('UserStub', (), {'id': 1, 'is_staff': True, 'role': 'staff'})()

    with patch('app.api.routes.events.publish_event_to_discord', return_value={
        'message_id': '123456',
        'channel_id': '654321',
        'message_url': 'https://discord.com/channels/1/654321/123456',
    }) as publish_mock:
        app.dependency_overrides[app.api.routes.events.require_staff] = lambda: fake_user
        try:
            response = client.post('/api/events/', json={
                'guild_id': 1,
                'title': 'Avalon 8.2',
                'content_type': 'Dungeon',
                'event_date': '2026-06-13T23:30:00',
                'status': 'open',
            })
        finally:
            app.dependency_overrides.clear()

    assert response.status_code == 201
    payload = response.json()
    assert publish_mock.called
    assert payload['discord_message_id'] == '123456'
    assert payload['discord_channel_id'] == '654321'
    assert payload['discord_message_url'] == 'https://discord.com/channels/1/654321/123456'
