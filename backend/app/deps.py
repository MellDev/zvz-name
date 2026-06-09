from contextlib import contextmanager

from sqlalchemy.orm import Session

from .db.session import SessionLocal

@contextmanager
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
