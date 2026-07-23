from pydantic import BaseModel, ConfigDict
from datetime import datetime

class DoorCodeOut(BaseModel):
    code: str
    expires_at: datetime
    used: bool

    model_config = ConfigDict(from_attributes=True)