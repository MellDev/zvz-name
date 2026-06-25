from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Weapon

router = APIRouter()

@router.post('/', response_model=List[dict], status_code=status.HTTP_201_CREATED)
def create_weapon(payload: dict, db: Session = Depends(get_db)):
    if db.query(Weapon).filter(Weapon.weapon_name == payload['weapon_name']).first():
        raise HTTPException(status_code=400, detail='Weapon already exists')
    weapon = Weapon(**payload)
    db.add(weapon)
    db.commit()
    db.refresh(weapon)
    return [{
        'id': weapon.id,
        'weapon_name': weapon.weapon_name,
        'weapon_category': weapon.weapon_category,
        'active': weapon.active,
    }]

@router.get('/', response_model=List[dict])
def list_weapons(db: Session = Depends(get_db)):
    return [
        {'id': weapon.id, 'weapon_name': weapon.weapon_name, 'weapon_category': weapon.weapon_category, 'active': weapon.active}
        for weapon in db.query(Weapon).all()
    ]
