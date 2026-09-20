"""
Modelo de datos para un anuncio digital.
"""
from dataclasses import dataclass
import numpy as np

@dataclass
class Ad:
    """Clase que representa un anuncio digital."""
    id: int
    titulo: str
    categoria: str
    duracion: float
    tasa_retencion_base: float
    tags: np.ndarray

    def __repr__(self) -> str:
        return f"Ad(id={self.id}, titulo='{self.titulo}', categoria='{self.categoria}', duracion={self.duracion})"
