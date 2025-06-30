import google.generativeai as genai
from ..core.config import settings
import logging
import re

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GOOGLE_API_KEY)

def _extract_json(text: str) -> str:
    """
    Extracts a JSON object from a string that might be wrapped in markdown code fences.
    """
    # This regex looks for a JSON object enclosed in ```json or ```
    # It's non-greedy to find the first complete object.
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        logger.info("Found JSON block with markdown fence.")
        return match.group(1)

    # If no markdown block is found, fall back to finding the first and last curly braces.
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        logger.warning("Could not find markdown-fenced JSON, falling back to first/last curly brace.")
        return text[start:end+1]

    logger.error("No JSON object could be extracted from the LLM response. Returning raw text.")
    return text

def get_structured_thoughts(thoughts_data: str) -> str:
    """
    Calls the Gemini API to structure the thoughts.
    """
    # Use a more robust check for the API key
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY_HERE":
        logger.warning("Google API Key is not set or is a placeholder. Using mock data.")
        return '{"title": "My Thoughts", "thoughts": [{"id": 1, "content": "This is a mock thought.", "category": "mock"}]}'

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        with open(settings.PROMPT_FILE, 'r') as f:
            prompt_template = f.read()

        prompt = f"{prompt_template}\n\nHere is the data:\n{thoughts_data}"
        
        logger.info("Generating content with Gemini API.")
        response = model.generate_content(prompt)
        
        logger.info(f"Raw LLM response received: {response.text}")
        
        # Use the new robust JSON extractor
        cleaned_response = _extract_json(response.text)

        return cleaned_response
    except Exception:
        logger.error("Error calling Gemini API.", exc_info=True)
        return "{}" 