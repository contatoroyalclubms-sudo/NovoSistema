"""
Configurações específicas da OpenAI
Sistema Universal de Gestão de Eventos
"""

import os
from typing import Optional

class OpenAIConfig:
    """Configurações da OpenAI API"""
    
    # Chave da API OpenAI
    API_KEY: str = "your-openai-api-key-here"
    
    # Configurações do modelo
    MODEL: str = "gpt-4o-mini"
    MAX_TOKENS: int = 1500
    TEMPERATURE: float = 0.7
    
    # Configurações de timeout
    TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    
    @classmethod
    def get_api_key(cls) -> str:
        """Obtém a chave da API, priorizando variável de ambiente"""
        return os.getenv("OPENAI_API_KEY", cls.API_KEY)
    
    @classmethod
    def get_model(cls) -> str:
        """Obtém o modelo a ser usado"""
        return os.getenv("OPENAI_MODEL", cls.MODEL)
    
    @classmethod
    def get_max_tokens(cls) -> int:
        """Obtém o máximo de tokens"""
        return int(os.getenv("OPENAI_MAX_TOKENS", cls.MAX_TOKENS))
    
    @classmethod
    def get_temperature(cls) -> float:
        """Obtém a temperatura do modelo"""
        return float(os.getenv("OPENAI_TEMPERATURE", cls.TEMPERATURE))

# Instância global
openai_config = OpenAIConfig()
