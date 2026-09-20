"""
Modelo de datos para la secuencia de anuncios (Slate).
"""
import copy
from src.models.ad import Ad

class Slate:
    """Clase que representa una secuencia de anuncios asignados a K slots."""
    def __init__(self, anuncios: list[Ad]):
        self.anuncios = anuncios

    def copy(self) -> 'Slate':
        """Devuelve una copia profunda del slate."""
        return Slate(copy.deepcopy(self.anuncios))

    def __repr__(self) -> str:
        secuencia = ", ".join([f"(ID:{ad.id}, Cat:{ad.categoria})" for ad in self.anuncios])
        return f"Slate[{secuencia}]"

    def __len__(self) -> int:
        return len(self.anuncios)

    def __getitem__(self, idx: int) -> Ad:
        return self.anuncios[idx]

    def __setitem__(self, idx: int, value: Ad) -> None:
        self.anuncios[idx] = value
