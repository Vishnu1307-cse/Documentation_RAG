import logging
import anthropic
from app.config import settings
from app.llm.provider_factory import BaseLLMProvider

logger = logging.getLogger(__name__)

class AnthropicProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.anthropic_api_key
        if not self.api_key:
            raise ValueError(
                "Anthropic API key is missing. Define ANTHROPIC_API_KEY in environment or anthropic_api_key.txt."
            )
            
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = settings.ANTHROPIC_MODEL
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise e

    def generate(self, prompt: str, system_instruction: str = None) -> str:
        """Invokes Claude messages endpoint via Anthropic python package."""
        logger.info(f"Generating completion using Anthropic model {self.model}...")
        
        try:
            # Construct message request payload
            # System instructions are passed explicitly to messages.create system param
            kwargs = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            if system_instruction:
                kwargs["system"] = system_instruction
                
            response = self.client.messages.create(**kwargs)
            # Extrapolate text blocks
            content = "".join([block.text for block in response.content if block.type == "text"])
            return content.strip()
            
        except Exception as e:
            logger.error(f"Anthropic completion request failed: {e}")
            raise e
