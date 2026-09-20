"""
Modelo de datos para el perfil del usuario.
"""
from dataclasses import dataclass
import numpy as np
from src.models.ad import Ad

@dataclass
class UserProfile:
    """Clase que representa el perfil de un usuario."""
    id: int
    nombre: str
    intereses: np.ndarray
    tolerancia_fatiga: float

    def afinidad(self, ad: Ad) -> float:
        """
        Calcula la similitud coseno entre los intereses del usuario y los tags del anuncio.
        """
        norm_intereses = np.linalg.norm(self.intereses)
        norm_tags = np.linalg.norm(ad.tags)
        if norm_intereses == 0 or norm_tags == 0:
            return 0.0
        return float(np.dot(self.intereses, ad.tags) / (norm_intereses * norm_tags))
