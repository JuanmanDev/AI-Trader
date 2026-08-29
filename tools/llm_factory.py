"""
LLM Factory Module

This module provides a factory for creating different types of LLM instances
supporting OpenAI, Ollama, and other providers.
"""

import os
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()

# Import LLM classes
try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  langchain-openai not installed")

try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️  langchain-ollama not installed")

try:
    from langchain_community.chat_models import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LLMFactory:
    """
    Factory class for creating LLM instances based on provider type
    """
    
    PROVIDER_OPENAI = "openai"
    PROVIDER_OLLAMA = "ollama"
    PROVIDER_ANTHROPIC = "anthropic"
    
    @staticmethod
    def detect_provider(model_name: str) -> str:
        """
        Detect LLM provider from model name
        
        Args:
            model_name: Model name (e.g., "openai/gpt-4", "ollama/llama2", "gpt-4")
            
        Returns:
            Provider type string
        """
        model_lower = model_name.lower()
        
        # Check for explicit provider prefix
        if "/" in model_name:
            prefix = model_name.split("/")[0].lower()
            if prefix in ["openai", "ollama", "anthropic"]:
                return prefix
        
        # Detect from model name patterns
        if any(x in model_lower for x in ["gpt", "o1", "chatgpt"]):
            return LLMFactory.PROVIDER_OPENAI
        elif any(x in model_lower for x in ["llama", "mistral", "mixtral", "phi", "gemma"]):
            return LLMFactory.PROVIDER_OLLAMA
        elif any(x in model_lower for x in ["claude", "anthropic"]):
            return LLMFactory.PROVIDER_ANTHROPIC
        
        # Default to OpenAI (for compatibility)
        return LLMFactory.PROVIDER_OPENAI
    
    @staticmethod
    def create_llm(
        model_name: str,
        provider: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Create an LLM instance based on provider type
        
        Args:
            model_name: Model name (e.g., "gpt-4", "llama2", "openai/gpt-4")
            provider: Provider type (auto-detected if None)
            base_url: Base URL for API (provider-specific)
            api_key: API key (provider-specific)
            temperature: Temperature for sampling
            max_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific arguments
            
        Returns:
            LLM instance
        """
        # Auto-detect provider if not specified
        if provider is None:
            provider = LLMFactory.detect_provider(model_name)
        
        # Extract actual model name (remove provider prefix if present)
        if "/" in model_name:
            actual_model = model_name.split("/", 1)[1]
        else:
            actual_model = model_name
        
        print(f"🤖 Creating LLM: provider={provider}, model={actual_model}")
        
        # Create LLM based on provider
        if provider == LLMFactory.PROVIDER_OPENAI:
            return LLMFactory._create_openai(
                actual_model, base_url, api_key, temperature, max_tokens, **kwargs
            )
        elif provider == LLMFactory.PROVIDER_OLLAMA:
            return LLMFactory._create_ollama(
                actual_model, base_url, temperature, max_tokens, **kwargs
            )
        elif provider == LLMFactory.PROVIDER_ANTHROPIC:
            return LLMFactory._create_anthropic(
                actual_model, api_key, temperature, max_tokens, **kwargs
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def _create_openai(
        model_name: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Any:
        """Create OpenAI LLM instance"""
        if not OPENAI_AVAILABLE:
            raise ImportError("langchain-openai not installed. Install with: pip install langchain-openai")
        
        # Get API key from env if not provided
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        
        # Get base URL from env if not provided
        if base_url is None:
            base_url = os.getenv("OPENAI_API_BASE")
        
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        llm_kwargs = {
            "model": model_name,
            "api_key": api_key,
            "temperature": temperature,
            "max_retries": kwargs.get("max_retries", 3),
            "timeout": kwargs.get("timeout", 30),
        }
        
        if base_url:
            llm_kwargs["base_url"] = base_url
        
        if max_tokens:
            llm_kwargs["max_tokens"] = max_tokens
        
        print(f"✅ Creating OpenAI LLM with model: {model_name}")
        return ChatOpenAI(**llm_kwargs)
    
    @staticmethod
    def _create_ollama(
        model_name: str,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Any:
        """Create Ollama LLM instance"""
        if not OLLAMA_AVAILABLE:
            raise ImportError("langchain-ollama not installed. Install with: pip install langchain-ollama")
        
        # Get base URL from env if not provided (default Ollama URL)
        if base_url is None:
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        llm_kwargs = {
            "model": model_name,
            "base_url": base_url,
            "temperature": temperature,
        }
        
        if max_tokens:
            llm_kwargs["num_predict"] = max_tokens
        
        print(f"✅ Creating Ollama LLM with model: {model_name} at {base_url}")
        return ChatOllama(**llm_kwargs)
    
    @staticmethod
    def _create_anthropic(
        model_name: str,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Any:
        """Create Anthropic LLM instance"""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("langchain-community not installed. Install with: pip install langchain-community")
        
        # Get API key from env if not provided
        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
        
        llm_kwargs = {
            "model": model_name,
            "anthropic_api_key": api_key,
            "temperature": temperature,
        }
        
        if max_tokens:
            llm_kwargs["max_tokens"] = max_tokens
        
        print(f"✅ Creating Anthropic LLM with model: {model_name}")
        return ChatAnthropic(**llm_kwargs)


def create_llm_from_config(
    model_config: dict,
    fallback_base_url: Optional[str] = None,
    fallback_api_key: Optional[str] = None
) -> Any:
    """
    Create LLM from configuration dictionary (for easy integration with existing code)
    
    Args:
        model_config: Configuration dictionary with model settings
        fallback_base_url: Fallback base URL if not in config
        fallback_api_key: Fallback API key if not in config
        
    Returns:
        LLM instance
    """
    model_name = model_config.get("basemodel", model_config.get("name", "gpt-4"))
    provider = model_config.get("provider")  # Optional explicit provider
    base_url = model_config.get("openai_base_url", fallback_base_url)
    api_key = model_config.get("openai_api_key", fallback_api_key)
    
    return LLMFactory.create_llm(
        model_name=model_name,
        provider=provider,
        base_url=base_url,
        api_key=api_key,
        temperature=model_config.get("temperature", 0.7),
        max_tokens=model_config.get("max_tokens"),
    )
