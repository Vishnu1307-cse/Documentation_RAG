import logging
import google.generativeai as genai
from app.config import settings
from app.llm.provider_factory import BaseLLMProvider

logger = logging.getLogger(__name__)

class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if not self.api_key:
            raise ValueError(
                "Gemini API key is missing. Define GEMINI_API_KEY in environment or gemini_api_key.txt."
            )
            
        try:
            genai.configure(api_key=self.api_key)
            self.model_name = settings.GEMINI_MODEL
        except Exception as e:
            logger.error(f"Failed to configure Gemini package: {e}")
            raise e

    def generate(self, prompt: str, system_instruction: str = None) -> str:
        """Invokes content generation endpoint via Google GenerativeAI package."""
        logger.info(f"Generating completion using Gemini model {self.model_name}...")
        
        try:
            # Construct model structure with optional system instructions
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"temperature": 0.2},
                system_instruction=system_instruction
            )
            
            response = model.generate_content(prompt)
            if not response.text:
                return "Error: Received empty text from Gemini."
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API generation failed: {e}")
            raise e
