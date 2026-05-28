import logging
from openai import OpenAI
from app.config import settings
from app.llm.provider_factory import BaseLLMProvider

logger = logging.getLogger(__name__)

class DeepSeekProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key is missing. Define DEEPSEEK_API_KEY in environment or deepseek_api_key.txt."
            )
            
        try:
            # DeepSeek provides an OpenAI-compatible API base endpoint
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            self.model = settings.DEEPSEEK_MODEL
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client for DeepSeek: {e}")
            raise e

    def generate(self, prompt: str, system_instruction: str = None) -> str:
        """Invokes DeepSeek completions via standard OpenAI compatible API base."""
        logger.info(f"Generating completion using DeepSeek model {self.model}...")
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            if not content:
                return "Error: Received empty response from DeepSeek."
            return content.strip()
            
        except Exception as e:
            logger.error(f"DeepSeek completion request failed: {e}")
            raise e
