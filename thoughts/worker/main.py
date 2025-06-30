import time
import json
import logging
from jinja2 import Environment, FileSystemLoader
from pymemcache.client.base import Client as MemcacheClient

from ..core.config import settings
from ..api.models import ThoughtDB
from ..api.database import SessionLocal
from ..core.llm import get_structured_thoughts

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_thoughts():
    """
    Fetches thoughts, gets structured data from LLM, and generates HTML.
    """
    db = SessionLocal()
    try:
        logger.info("Reading all thoughts from database.")
        thoughts = db.query(ThoughtDB).all()
        logger.info(f"Found {len(thoughts)} thoughts to process.")
        if not thoughts:
            return

        # Format thoughts for the LLM
        thoughts_data = "\n".join([f"- {t.content}" for t in thoughts])
        
        logger.info("Calling LLM to get structured thoughts.")
        structured_json_str = get_structured_thoughts(thoughts_data)
        
        try:
            structured_data = json.loads(structured_json_str)
            logger.info("Successfully decoded JSON from LLM.")
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from LLM response. Continuing with raw response.", exc_info=True)
            # For the template, we can't pass a string, so we'll pass a dict with the raw text
            structured_data = {"raw_response": structured_json_str, "title": "Failed to Decode LLM Response"}


        # Render HTML from template
        logger.info("Rendering HTML template.")
        env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))
        template = env.get_template('thoughts_template.html')
        
        output_html = template.render(data=structured_data)

        # Save to static file
        output_path = settings.STATIC_DIR / "index.html"
        logger.info(f"Writing structured thoughts to {output_path}")
        with open(output_path, "w") as f:
            f.write(output_html)
        
        logger.info("Successfully generated static HTML page.")

    except Exception:
        logger.error("An error occurred during thought processing.", exc_info=True)
    finally:
        db.close()
        logger.info("Database session closed.")

def main():
    memcache_client = MemcacheClient((settings.MEMCACHED_HOST, settings.MEMCACHED_PORT))
    logger.info("Worker started. Waiting for jobs...")
    while True:
        try:
            # Note: This is a quiet check. We only log when a job is found.
            job_id = memcache_client.get("new_job_trigger")
            if job_id:
                logger.info(f"New job triggered with ID: {job_id.decode()}. Processing thoughts...")
                process_thoughts()
                logger.info("Processing finished. Deleting job trigger from Memcached.")
                memcache_client.delete("new_job_trigger")
                logger.info("Job trigger deleted.")
        
        except Exception:
            logger.error("An error occurred in the main worker loop.", exc_info=True)
        
        time.sleep(5)

if __name__ == "__main__":
    main() 