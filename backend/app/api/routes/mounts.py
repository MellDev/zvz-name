from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Mount

router = APIRouter()

@router.post('/', response_model=List[dict], status_code=status.HTTP_201_CREATED)
def create_mount(payload: dict, db: Session = Depends(get_db)):
    if db.query(Mount).filter(Mount.mount_name == payload['mount_name']).first():
        raise HTTPException(status_code=400, detail='Mount already exists')
    mount = Mount(**payload)
    db.add(mount)
    db.commit()
    db.refresh(mount)
    return [mount]

@router.get('/', response_model=List[dict])
def list_mounts(db: Session = Depends(get_db)):
    return [
        {'id': mount.id, 'mount_name': mount.mount_name, 'active': mount.active}
        for mount in db.query(Mount).all()
    ]
