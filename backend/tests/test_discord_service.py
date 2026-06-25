from datetime import datetime

from app.models import Build, CheckIn, EventBuild, User, ZvZEvent
from app.services.discord import _build_message_content


def test_discord_message_includes_event_name_and_builds():
    event = ZvZEvent(
        title='AULA 8.3',
        content_type='Dungeon',
        caller='ZIULZ',
        event_date=datetime(2026, 6, 24, 23, 31),
        status='open',
        discord_message_extra='Saida de Martlock, tenham o lock.',
    )
    build = Build(
        id=10,
        name='Quebra-Reino',
        role='Suporte',
        weapon_name='Quebra-Reino',
        build_type='Dungeon',
        guild_id=1,
    )
    player = User(
        id=20,
        guild_id=1,
        discord_id='123456789012345678',
        discord_name='llxwk',
        albion_nick='llxwk',
    )
    checkin = CheckIn(
        guild_id=1,
        event_id=1,
        user_id=player.id,
        build_id=build.id,
        weapon_selected=build.name,
        mount_selected='Urso',
        player_nick_snapshot=player.albion_nick,
        user=player,
    )
    event.build_links = [EventBuild(build_id=build.id, build=build, max_slots=1)]
    event.checkins = [checkin]

    message = _build_message_content(event)

    assert '**Evento:** AULA 8.3' in message
    assert '**Mensagem:**' in message
    assert 'Saida de Martlock, tenham o lock.' in message
    assert '**Builds usadas:**' in message
    assert '- Quebra-Reino | Suporte | Quebra-Reino | 1/1 vaga(s)' in message
    assert '1. <@123456789012345678> (llxwk)' in message
