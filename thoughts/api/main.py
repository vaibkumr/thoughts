import uuid
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pymemcache.client.base import Client as MemcacheClient
import os

from ..core.config import settings
from . import models, database

database.create_db_and_tables()

app = FastAPI()

# Mount the static directory to serve the generated thoughts page
app.mount("/thoughts", StaticFiles(directory=settings.STATIC_DIR), name="thoughts")

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get Memcached client
def get_memcached_client():
    return MemcacheClient((settings.MEMCACHED_HOST, settings.MEMCACHED_PORT))

@app.get("/")
async def get_home():
    client_html_path = os.path.join(os.path.dirname(__file__), "..", "..", "client", "index.html")
    return FileResponse(client_html_path)

@app.post("/submit", response_model=models.Thought)
def submit_thought(thought: models.ThoughtCreate, db: Session = Depends(get_db), memcache_client: MemcacheClient = Depends(get_memcached_client)):
    db_thought = database.Thought(content=thought.content)
    db.add(db_thought)
    db.commit()
    db.refresh(db_thought)

    job_id = str(uuid.uuid4())
    job_data = {
        "job_id": job_id,
        "timestamp": db_thought.timestamp.isoformat()
    }
    
    # Use a specific key for the queue, e.g., 'job_queue'
    # Memcached doesn't have a built-in queue, so we'll use a list under a key.
    # This is a simplification. For a real scenario, a more robust queue like RabbitMQ or Redis would be better.
    
    # For simplicity, we'll just set a key indicating a new job.
    # The worker will look for this key.
    memcache_client.set("new_job_trigger", job_id, expire=3600)

    return db_thought 