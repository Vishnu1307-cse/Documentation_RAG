import logging
from abc import ABC, abstractmethod
from app.config import settings

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    """Abstract interface defining required behaviors for cloud LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, system_instruction: str = None) -> str:
        """
        Executes a completion generation request.
        Both prompts and instruction arguments are parsed.
        """
        pass

class LLMProviderFactory:
    @staticmethod
    def get_provider(provider_name: str = None) -> BaseLLMProvider:
        """
        Returns an active, initialized LLM provider instance matching the selected name.
        Defaults to configured `settings.LLM_PROVIDER` if none specified.
        """
        name = (provider_name or settings.LLM_PROVIDER).lower().strip()
        
        logger.info(f"Resolving LLM Provider instance for: {name}")
        
        if name == "openai":
            from app.llm.providers.openai_provider import OpenAIProvider
            return OpenAIProvider()
            
        elif name == "anthropic" or name == "claude":
            from app.llm.providers.anthropic_provider import AnthropicProvider
            return AnthropicProvider()
            
        elif name == "gemini" or name == "google":
            from app.llm.providers.gemini_provider import GeminiProvider
            return GeminiProvider()
            
        elif name == "deepseek":
            from app.llm.providers.deepseek_provider import DeepSeekProvider
            return DeepSeekProvider()
            
        else:
            logger.error(f"Unrecognized provider name: {name}. Defaulting to OpenAI.")
            from app.llm.providers.openai_provider import OpenAIProvider
            return OpenAIProvider()
