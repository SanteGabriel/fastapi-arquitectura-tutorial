"""
Contador de tokens simple para Chat Service
"""

import re
from typing import Optional


class TokenCounter:
    """Contador simple de tokens (aproximado)"""
    
    def __init__(self):
        # Factores de conversión aproximados
        self.words_per_token = 0.75  # Aproximadamente 1.33 tokens por palabra
        
    def count_tokens(self, text: str) -> int:
        """Contar tokens de manera aproximada"""
        if not text:
            return 0
        
        # Método simple: contar palabras y convertir a tokens
        words = len(text.split())
        tokens = int(words / self.words_per_token)
        
        # Ajustes por caracteres especiales y código
        if self._has_code_blocks(text):
            tokens = int(tokens * 1.2)  # Código tiende a usar más tokens
        
        if self._has_special_chars(text):
            tokens = int(tokens * 1.1)  # Caracteres especiales
        
        return max(tokens, 1)  # Mínimo 1 token
    
    def _has_code_blocks(self, text: str) -> bool:
        """Detectar bloques de código"""
        return "```" in text or "    " in text or "\t" in text
    
    def _has_special_chars(self, text: str) -> bool:
        """Detectar caracteres especiales"""
        special_pattern = r'[{}[\]().,;:!?@#$%^&*+=~`|\\/<>"\'-]'
        return bool(re.search(special_pattern, text))
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimar costo basado en tokens"""
        # Precios aproximados por 1K tokens (USD)
        pricing = {
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-4": {"input": 0.01, "output": 0.03},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        }
        
        if model not in pricing:
            return 0.0
        
        input_cost = (input_tokens / 1000) * pricing[model]["input"]
        output_cost = (output_tokens / 1000) * pricing[model]["output"]
        
        return input_cost + output_cost
