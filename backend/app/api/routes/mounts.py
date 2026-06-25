from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Mount

router = APIRouter()

MOUNT_CATALOG = [
    {'mount_name': 'Mule', 'display_name': 'Mula', 'item_id': 'T2_MOUNT_MULE', 'tier': '2', 'move_speed_bonus': 30, 'gallop_speed_bonus': None, 'max_load': None},
    {'mount_name': 'Riding Horse', 'display_name': 'Cavalo de Montaria', 'item_id': 'T3_MOUNT_HORSE', 'tier': '3', 'move_speed_bonus': 65, 'gallop_speed_bonus': 95, 'max_load': 157},
    {'mount_name': 'Riding Horse T4', 'display_name': 'Cavalo de Montaria T4', 'item_id': 'T4_MOUNT_HORSE', 'tier': '4', 'move_speed_bonus': 65, 'gallop_speed_bonus': 100, 'max_load': 225},
    {'mount_name': 'Riding Horse T5', 'display_name': 'Cavalo de Montaria T5', 'item_id': 'T5_MOUNT_HORSE', 'tier': '5', 'move_speed_bonus': 70, 'gallop_speed_bonus': 110, 'max_load': 318},
    {'mount_name': 'Riding Horse T6', 'display_name': 'Cavalo de Montaria T6', 'item_id': 'T6_MOUNT_HORSE', 'tier': '6', 'move_speed_bonus': 75, 'gallop_speed_bonus': 120, 'max_load': 449},
    {'mount_name': 'Riding Horse T7', 'display_name': 'Cavalo de Montaria T7', 'item_id': 'T7_MOUNT_HORSE', 'tier': '7', 'move_speed_bonus': 75, 'gallop_speed_bonus': 125, 'max_load': 636},
    {'mount_name': 'Riding Horse T8', 'display_name': 'Cavalo de Montaria T8', 'item_id': 'T8_MOUNT_HORSE', 'tier': '8', 'move_speed_bonus': 80, 'gallop_speed_bonus': 135, 'max_load': 900},
    {'mount_name': 'Transport Ox', 'display_name': 'Boi de Transporte', 'item_id': 'T3_MOUNT_OX', 'tier': '3', 'move_speed_bonus': 35, 'gallop_speed_bonus': 60, 'max_load': 1569},
    {'mount_name': 'Transport Ox T4', 'display_name': 'Boi de Transporte T4', 'item_id': 'T4_MOUNT_OX', 'tier': '4', 'move_speed_bonus': 40, 'gallop_speed_bonus': 70, 'max_load': 2237},
    {'mount_name': 'Transport Ox T5', 'display_name': 'Boi de Transporte T5', 'item_id': 'T5_MOUNT_OX', 'tier': '5', 'move_speed_bonus': 45, 'gallop_speed_bonus': 80, 'max_load': 3180},
    {'mount_name': 'Transport Ox T6', 'display_name': 'Boi de Transporte T6', 'item_id': 'T6_MOUNT_OX', 'tier': '6', 'move_speed_bonus': 50, 'gallop_speed_bonus': 90, 'max_load': 4498},
    {'mount_name': 'Transport Ox T7', 'display_name': 'Boi de Transporte T7', 'item_id': 'T7_MOUNT_OX', 'tier': '7', 'move_speed_bonus': 55, 'gallop_speed_bonus': 100, 'max_load': 6369},
    {'mount_name': 'Transport Ox T8', 'display_name': 'Boi de Transporte T8', 'item_id': 'T8_MOUNT_OX', 'tier': '8', 'move_speed_bonus': 60, 'gallop_speed_bonus': 110, 'max_load': 9000},
    {'mount_name': 'Armored Horse', 'display_name': 'Cavalo Blindado', 'item_id': 'T5_MOUNT_ARMORED_HORSE', 'tier': '5', 'move_speed_bonus': 65, 'gallop_speed_bonus': 115, 'max_load': None},
    {'mount_name': 'Armored Horse T6', 'display_name': 'Cavalo Blindado T6', 'item_id': 'T6_MOUNT_ARMORED_HORSE', 'tier': '6', 'move_speed_bonus': 70, 'gallop_speed_bonus': 120, 'max_load': None},
    {'mount_name': 'Armored Horse T7', 'display_name': 'Cavalo Blindado T7', 'item_id': 'T7_MOUNT_ARMORED_HORSE', 'tier': '7', 'move_speed_bonus': 75, 'gallop_speed_bonus': 125, 'max_load': None},
    {'mount_name': 'Armored Horse T8', 'display_name': 'Cavalo Blindado T8', 'item_id': 'T8_MOUNT_ARMORED_HORSE', 'tier': '8', 'move_speed_bonus': 80, 'gallop_speed_bonus': 135, 'max_load': None},
    {'mount_name': 'Swiftclaw', 'display_name': 'Garra Ligeira', 'item_id': 'T5_MOUNT_COUGAR_KEEPER', 'tier': '5', 'move_speed_bonus': 75, 'gallop_speed_bonus': 120, 'max_load': None},
    {'mount_name': 'Direwolf', 'display_name': 'Lobo Terrivel', 'item_id': 'T6_MOUNT_DIREWOLF', 'tier': '6', 'move_speed_bonus': 85, 'gallop_speed_bonus': 125, 'max_load': None},
    {'mount_name': 'Stag', 'display_name': 'Cervo', 'item_id': 'T4_MOUNT_GIANTSTAG', 'tier': '4', 'move_speed_bonus': 70, 'gallop_speed_bonus': 110, 'max_load': 695},
    {'mount_name': 'Moose', 'display_name': 'Alce', 'item_id': 'T6_MOUNT_GIANTSTAG_MOOSE', 'tier': '6', 'move_speed_bonus': 75, 'gallop_speed_bonus': 120, 'max_load': 1040},
    {'mount_name': 'Saddled Boar', 'display_name': 'Javali Selado', 'item_id': 'T5_MOUNT_DIREBOAR', 'tier': '5', 'move_speed_bonus': 60, 'gallop_speed_bonus': 100, 'max_load': 766},
    {'mount_name': 'Direboar', 'display_name': 'Javali Terrivel', 'item_id': 'T7_MOUNT_DIREBOAR', 'tier': '7', 'move_speed_bonus': 65, 'gallop_speed_bonus': 115, 'max_load': 1322},
    {'mount_name': 'Grizzly Bear', 'display_name': 'Urso Cinzento', 'item_id': 'T7_MOUNT_ARMORED_HORSE_MORGANA', 'tier': '7', 'move_speed_bonus': 60, 'gallop_speed_bonus': 100, 'max_load': 2397},
    {'mount_name': 'Winter Bear', 'display_name': 'Urso Invernal', 'item_id': 'T8_MOUNT_ARMORED_HORSE_FROST', 'tier': '8', 'move_speed_bonus': 60, 'gallop_speed_bonus': 100, 'max_load': 2477},
    {'mount_name': 'Frost Ram', 'display_name': 'Carneiro Gelido', 'item_id': 'T6_MOUNT_RAM_FW_FAME', 'tier': '6', 'move_speed_bonus': 70, 'gallop_speed_bonus': 120, 'max_load': None},
    {'mount_name': 'Pest Lizard', 'display_name': 'Lagarto Pestilento', 'item_id': 'T7_MOUNT_SWAMPDRAGON_BATTLE', 'tier': '7', 'move_speed_bonus': 103, 'gallop_speed_bonus': 103, 'max_load': None},
    {'mount_name': 'Saddled Swamp Salamander', 'display_name': 'Salamandra do Pantano Selada', 'item_id': 'T5_MOUNT_SWAMPDRAGON', 'tier': '5', 'move_speed_bonus': 100, 'gallop_speed_bonus': 100, 'max_load': None},
    {'mount_name': 'Saddled Swamp Dragon', 'display_name': 'Dragao do Pantano Selado', 'item_id': 'T7_MOUNT_SWAMPDRAGON', 'tier': '7', 'move_speed_bonus': 103, 'gallop_speed_bonus': 103, 'max_load': None},
    {'mount_name': 'Spectral Bat', 'display_name': 'Morcego Espectral', 'item_id': 'T7_MOUNT_BAT', 'tier': '7', 'move_speed_bonus': 85, 'gallop_speed_bonus': 132, 'max_load': None},
    {'mount_name': 'Fiery Warhorse', 'display_name': 'Cavalo de Guerra Flamejante', 'item_id': 'T8_MOUNT_HORSE_UNDEAD', 'tier': '8', 'move_speed_bonus': 80, 'gallop_speed_bonus': 135, 'max_load': None},
    {'mount_name': 'Morgana Nightmare', 'display_name': 'Pesadelo de Morgana', 'item_id': 'T8_MOUNT_MORGANA_NIGHTMARE', 'tier': '8.1', 'move_speed_bonus': 80, 'gallop_speed_bonus': 137, 'max_load': None},
    {'mount_name': 'Spectral Bonehorse', 'display_name': 'Cavalo de Osso Espectral', 'item_id': 'T8_MOUNT_HORSE_UNDEAD', 'tier': '8.1', 'move_speed_bonus': 80, 'gallop_speed_bonus': 137, 'max_load': None},
    {'mount_name': 'Saddled Mystic Owl', 'display_name': 'Coruja Mistica Selada', 'item_id': 'T5_MOUNT_OWL', 'tier': '5', 'move_speed_bonus': 95, 'gallop_speed_bonus': 134, 'max_load': None},
    {'mount_name': 'Elite Mystic Owl', 'display_name': 'Coruja Mistica Elite', 'item_id': 'T8_MOUNT_OWL_ELITE', 'tier': '8', 'move_speed_bonus': 95, 'gallop_speed_bonus': 139, 'max_load': None},
    {'mount_name': 'Elite Greywolf', 'display_name': 'Lobo Cinzento Elite', 'item_id': 'T8_MOUNT_DIREWOLF_ELITE', 'tier': '8', 'move_speed_bonus': 85, 'gallop_speed_bonus': 135, 'max_load': None},
    {'mount_name': 'Avalonian Basilisk', 'display_name': 'Basilisco Avaleriano', 'item_id': 'T7_MOUNT_BASILISK_AVALON', 'tier': '7', 'move_speed_bonus': 115, 'gallop_speed_bonus': 115, 'max_load': None},
    {'mount_name': 'Soulspinner', 'display_name': 'Tecela-Almas', 'item_id': 'T8_MOUNT_ARACHNID_SOUL', 'tier': '8', 'move_speed_bonus': 117, 'gallop_speed_bonus': 117, 'max_load': None},
    {'mount_name': 'Hellspinner', 'display_name': 'Tecela-Infernal', 'item_id': 'T5_MOUNT_ARACHNID_HELL', 'tier': '5', 'move_speed_bonus': 110, 'gallop_speed_bonus': 110, 'max_load': None},
]


def mount_icon(item_id: str) -> str:
    return f'https://render.albiononline.com/v1/item/{item_id}@0.png?quality=0&size=217&locale=pt-BR'


def serialize_catalog_mount(mount: dict) -> dict:
    return {
        **mount,
        'icon_url': mount_icon(mount['item_id']),
        'active': True,
        'summary': f"{mount['display_name']} T{mount['tier']} - {mount['move_speed_bonus']}% velocidade"
        + (f", {mount['gallop_speed_bonus']}% galope" if mount.get('gallop_speed_bonus') else ''),
    }

@router.post('/', response_model=List[dict], status_code=status.HTTP_201_CREATED)
def create_mount(payload: dict, db: Session = Depends(get_db)):
    if db.query(Mount).filter(Mount.mount_name == payload['mount_name']).first():
        raise HTTPException(status_code=400, detail='Mount already exists')
    mount = Mount(**payload)
    db.add(mount)
    db.commit()
    db.refresh(mount)
    return [{
        'id': mount.id,
        'mount_name': mount.mount_name,
        'active': mount.active,
    }]

@router.get('/', response_model=List[dict])
def list_mounts(db: Session = Depends(get_db)):
    catalog_by_name = {mount['mount_name']: serialize_catalog_mount(mount) for mount in MOUNT_CATALOG}
    for mount in db.query(Mount).all():
        if mount.mount_name not in catalog_by_name:
            catalog_by_name[mount.mount_name] = {
                'id': mount.id,
                'mount_name': mount.mount_name,
                'display_name': mount.mount_name,
                'item_id': None,
                'icon_url': None,
                'tier': None,
                'move_speed_bonus': None,
                'gallop_speed_bonus': None,
                'max_load': None,
                'summary': mount.mount_name,
                'active': mount.active,
            }
    return sorted(catalog_by_name.values(), key=lambda mount: mount['display_name'])
