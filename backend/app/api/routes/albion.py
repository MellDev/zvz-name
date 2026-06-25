import httpx
from functools import lru_cache
import re
from fastapi import APIRouter, Query

router = APIRouter()

OPEN_ALBION_WEAPONS_URL = 'https://api.openalbion.com/api/v3/weapons'
OPEN_ALBION_ARMORS_URL = 'https://api.openalbion.com/api/v3/armors'
ALBION_ITEMS_DUMP_URL = 'https://raw.githubusercontent.com/ao-data/ao-bin-dumps/master/formatted/items.json'

FALLBACK_WEAPONS = [
    ('Chamador de Sombras', 'Shadowcaller', 'T4_2H_CURSEDSTAFF_MORGANA'),
    ('Quebra-Reinos', 'Realmbreaker', 'T4_2H_AXE_AVALON'),
    ('Prisma Permafrost', 'Permafrost Prism', 'T4_2H_ICECRYSTAL_UNDEAD'),
    ('Martelo Grande', 'Great Hammer', 'T4_2H_HAMMER'),
    ('Glaive da Fenda', 'Rift Glaive', 'T4_2H_WARBOW_HELL'),
]

CUSTOM_ITEMS = [
    {
        'base_en': 'Astral Staff',
        'base_pt': 'Cajado Astral',
        'category': 'Mage Weapons',
        'subcategory': 'Arcane Staff',
        'item_ids': [f'T{tier}_2H_ARCANESTAFF_CRYSTAL' for tier in range(4, 9)],
    },
    {
        'base_en': 'Blueflame Torch',
        'base_pt': 'Tocha Azul',
        'category': 'Off-Hands',
        'subcategory': 'Torch',
        'item_ids': [f'T{tier}_OFF_TORCH_CRYSTAL' for tier in range(4, 9)],
    },
]

TIER_PREFIXES = (
    "Beginner's ",
    "Novice's ",
    "Journeyman's ",
    "Adept's ",
    "Expert's ",
    "Master's ",
    "Grandmaster's ",
    "Elder's ",
)

WEAPON_TRANSLATIONS = {
    'Battleaxe': 'Machado de Batalha',
    'Greataxe': 'Machado Grande',
    'Halberd': 'Alabarda',
    'Carrioncaller': 'Chamador de Carnica',
    'Infernal Scythe': 'Foice Infernal',
    'Bear Paws': 'Patas de Urso',
    'Realmbreaker': 'Quebra-Reinos',
    'Broadsword': 'Espada Larga',
    'Claymore': 'Claymore',
    'Dual Swords': 'Espadas Duplas',
    'Clarent Blade': 'Lamina Clarent',
    'Carving Sword': 'Espada Entalhadora',
    'Galatine Pair': 'Par Galatino',
    'Kingmaker': 'Fazedor de Reis',
    'Great Hammer': 'Martelo Grande',
    'Hammer': 'Martelo',
    'Polehammer': 'Martelo de Haste',
    'Tombhammer': 'Martelo Tumular',
    'Forge Hammers': 'Martelos de Forja',
    'Grovekeeper': 'Guardiao do Bosque',
    'Heavy Mace': 'Maca Pesada',
    'Morning Star': 'Estrela da Manha',
    'Bedrock Mace': 'Maca Rocha-Firme',
    'Incubus Mace': 'Maca Incubus',
    'Camlann Mace': 'Maca Camlann',
    'Oathkeepers': 'Guardioes do Juramento',
    'Light Crossbow': 'Besta Leve',
    'Crossbow': 'Besta',
    'Heavy Crossbow': 'Besta Pesada',
    'Repeating Crossbow': 'Besta Repetidora',
    'Weeping Repeater': 'Repetidora Chorosa',
    'Boltcasters': 'Lancadores de Virotes',
    'Siegebow': 'Arco de Cerco',
    'Bow': 'Arco',
    'Warbow': 'Arco de Guerra',
    'Longbow': 'Arco Longo',
    'Whispering Bow': 'Arco Sussurrante',
    "Wailing Bow": 'Arco Lamentoso',
    'Bow of Badon': 'Arco de Badon',
    'Mistpiercer': 'Perfurador de Brumas',
    'Spear': 'Lanca',
    'Pike': 'Pique',
    'Glaive': 'Glaive',
    'Heron Spear': 'Lanca da Garca',
    'Spirithunter': 'Cacador de Espiritos',
    'Trinity Spear': 'Lanca da Trindade',
    'Daybreaker': 'Rompe-Aurora',
    'Dagger': 'Adaga',
    'Dagger Pair': 'Par de Adagas',
    'Claws': 'Garras',
    'Bloodletter': 'Sangradora',
    'Demonfang': 'Presa Demoniaca',
    'Bridled Fury': 'Furia Refreada',
    'Deathgivers': 'Doadoras de Morte',
    'Quarterstaff': 'Cajado de Combate',
    'Iron-clad Staff': 'Cajado Revestido de Ferro',
    'Double Bladed Staff': 'Cajado de Duas Laminas',
    'Black Monk Stave': 'Bastao do Monge Negro',
    'Soulscythe': 'Foice de Almas',
    'Grailseeker': 'Buscador do Graal',
    'Fire Staff': 'Cajado de Fogo',
    'Great Fire Staff': 'Cajado de Fogo Grande',
    'Infernal Staff': 'Cajado Infernal',
    'Wildfire Staff': 'Cajado Fogo Selvagem',
    'Brimstone Staff': 'Cajado Enxofre',
    'Blazing Staff': 'Cajado Ardente',
    'Dawnsong': 'Cancao da Aurora',
    'Frost Staff': 'Cajado de Gelo',
    'Great Frost Staff': 'Cajado de Gelo Grande',
    'Glacial Staff': 'Cajado Glacial',
    'Hoarfrost Staff': 'Cajado Geada',
    'Icicle Staff': 'Cajado de Carambano',
    'Permafrost Prism': 'Prisma Permafrost',
    'Chillhowl': 'Uivo Gelido',
    'Arcane Staff': 'Cajado Arcano',
    'Great Arcane Staff': 'Cajado Arcano Grande',
    'Enigmatic Staff': 'Cajado Enigmatico',
    'Witchwork Staff': 'Cajado de Bruxaria',
    'Occult Staff': 'Cajado Oculto',
    'Malevolent Locus': 'Locus Malevolente',
    'Evensong': 'Cancao do Crepusculo',
    'Cursed Staff': 'Cajado Amaldicoado',
    'Great Cursed Staff': 'Cajado Amaldicoado Grande',
    'Demonic Staff': 'Cajado Demonico',
    'Lifecurse Staff': 'Cajado Maldicao Vital',
    'Damnation Staff': 'Cajado da Condenacao',
    'Shadowcaller': 'Chamador de Sombras',
    'Holy Staff': 'Cajado Sagrado',
    'Great Holy Staff': 'Cajado Sagrado Grande',
    'Divine Staff': 'Cajado Divino',
    'Lifetouch Staff': 'Cajado Toque Vital',
    'Fallen Staff': 'Cajado Caido',
    'Redemption Staff': 'Cajado da Redencao',
    'Hallowfall': 'Queda Sagrada',
    'Nature Staff': 'Cajado da Natureza',
    'Great Nature Staff': 'Cajado da Natureza Grande',
    'Wild Staff': 'Cajado Selvagem',
    'Druidic Staff': 'Cajado Druidico',
    'Blight Staff': 'Cajado da Praga',
    'Rampant Staff': 'Cajado Rampante',
    'Ironroot Staff': 'Cajado Raiz de Ferro',
    'Prowling Staff': 'Cajado Espreitador',
    'Rootbound Staff': 'Cajado Raiz Presa',
    'Primal Staff': 'Cajado Primal',
    'Bloodmoon Staff': 'Cajado Lua Sangrenta',
    'Hellspawn Staff': 'Cajado Cria Infernal',
    'Earthrune Staff': 'Cajado Runa da Terra',
    'Lightcaller': 'Chamador da Luz',
}

CATEGORY_TRANSLATIONS = {
    'Warrior Weapons': 'Armas de Guerreiro',
    'Hunter Weapons': 'Armas de Cacador',
    'Mage Weapons': 'Armas de Mago',
    'Axe': 'Machado',
    'Sword': 'Espada',
    'Hammer': 'Martelo',
    'Mace': 'Maca',
    'Crossbow': 'Besta',
    'Bow': 'Arco',
    'Spear': 'Lanca',
    'Dagger': 'Adaga',
    'Quarterstaff': 'Cajado de Combate',
    'Fire Staff': 'Cajado de Fogo',
    'Frost Staff': 'Cajado de Gelo',
    'Arcane Staff': 'Cajado Arcano',
    'Cursed Staff': 'Cajado Amaldicoado',
    'Holy Staff': 'Cajado Sagrado',
    'Nature Staff': 'Cajado da Natureza',
    'Shapeshifter Staff': 'Cajado Metamorfo',
    'Torch': 'Tocha',
    'Blueflame Torch': 'Tocha Azul',
    'Shield': 'Escudo',
    'Tome of Spells': 'Tomo de Feiticos',
}

PORTUGUESE_TIER_PARTS = (
    ' do Iniciante',
    ' do Novico',
    ' do Noviço',
    ' do Aprendiz',
    ' do Adepto',
    ' do Perito',
    ' do Mestre',
    ' do Grao-mestre',
    ' do Grão-mestre',
    ' do Anciao',
    ' do Ancião',
    ' da Iniciante',
    ' da Novica',
    ' da Noviça',
    ' da Aprendiz',
    ' da Adepta',
    ' da Perita',
    ' da Mestra',
    ' da Grao-mestra',
    ' da Grão-mestra',
    ' da Ancia',
    ' da Anciã',
)


@lru_cache(maxsize=1)
def localized_items_by_unique_name() -> dict[str, dict]:
    try:
        response = httpx.get(ALBION_ITEMS_DUMP_URL, timeout=30)
        response.raise_for_status()
        return {item['UniqueName']: item for item in response.json() if item.get('UniqueName')}
    except Exception:
        return {}


def localized_name(item_id: str | None, locale: str, fallback: str | None = None) -> str | None:
    if not item_id:
        return fallback
    clean_item_id = item_id.split('@', 1)[0]
    item = localized_items_by_unique_name().get(clean_item_id)
    names = item.get('LocalizedNames') if item else None
    if not names:
        return fallback
    normalized_locale = locale.upper()
    return names.get(normalized_locale) or names.get('PT-BR') or names.get('EN-US') or fallback


def display_base_name(localized: str, fallback: str) -> str:
    value = localized or fallback
    for part in PORTUGUESE_TIER_PARTS:
        value = value.replace(part, '')
    return re.sub(r'\s+', ' ', value).strip()


def icon_url(item_id: str, locale: str = 'pt-BR') -> str:
    return f'https://render.albiononline.com/v1/item/{item_id}.png?quality=0&size=217&locale={locale}'


def base_weapon_name(name: str) -> str:
    for prefix in TIER_PREFIXES:
        if name.startswith(prefix):
            return name.removeprefix(prefix)
    return name


def tier_label(tier: str | int | float | None, item_id: str | None) -> str | None:
    if tier:
        return f'T{str(tier).split(".")[0]}'
    if item_id and item_id.startswith('T') and '_' in item_id:
        return item_id.split('_', 1)[0]
    return None


def translate_weapon_name(name: str, tier: str | int | float | None, item_id: str | None) -> str:
    base_name = base_weapon_name(name)
    translated = WEAPON_TRANSLATIONS.get(base_name, base_name)
    tier_prefix = tier_label(tier, item_id)
    return f'{tier_prefix} {translated}' if tier_prefix else translated


def translate_weapon_base_name(name: str) -> str:
    base_name = base_weapon_name(name)
    return WEAPON_TRANSLATIONS.get(base_name, base_name)


def source_url(item_type: str) -> str:
    return OPEN_ALBION_ARMORS_URL if item_type == 'armor' else OPEN_ALBION_WEAPONS_URL


def translate_category(value):
    if isinstance(value, dict):
        translated = {**value}
        if value.get('name'):
            translated['name'] = CATEGORY_TRANSLATIONS.get(value['name'], value['name'])
        return translated
    if isinstance(value, str):
        return CATEGORY_TRANSLATIONS.get(value, value)
    return value


def dump_item_matches(item_id: str, item_type: str) -> bool:
    if not re.match(r'^T[1-8]_', item_id):
        return False
    if item_type == 'cape':
        return '_CAPE' in item_id
    if item_type == 'food':
        return '_MEAL_' in item_id or item_id.startswith('T8_MEAL_') or re.match(r'^T[1-8]_MEAL_', item_id) is not None
    if item_type == 'potion':
        return '_POTION_' in item_id or re.match(r'^T[1-8]_POTION_', item_id) is not None
    return False


def dump_items(item_type: str, locale: str):
    items = []
    for item_id, item in localized_items_by_unique_name().items():
        if not dump_item_matches(item_id, item_type):
            continue
        english_name = localized_name(item_id, 'EN-US', item_id) or item_id
        name = localized_name(item_id, locale, english_name) or english_name
        items.append({
            'name': name,
            'name_pt': localized_name(item_id, 'pt-BR', name) or name,
            'name_en': english_name,
            'item_id': item_id,
            'icon_url': icon_url(item_id, locale),
            'tier': tier_label(None, item_id),
            'category': item_type,
            'subcategory': item_type,
        })
    return sorted(items, key=lambda entry: (entry['name'], entry['item_id']))


@router.get('/weapons')
async def albion_weapons(
    search: str | None = Query(None),
    limit: int = Query(80, ge=1, le=300),
    locale: str = Query('pt-BR'),
    grouped: bool = Query(False),
    item_type: str = Query('weapon', pattern='^(weapon|armor|cape|food|potion)$'),
):
    if item_type in {'cape', 'food', 'potion'}:
        items = dump_items(item_type, locale)
        if search:
            needle = search.strip().lower()
            items = [
                item for item in items
                if needle in item['name'].lower()
                or needle in item.get('name_en', '').lower()
                or needle in str(item.get('item_id') or '').lower()
            ]
        if grouped:
            groups = {}
            for item in items:
                base_en = base_weapon_name(item['name_en'])
                base_pt = display_base_name(item.get('name_pt') or item.get('name'), base_en)
                group = groups.setdefault(base_en, {
                    'name': base_pt if locale.lower().startswith('pt') else base_en,
                    'name_pt': base_pt,
                    'name_en': base_en,
                    'category': item_type,
                    'subcategory': item_type,
                    'variants': [],
                })
                tier = tier_label(item.get('tier'), item.get('item_id'))
                group['variants'].append({
                    'tier': tier.removeprefix('T') if tier else None,
                    'item_id': item.get('item_id'),
                    'icon_url': item.get('icon_url'),
                    'name': item.get('name'),
                    'name_en': item.get('name_en'),
                })
            return {'data': sorted(groups.values(), key=lambda entry: entry['name'])[:limit]}
        return {'data': items[:limit]}

    params = {'limit': 300}

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(source_url(item_type), params=params)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        return {
            'data': [
                {
                    'name': name_pt if locale.lower().startswith('pt') else name_en,
                    'name_pt': name_pt,
                    'name_en': name_en,
                    'item_id': item_id,
                    'icon_url': icon_url(item_id, locale),
                    'tier': None,
                    'category': 'fallback',
                }
                for name_pt, name_en, item_id in FALLBACK_WEAPONS
            ],
            'warning': 'Albion weapons provider unavailable',
        }

    payload = response.json()
    data = payload.get('data', payload if isinstance(payload, list) else [])
    weapons = []

    for item in data:
        english_name = item.get('name') or item.get('localized_name') or item.get('unique_name') or item.get('identifier')
        item_id = item.get('identifier') or item.get('unique_name') or item.get('item_id') or item.get('itemId')
        icon = item.get('icon')
        if not icon and item_id:
            icon = icon_url(item_id, locale)
        elif icon and locale.lower().startswith('pt'):
            icon = icon.replace('locale=en', f'locale={locale}')
        if english_name:
            official_name = localized_name(item_id, locale, english_name)
            translated_name = official_name or (
                translate_weapon_name(english_name, item.get('tier'), item_id) if item_type == 'weapon' else english_name
            )
            english_official_name = localized_name(item_id, 'EN-US', english_name) or english_name
            weapons.append({
                'name': translated_name,
                'name_pt': translated_name,
                'name_en': english_official_name,
                'item_id': item_id,
                'icon_url': icon,
                'tier': item.get('tier'),
                'category': translate_category(item.get('category') or item.get('subcategory')),
                'subcategory': translate_category(item.get('subcategory')),
            })

    for custom_item in CUSTOM_ITEMS:
        if item_type != 'weapon':
            continue
        for item_id in custom_item['item_ids']:
            tier = tier_label(None, item_id)
            tier_number = tier.removeprefix('T') if tier else None
            name_pt = custom_item['base_pt']
            name_en = custom_item['base_en']
            if any(weapon.get('item_id') == item_id for weapon in weapons):
                continue
            weapons.append({
                'name': name_pt if locale.lower().startswith('pt') else name_en,
                'name_pt': name_pt,
                'name_en': name_en,
                'item_id': item_id,
                'icon_url': icon_url(item_id, locale),
                'tier': tier_number,
                'category': translate_category(custom_item['category']),
                'subcategory': translate_category(custom_item['subcategory']),
            })

    if search:
        needle = search.strip().lower()
        weapons = [
            weapon for weapon in weapons
            if needle in weapon['name'].lower()
            or needle in weapon.get('name_en', '').lower()
            or needle in str(weapon.get('item_id') or '').lower()
        ]

    if grouped:
        groups = {}
        for weapon in weapons:
            base_en = base_weapon_name(weapon['name_en'])
            base_pt = display_base_name(weapon.get('name_pt') or weapon.get('name'), base_en)
            group = groups.setdefault(base_en, {
                'name': base_pt if locale.lower().startswith('pt') else base_en,
                'name_pt': base_pt,
                'name_en': base_en,
                'category': weapon.get('category'),
                'subcategory': weapon.get('subcategory'),
                'variants': [],
            })
            tier = tier_label(weapon.get('tier'), weapon.get('item_id'))
            group['variants'].append({
                'tier': tier.removeprefix('T') if tier else None,
                'item_id': weapon.get('item_id'),
                'icon_url': weapon.get('icon_url'),
                'name': weapon.get('name'),
                'name_en': weapon.get('name_en'),
            })

        grouped_weapons = sorted(groups.values(), key=lambda item: item['name'])
        return {'data': grouped_weapons[:limit]}

    return {'data': weapons[:limit]}
