from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import TokenResponse
from app.auth import verify_password, create_access_token
from app.crud.user import get_user_by_username, create_user

router = APIRouter()

@router.post("/register", status_code=201)
def register(username: str, password: str, db: Session = Depends(get_db)):
    if get_user_by_username(db, username):
        raise HTTPException(status_code=400, detail="Username already taken")
    create_user(db, username, password)
    return {"message": f"User '{username}' created"}

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)