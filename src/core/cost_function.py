"""
Funciones para calcular el fitness y el costo de una secuencia de anuncios.
"""
import math
from src.models.ad import Ad
from src.models.user import UserProfile
from src.models.slate import Slate

def _calcular_factor_fatiga(slate: Slate, posicion: int, lambda_val: float) -> float:
    """Calcula el factor de fatiga gamma para un slot dado.
    
    gamma_fatiga(S, i) = PRODUCTO sobre todos los j < i donde cat(a_j) == cat(a_i) de lambda^(1/(i-j))
    
    Si ningún anuncio previo tiene la misma categoría, gamma = 1.0 (sin penalización).
    """
    categoria_actual = slate[posicion].categoria
    gamma = 1.0
    for j in range(posicion):
        if slate[j].categoria == categoria_actual:
            distancia = posicion - j
            gamma *= lambda_val ** (1.0 / distancia)
    return gamma

def calcular_tiempo_visualizacion_slot(ad: Ad, user: UserProfile, slate: Slate, posicion: int, lambda_fatiga: float) -> float:
    """Calcula el tiempo de visualización esperado para un anuncio en un slot específico.
    
    T_i(S) = D(a) * Afinidad(u, a) * gamma_fatiga(S, i) * delta_posicion(i)
    """
    # D(a): duración del anuncio
    duracion = ad.duracion
    
    # Afinidad(u, a): similitud coseno entre perfil del usuario y tags del anuncio
    afinidad = user.afinidad(ad)
    
    # delta_posicion(i): factor de desgaste natural de la sesión = 1 / sqrt(i+1)
    # Usamos i+1 porque las posiciones empiezan en 0 pero la fórmula en 1
    delta_posicion = 1.0 / math.sqrt(posicion + 1)
    
    # gamma_fatiga(S, i): penalización por repetición de categoría
    gamma_fatiga = _calcular_factor_fatiga(slate, posicion, lambda_fatiga)
    
    return duracion * afinidad * gamma_fatiga * delta_posicion

def calcular_fitness(slate: Slate, user: UserProfile, lambda_fatiga: float) -> float:
    """Calcula el fitness total F(S) = suma de T_i para todos los slots. A MAXIMIZAR."""
    total = 0.0
    for i in range(len(slate)):
        total += calcular_tiempo_visualizacion_slot(slate[i], user, slate, i, lambda_fatiga)
    return total

def calcular_costo(slate: Slate, user: UserProfile, lambda_fatiga: float) -> float:
    """Calcula el costo = -F(S). A MINIMIZAR.
    Menor costo = mayor tiempo de visualización."""
    return -calcular_fitness(slate, user, lambda_fatiga)
