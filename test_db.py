# test_db.py
from app.database import engine

with engine.connect() as conn:
    print("Connected!")