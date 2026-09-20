"""
Operadores de vecindario para generar vecinos en los algoritmos de búsqueda.
"""
import copy
import numpy as np
from src.models.slate import Slate
from src.models.ad import Ad

def swap(slate: Slate, rng: np.random.Generator) -> Slate:
    """Intercambia la posición de dos anuncios aleatorios en el slate."""
    nuevo_slate = slate.copy()
    n = len(nuevo_slate)
    if n >= 2:
        idx1, idx2 = rng.choice(n, size=2, replace=False)
        nuevo_slate[idx1], nuevo_slate[idx2] = nuevo_slate[idx2], nuevo_slate[idx1]
    return nuevo_slate

def replace(slate: Slate, catalogo: list[Ad], rng: np.random.Generator) -> Slate:
    """Reemplaza un anuncio en una posición aleatoria por otro del catálogo que no esté en el slate actual."""
    nuevo_slate = slate.copy()
    n = len(nuevo_slate)
    if n > 0:
        idx_reemplazar = rng.integers(0, n)
        
        # Obtener IDs actuales para no repetir
        ids_actuales = {ad.id for ad in nuevo_slate.anuncios}
        candidatos = [ad for ad in catalogo if ad.id not in ids_actuales]
        
        if candidatos:
            nuevo_ad = rng.choice(candidatos)
            nuevo_slate[idx_reemplazar] = copy.deepcopy(nuevo_ad)
            
    return nuevo_slate

def invert(slate: Slate, rng: np.random.Generator) -> Slate:
    """Invierte una subsecuencia contigua aleatoria del slate."""
    nuevo_slate = slate.copy()
    n = len(nuevo_slate)
    if n >= 2:
        idx1, idx2 = rng.choice(n, size=2, replace=False)
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1
        
        nuevo_slate.anuncios[idx1:idx2+1] = list(reversed(nuevo_slate.anuncios[idx1:idx2+1]))
        
    return nuevo_slate

def generar_vecino(slate: Slate, catalogo: list[Ad], operadores: list[str], rng: np.random.Generator) -> tuple[Slate, str]:
    """Genera un estado vecino aplicando un operador aleatorio. Retorna (nuevo_slate, nombre_operador)."""
    op = rng.choice(operadores)
    
    if op == 'swap':
        vecino = swap(slate, rng)
    elif op == 'replace':
        vecino = replace(slate, catalogo, rng)
    elif op == 'invert':
        vecino = invert(slate, rng)
    else:
        raise ValueError(f"Operador desconocido: {op}")
        
    return vecino, op
