import uuid
import logging
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pymemcache.client.base import Client as MemcacheClient
import os

from ..core.config import settings
from . import models, database

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
async def get_home(request: Request):
    logger.info(f"Serving client/index.html to {request.client.host}")
    client_html_path = os.path.join(os.path.dirname(__file__), "..", "..", "client", "index.html")
    return FileResponse(client_html_path)

@app.post("/submit", response_model=models.Thought)
def submit_thought(thought: models.ThoughtCreate, db: Session = Depends(get_db), memcache_client: MemcacheClient = Depends(get_memcached_client)):
    logger.info(f"Received new thought submission: '{thought.content[:50]}...'")
    try:
        db_thought = database.Thought(content=thought.content)
        logger.info("Writing thought to database.")
        db.add(db_thought)
        db.commit()
        db.refresh(db_thought)
        logger.info(f"Successfully wrote thought with id {db_thought.id} to database.")

        job_id = str(uuid.uuid4())
        
        logger.info(f"Writing job trigger to memcached with job_id: {job_id}")
        memcache_client.set("new_job_trigger", job_id, expire=3600)
        logger.info("Successfully wrote job trigger to memcached.")

        return db_thought
    except Exception:
        logger.error("Error processing thought submission.", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error") 