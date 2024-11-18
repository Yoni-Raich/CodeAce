from langchain_core.language_models import BaseLLM
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from typing import Optional, Dict, Any

class LLMManager:
    """Manager class for handling different LLM providers through LangChain."""
    
    def __init__(self):
        self.supported_llms = {
            "openai": self._get_openai_llm,
            "anthropic": self._get_anthropic_llm,
        }
    
    def get_llm(self, provider: str, **kwargs) -> BaseLLM:
        """
        Get an LLM instance based on the specified provider.
        
        Args:
            provider (str): The LLM provider to use ("openai", "anthropic", etc.)
            **kwargs: Additional arguments to pass to the LLM constructor
            
        Returns:
            BaseLLM: A LangChain LLM instance
            
        Raises:
            ValueError: If the provider is not supported
        """
        if provider.lower() not in self.supported_llms:
            raise ValueError(f"Unsupported LLM provider: {provider}. "
                           f"Supported providers: {list(self.supported_llms.keys())}")
            
        return self.supported_llms[provider.lower()](**kwargs)
    
    def _get_openai_llm(self, **kwargs) -> ChatOpenAI:
        """Initialize an OpenAI LLM instance."""
        default_params = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.7
        }
        params = {**default_params, **kwargs}
        return ChatOpenAI(**params)
    
    def _get_anthropic_llm(self, **kwargs) -> ChatAnthropic:
        """Initialize an Anthropic LLM instance."""
        default_params = {
            "model": "claude-3-sonnet-20240229",
            "temperature": 0.7
        }
        params = {**default_params, **kwargs}
        return ChatAnthropic(**params)
