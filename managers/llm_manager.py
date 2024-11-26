from langchain_core.language_models import BaseLLM
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama.chat_models import ChatOllama
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import os
load_dotenv()
class LLMManager:
    """Manager class for handling different LLM providers through LangChain."""
    
    def __init__(self):
        self.supported_llms = {
            "openai": self._get_openai_llm,
            "anthropic": self._get_anthropic_llm,
            "azure": self._get_azure_openai_llm,
            "ollama": self._get_ollama_llm,
            "gemini": self._get_gemini_llm,
        }

    def create_model_instance_by_name(self, model_name: str):
        if model_name not in self.supported_llms:
            raise ValueError(f"Model {model_name} is not supported.")
        return self.supported_llms[model_name]()    
    
    def _initialize_api_key(self, provider: str, api_key: Optional[str] = None) -> str:
        """Initialize API key for a provider."""
        env_vars = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "azure": "AZ_OPENAI_API_KEY",
            "gemini": "GOOGLE_API_KEY"
        }
        
        if api_key:
            return api_key
        
        env_key = os.getenv(env_vars[provider])
        if not env_key:
            raise ValueError(
                f"API key for {provider} is required. Either pass api_key or set {env_vars[provider]}"
            )
        
        return env_key

    def _get_openai_llm(self, **kwargs) -> ChatOpenAI:
        """Initialize an OpenAI LLM instance."""
        api_key = self._initialize_api_key("openai", kwargs.pop("api_key", None))
        default_params = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "openai_api_key": api_key,
        }
        
        # Handle organization if provided
        org_id = kwargs.pop("organization", os.getenv("OPENAI_ORG_ID"))
        if org_id:
            default_params["organization"] = org_id
        
        params = {**default_params, **kwargs}
        return ChatOpenAI(**params)
    
    def _get_anthropic_llm(self, **kwargs) -> ChatAnthropic:
        """Initialize an Anthropic LLM instance."""
        api_key = self._initialize_api_key("anthropic", kwargs.pop("api_key", None))
        default_params = {
            "model": "claude-3-sonnet-20240229",
            "temperature": 0.7,
            "anthropic_api_key": api_key,
        }
        params = {**default_params, **kwargs}
        return ChatAnthropic(**params)

    def _get_azure_openai_llm(self, **kwargs) -> AzureChatOpenAI:
        """Initialize an Azure OpenAI LLM instance."""
        openai_api_key = self._initialize_api_key("azure", kwargs.pop("api_key", None))
        azure_deployment = os.getenv("AZ_OPENAI_LLM_4_O")
        azure_endpoint = os.getenv("AZ_OPENAI_API_BASE")
        openai_api_version = os.getenv("AZ_OPENAI_API_VERSION")
        
        if not azure_endpoint:
            raise ValueError(
                "Azure endpoint is required. Set AZ_OPENAI_API_BASE env var or pass azure_endpoint"
            )
        if not azure_deployment:
            raise ValueError(
                "Azure deployment is required. Set AZ_OPENAI_LLM_4_O env var or pass azure_deployment"
            )
        if not openai_api_version:
            raise ValueError(
                "Azure API version is required. Set AZ_OPENAI_API_VERSION env var or pass openai_api_version")
        
        default_params = {
            "temperature": 0.7,
            "openai_api_key": openai_api_key,  # Azure uses this parameter
            "azure_endpoint": azure_endpoint,
            "azure_deployment": azure_deployment,
            "openai_api_version": openai_api_version,
        }
        

        
        params = {**default_params, **kwargs}
        return AzureChatOpenAI(**params)

    def _get_ollama_llm(self, **kwargs) -> ChatOllama:
        """Initialize an Ollama LLM instance."""
        default_params = {
            "model": "llama3.2",
            "temperature": 0.7,
            "base_url": "http://localhost:11434"
        }
        params = {**default_params, **kwargs}
        return ChatOllama(**params)

    def _get_gemini_llm(self, **kwargs) -> ChatGoogleGenerativeAI:
        """Initialize a Google Gemini LLM instance."""
        api_key = self._initialize_api_key("gemini", kwargs.pop("api_key", None))
        default_params = {
            "model": "gemini-1.5-flash-002",
            "temperature": 0.7,
            "google_api_key": api_key,
        }
        params = {**default_params, **kwargs}
        return ChatGoogleGenerativeAI(**params)
