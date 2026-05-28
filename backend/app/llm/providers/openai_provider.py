import logging
from openai import OpenAI
from app.config import settings
from app.llm.provider_factory import BaseLLMProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        # 1. Multi-tiered api key resolution
        self.api_key = settings.openai_api_key
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is missing. Define OPENAI_API_KEY in environment or openai_api_key.txt."
            )
            
        try:
            self.client = OpenAI(api_key=self.api_key)
            self.model = settings.OPENAI_MODEL
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise e

    def generate(self, prompt: str, system_instruction: str = None) -> str:
        """Invokes chat completion endpoint via OpenAI python package."""
        logger.info(f"Generating completion using OpenAI model {self.model}...")
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2, # Low temperature for factual RAG explanations
            )
            
            content = response.choices[0].message.content
            if not content:
                return "Error: Received empty response from OpenAI."
            return content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI completion request failed: {e}")
            raise e
