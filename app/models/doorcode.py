from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database import Base

class DoorCode(Base):
    __tablename__ = "doorcodes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)    # ← timezone=True
    expires_at = Column(DateTime(timezone=True), nullable=False)     # ← timezone=True
    used = Column(Boolean, default=False, nullable=False)