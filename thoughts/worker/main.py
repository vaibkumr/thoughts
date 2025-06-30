import time
import json
import logging
from jinja2 import Environment, FileSystemLoader
from pymemcache.client.base import Client as MemcacheClient

from ..core.config import settings
from ..api.database import SessionLocal, Thought
from ..core.llm import get_structured_thoughts

logging.basicConfig(level=logging.INFO)

def process_thoughts():
    """
    Fetches thoughts, gets structured data from LLM, and generates HTML.
    """
    db = SessionLocal()
    try:
        thoughts = db.query(Thought).all()
        if not thoughts:
            logging.info("No thoughts to process.")
            return

        # Format thoughts for the LLM
        thoughts_data = "\n".join([f"- {t.content}" for t in thoughts])
        
        # Get structured JSON from the LLM
        structured_json_str = get_structured_thoughts(thoughts_data)
        
        try:
            structured_data = json.loads(structured_json_str)
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON from LLM response.")
            return

        # Render HTML from template
        env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))
        template = env.get_template('thoughts_template.html')
        
        output_html = template.render(data=structured_data)

        # Save to static file
        with open(settings.STATIC_DIR / "index.html", "w") as f:
            f.write(output_html)
        
        logging.info("Successfully generated static HTML page.")

    finally:
        db.close()

def main():
    memcache_client = MemcacheClient((settings.MEMCACHED_HOST, settings.MEMCACHED_PORT))
    logging.info("Worker started. Waiting for jobs...")
    while True:
        if memcache_client.get("new_job_trigger"):
            logging.info("New job triggered. Processing thoughts...")
            process_thoughts()
            memcache_client.delete("new_job_trigger")
        
        time.sleep(5)

if __name__ == "__main__":
    main() 