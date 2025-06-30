import google.generativeai as genai
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GOOGLE_API_KEY)

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
        
        # Basic cleanup to get only the JSON part
        cleaned_response = response.text.strip().replace('`json', '').replace('`', '')

        return cleaned_response
    except Exception:
        logger.error("Error calling Gemini API.", exc_info=True)
        return "{}" 