"""
Generador de datos sintéticos realistas para anuncios y perfiles de usuarios.
"""
import os
import csv
import json
import numpy as np
from src.models.ad import Ad
from src.models.user import UserProfile
from src.config import CATEGORIES, NUM_CATEGORIES, AD_DURATION_MIN, AD_DURATION_MAX

def generar_catalogo(num_anuncios: int = 100, seed: int = 42) -> list[Ad]:
    """Genera un catálogo sintético de anuncios digitales."""
    rng = np.random.default_rng(seed)
    catalogo = []
    
    titulos_por_categoria = {
        'Gaming': ['Fortnite', 'League of Legends', 'FIFA', 'Call of Duty', 'Minecraft'],
        'Moda': ['Zara', 'Nike', 'Adidas', 'H&M', 'Shein'],
        'Finanzas': ['Banco X', 'Inversiones Y', 'Crypto Z', 'Seguros A', 'Trading B'],
        'Gastronomía': ['McDonald\'s', 'Starbucks', 'Uber Eats', 'Burger King', 'Domino\'s'],
        'Tecnología': ['Apple', 'Samsung', 'Sony', 'Microsoft', 'Logitech'],
        'Fitness': ['GymShark', 'Nike Training', 'Fitbit', 'MyFitnessPal', 'Peloton']
    }
    
    for i in range(num_anuncios):
        idx_categoria = rng.integers(0, NUM_CATEGORIES)
        categoria = CATEGORIES[idx_categoria]
        
        duracion = float(rng.integers(AD_DURATION_MIN, AD_DURATION_MAX + 1))
        tasa_retencion_base = float(rng.uniform(0.3, 1.0))
        
        # Tags: dominante en la categoría actual con algo de ruido
        tags = rng.uniform(0, 0.2, NUM_CATEGORIES)
        tags[idx_categoria] = rng.uniform(0.8, 1.0)
        tags = tags / np.sum(tags) # Normalización
        
        marca = rng.choice(titulos_por_categoria[categoria])
        titulo = f"Ad de {marca}"
        
        ad = Ad(
            id=i,
            titulo=titulo,
            categoria=categoria,
            duracion=duracion,
            tasa_retencion_base=tasa_retencion_base,
            tags=tags
        )
        catalogo.append(ad)
        
    return catalogo

def generar_perfil_usuario(seed: int = 42) -> UserProfile:
    """Genera un perfil de usuario de prueba con intereses definidos."""
    rng = np.random.default_rng(seed)
    
    # Intereses predefinidos
    intereses = np.zeros(NUM_CATEGORIES)
    
    for i, cat in enumerate(CATEGORIES):
        if cat == 'Gaming':
            intereses[i] = 0.85
        elif cat == 'Tecnología':
            intereses[i] = 0.75
        elif cat == 'Fitness':
            intereses[i] = 0.50
        elif cat == 'Moda':
            intereses[i] = 0.30
        elif cat == 'Gastronomía':
            intereses[i] = 0.25
        elif cat == 'Finanzas':
            intereses[i] = 0.15
            
    # Añadir un poco de ruido
    ruido = rng.uniform(-0.05, 0.05, NUM_CATEGORIES)
    intereses = np.clip(intereses + ruido, 0.0, 1.0)
    
    tolerancia_fatiga = 0.7
    
    return UserProfile(
        id=1,
        nombre="Usuario de Prueba",
        intereses=intereses,
        tolerancia_fatiga=tolerancia_fatiga
    )

def guardar_catalogo_csv(catalogo: list[Ad], filepath: str = 'data/ads_catalog.csv') -> None:
    """Guarda el catálogo en formato CSV."""
    os.makedirs(os.dirname(filepath), exist_ok=True)
    
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'titulo', 'categoria', 'duracion', 'tasa_retencion_base', 'tags'])
        for ad in catalogo:
            tags_str = json.dumps(ad.tags.tolist())
            writer.writerow([ad.id, ad.titulo, ad.categoria, ad.duracion, ad.tasa_retencion_base, tags_str])
            
def guardar_perfil_json(user: UserProfile, filepath: str = 'data/user_profile.json') -> None:
    """Guarda el perfil del usuario en formato JSON."""
    os.makedirs(os.dirname(filepath), exist_ok=True)
    
    datos = {
        'id': user.id,
        'nombre': user.nombre,
        'intereses': user.intereses.tolist(),
        'tolerancia_fatiga': user.tolerancia_fatiga
    }
    
    with open(filepath, mode='w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)
