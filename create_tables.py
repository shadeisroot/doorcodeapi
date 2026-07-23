from app.database import Base, engine
from app.models.doorcode import DoorCode
from app.models.user import User

Base.metadata.create_all(bind=engine)
print("Tables created!")