from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.doorcode import DoorCodeOut
from app.crud.doorcode import generate_code, verify_code

router = APIRouter()

@router.post("/", response_model=DoorCodeOut, status_code=201)
def create_code(valid_minutes: int = 60, db: Session = Depends(get_db)):
    return generate_code(db, valid_minutes)

@router.post("/verify/{code}")
def check_code(code: str, db: Session = Depends(get_db)):
    is_valid = verify_code(db, code)
    if not is_valid:
        raise HTTPException(status_code=403, detail="Invalid or expired code")
    return {"access": "granted"}