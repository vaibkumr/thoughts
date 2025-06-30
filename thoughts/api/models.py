from pydantic import BaseModel
import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

class ThoughtBase(BaseModel):
    content: str

class ThoughtCreate(ThoughtBase):
    password: str

class Thought(ThoughtBase):
    id: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

Base = declarative_base()

class ThoughtDB(Base):
    __tablename__ = "thoughts_table_v1"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow) 