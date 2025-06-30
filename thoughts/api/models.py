from pydantic import BaseModel
import datetime

class ThoughtBase(BaseModel):
    content: str

class ThoughtCreate(ThoughtBase):
    pass

class Thought(ThoughtBase):
    id: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True 