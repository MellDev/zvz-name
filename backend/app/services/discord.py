from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx

from app.core.config import settings
from app.models import ZvZEvent


def _format_event_datetime(value: datetime | None) -> str:
    if not value:
        return 'Nao informado'
    return value.strftime('%d/%m/%Y %H:%M')


def _event_build_lines(event: ZvZEvent) -> list[str]:
    links = sorted(
        event.build_links or [],
        key=lambda link: ((link.build.role if link.build else '') or '', (link.build.name if link.build else '') or ''),
    )
    checkins_by_build_id = {}
    for checkin in event.checkins or []:
        checkins_by_build_id.setdefault(checkin.build_id, []).append(checkin)

    lines = []
    for link in links:
        build = link.build
        slots = max(link.max_slots or 1, 1)
        checkins = sorted(
            checkins_by_build_id.get(link.build_id, []),
            key=lambda checkin: checkin.checkin_time or datetime.min,
        )
        if not build:
            lines.append(f'- Build removida ou indisponivel | {len(checkins)}/{slots} vaga(s)')
            lines.extend(_checkin_lines(checkins))
            continue

        role = build.role or 'funcao nao informada'
        weapon = build.weapon_name or 'arma nao informada'
        lines.append(f'- {build.name} | {role} | {weapon} | {len(checkins)}/{slots} vaga(s)')
        lines.extend(_checkin_lines(checkins))

    linked_build_ids = {link.build_id for link in links}
    unlinked_checkins = [
        checkin
        for checkin in event.checkins or []
        if checkin.build_id not in linked_build_ids
    ]
    if unlinked_checkins:
        lines.append('- Outros check-ins')
        lines.extend(_checkin_lines(unlinked_checkins))

    return lines


def _checkin_lines(checkins: list[Any]) -> list[str]:
    return [
        f'  {index}. {_checkin_player_label(checkin)}'
        for index, checkin in enumerate(checkins, start=1)
    ]


def _checkin_player_label(checkin: Any) -> str:
    player = checkin.user
    nick = checkin.player_nick_snapshot or (player.albion_nick if player else None) or 'Jogador sem nick'
    discord_id = str(player.discord_id or '').strip() if player else ''
    if discord_id.isdigit():
        return f'<@{discord_id}> ({nick})'
    return nick


def _truncate_discord_field(value: str, limit: int = 1024) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + '...'


def _truncate_discord_content(value: str, limit: int = 2000) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 32].rstrip() + '\n... mensagem resumida.'


def _build_message_content(event: ZvZEvent) -> str:
    build_lines = _event_build_lines(event)
    builds_text = '\n'.join(build_lines) if build_lines else 'Nenhuma build vinculada ainda.'
    extra_text = f'\n\n📝 **Mensagem:**\n{event.discord_message_extra.strip()}' if event.discord_message_extra else ''
    return _truncate_discord_content(
        f'📢 **Evento:** {event.title}\n'
        f'🗓️ **Data:** {_format_event_datetime(event.event_date)}\n'
        f'🧭 **Tipo:** {event.content_type}\n'
        f'👑 **Caller:** {event.caller or "Nao informado"}\n'
        f'📌 **Status:** {event.status}'
        f'{extra_text}\n\n'
        f'⚔️ **Builds usadas:**\n{builds_text}'
    )


def _build_embed(event: ZvZEvent) -> dict[str, Any]:
    builds_text = '\n'.join(_event_build_lines(event)) or 'Nenhuma build vinculada ainda.'
    return {
        'title': event.title,
        'description': (
            f'Tipo: {event.content_type}\n'
            f'Caller: {event.caller or "Nao informado"}\n'
            f'Status: {event.status}\n'
            f'Data: {_format_event_datetime(event.event_date)}'
        ),
        'color': 0x5865F2,
        'fields': [
            {
                'name': 'Mensagem',
                'value': _truncate_discord_field(event.discord_message_extra or 'Sem mensagem extra.'),
                'inline': False,
            },
            {
                'name': 'Regras',
                'value': _truncate_discord_field(event.mount_requirement_note or 'Sem observacoes adicionais.'),
                'inline': False,
            },
            {
                'name': 'Builds usadas',
                'value': _truncate_discord_field(builds_text),
                'inline': False,
            },
        ],
    }


def _webhook_url_with_wait(url: str) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query['wait'] = 'true'
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _webhook_message_url(url: str, message_id: str) -> str:
    parts = urlsplit(url)
    path = parts.path.rstrip('/') + f'/messages/{message_id}'
    return urlunsplit((parts.scheme, parts.netloc, path, '', parts.fragment))


def _discord_message_url(channel_id: str, message_id: str) -> str | None:
    guild_id = str(settings.DISCORD_DEFAULT_GUILD_ID or '')
    if not guild_id or not channel_id or not message_id:
        return None
    return f'https://discord.com/channels/{guild_id}/{channel_id}/{message_id}'


def publish_event_to_discord(event: ZvZEvent, db: Any | None = None) -> dict[str, Any]:
    if not settings.DISCORD_WEBHOOK_URL and not (settings.DISCORD_BOT_TOKEN and settings.DISCORD_ANNOUNCEMENT_CHANNEL_ID):
        return {'enabled': False, 'reason': 'Discord integration is not configured'}

    payload = {
        'content': _build_message_content(event),
        'embeds': [_build_embed(event)],
        'allowed_mentions': {'parse': ['users']},
    }

    try:
        if settings.DISCORD_WEBHOOK_URL:
            if event.discord_message_id:
                response = httpx.patch(
                    _webhook_message_url(settings.DISCORD_WEBHOOK_URL, event.discord_message_id),
                    json=payload,
                    timeout=10.0,
                )
            else:
                response = httpx.post(_webhook_url_with_wait(settings.DISCORD_WEBHOOK_URL), json=payload, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            message_id = str(data.get('id') or '')
            channel_id = str(data.get('channel_id') or '')
            message_url = _discord_message_url(channel_id, message_id)
        else:
            headers = {'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}'}
            channel_id = str(settings.DISCORD_ANNOUNCEMENT_CHANNEL_ID)
            if event.discord_message_id and event.discord_channel_id:
                response = httpx.patch(
                    f'https://discord.com/api/v10/channels/{event.discord_channel_id}/messages/{event.discord_message_id}',
                    headers=headers,
                    json=payload,
                    timeout=10.0,
                )
            else:
                response = httpx.post(
                    f'https://discord.com/api/v10/channels/{channel_id}/messages',
                    headers=headers,
                    json=payload,
                    timeout=10.0,
                )
            response.raise_for_status()
            data = response.json()
            message_id = str(data.get('id') or '')
            channel_id = str(data.get('channel_id') or '')
            message_url = _discord_message_url(channel_id, message_id)
    except Exception as exc:  # pragma: no cover - external integration guard
        return {'enabled': False, 'reason': str(exc)}

    if db is not None:
        event.discord_message_id = message_id
        event.discord_channel_id = channel_id
        event.discord_message_url = message_url
        event.discord_last_sync_at = datetime.utcnow()
        db.add(event)
        db.flush()

    return {
        'enabled': True,
        'message_id': message_id,
        'channel_id': channel_id,
        'message_url': message_url,
    }
