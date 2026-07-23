from sqlalchemy.orm import Session
from app.models.user import User
from app.auth import hash_password

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str):
    db_user = User(username=username, hashed_password=hash_password(password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user