from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
import datetime

from thoughts.core.config import settings
from thoughts.api.models import Base, ThoughtDB

db_url = settings.DATABASE_URL
if settings.TEST_MODE:
    db_url = settings.TEST_DATABASE_URL

engine = create_engine(db_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    Base.metadata.create_all(bind=engine) 