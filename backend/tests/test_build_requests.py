from app.schemas import BuildRequestCreate, BuildRequestUpdate


def test_build_request_update_accepts_weapon_power():
    payload = BuildRequestUpdate(status='approved', weapon_power=123)

    assert payload.status == 'approved'
    assert payload.weapon_power == 123


def test_build_request_create_allows_notes_and_weapon_power():
    payload = BuildRequestCreate(event_id=1, build_id=2, notes='Solicitando arma', weapon_power=250)

    assert payload.event_id == 1
    assert payload.build_id == 2
    assert payload.notes == 'Solicitando arma'
    assert payload.weapon_power == 250
