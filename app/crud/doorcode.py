import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.doorcode import DoorCode

def generate_code(db: Session, valid_minutes: int = 60):
    # 1. Generate a random code
    code = secrets.token_hex(3)  # e.g. "a3f9c1" — 6 hex chars

    # 2. Set timestamps
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=valid_minutes)

    # 3. Build and save the DB row
    db_code = DoorCode(
        code=code,
        created_at=now,
        expires_at=expires,
        used=False
    )
    db.add(db_code)
    db.commit()
    db.refresh(db_code)
    return db_code


def verify_code(db: Session, code: str) -> bool:
    db_code = db.query(DoorCode).filter(DoorCode.code == code).first()

    if not db_code:
        return False
    elif db_code.used:
        return False
    elif db_code.expires_at < datetime.now(timezone.utc):
        return False
    else:
        db_code.used = True    # ← consume it
        db.commit()             # ← save that change
        return True