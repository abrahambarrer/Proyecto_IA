"""
Funciones para cargar datos desde archivos y generar estados iniciales.
"""
import csv
import json
import numpy as np
from src.models.ad import Ad
from src.models.user import UserProfile
from src.models.slate import Slate

def cargar_catalogo(filepath: str = 'data/ads_catalog.csv') -> list[Ad]:
    """Carga el catálogo de anuncios desde un archivo CSV."""
    catalogo = []
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tags = np.array(json.loads(row['tags']))
            ad = Ad(
                id=int(row['id']),
                titulo=row['titulo'],
                categoria=row['categoria'],
                duracion=float(row['duracion']),
                tasa_retencion_base=float(row['tasa_retencion_base']),
                tags=tags
            )
            catalogo.append(ad)
    return catalogo

def cargar_perfil_usuario(filepath: str = 'data/user_profile.json') -> UserProfile:
    """Carga el perfil del usuario desde un archivo JSON."""
    with open(filepath, mode='r', encoding='utf-8') as f:
        datos = json.load(f)
        
    intereses = np.array(datos['intereses'])
    
    return UserProfile(
        id=datos['id'],
        nombre=datos['nombre'],
        intereses=intereses,
        tolerancia_fatiga=datos['tolerancia_fatiga']
    )

def generar_slate_inicial(catalogo: list[Ad], k: int, seed: int = 42) -> Slate:
    """Genera un slate inicial aleatorio seleccionando K anuncios del catálogo."""
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(catalogo), size=k, replace=False)
    anuncios = [catalogo[i] for i in indices]
    return Slate(anuncios)
