"""
Utilidades para manejo de contraseñas
"""

import bcrypt
import re
from typing import Optional


class PasswordManager:
    """Manejo seguro de contraseñas"""
    
    def __init__(self):
        self.salt_rounds = 12
    
    def hash_password(self, password: str) -> str:
        """Generar hash seguro de contraseña"""
        salt = bcrypt.gensalt(rounds=self.salt_rounds)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verificar contraseña contra hash"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                password_hash.encode('utf-8')
            )
        except Exception:
            return False
    
    def validate_password_strength(self, password: str) -> dict:
        """Validar fortaleza de contraseña"""
        errors = []
        score = 0
        
        # Longitud mínima
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        else:
            score += 1
        
        # Letra minúscula
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        else:
            score += 1
        
        # Letra mayúscula  
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        else:
            score += 1
        
        # Número
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        else:
            score += 1
        
        # Carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        else:
            score += 1
        
        # Longitud extra
        if len(password) >= 12:
            score += 1
        
        # Determinar nivel de fortaleza
        if score <= 2:
            strength = "weak"
        elif score <= 4:
            strength = "medium"
        else:
            strength = "strong"
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "strength": strength,
            "score": score
        }
    
    def generate_password_reset_token(self) -> str:
        """Generar token para reset de contraseña"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def is_password_breached(self, password: str) -> bool:
        """Verificar si la contraseña está en listas de contraseñas comprometidas"""
        # Lista básica de contraseñas comunes (en producción usarías HaveIBeenPwned API)
        common_passwords = {
            "123456", "password", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "1234567890", "abc123",
            "Password1", "password1", "12345678", "qwerty123",
            "1q2w3e4r", "admin123", "Password123", "root", "toor"
        }
        
        return password.lower() in {p.lower() for p in common_passwords}
    
    def suggest_password_improvements(self, password: str) -> list:
        """Sugerir mejoras para la contraseña"""
        suggestions = []
        
        if len(password) < 12:
            suggestions.append("Consider using a longer password (12+ characters)")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            suggestions.append("Add special characters for better security")
        
        if re.search(r'(.)\1{2,}', password):
            suggestions.append("Avoid repeating characters")
        
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            suggestions.append("Avoid sequential numbers")
        
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            suggestions.append("Avoid sequential letters")
        
        return suggestions
