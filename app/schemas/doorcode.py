from pydantic import BaseModel
from datetime import datetime

class DoorCodeOut(BaseModel):
    code: str
    expires_at: datetime
    used: bool

    class Config:
        from_attributes = True