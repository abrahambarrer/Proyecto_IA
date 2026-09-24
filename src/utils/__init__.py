"""
Utilidades para generación, carga, guardado de datos y visualización comparativa.
"""

from src.utils.data_generator import (
    generar_catalogo,
    generar_perfil_usuario,
    guardar_catalogo_csv,
    guardar_perfil_json,
)
from src.utils.data_loader import (
    cargar_catalogo,
    cargar_perfil_usuario,
    generar_slate_inicial,
)
from src.utils.visualizer import (
    calcular_porcentaje_mejora,
    graficar_convergencia,
    mostrar_composicion_slates,
    mostrar_explicacion_diferencia,
    mostrar_tabla_comparativa,
)

__all__ = [
    "generar_catalogo",
    "generar_perfil_usuario",
    "guardar_catalogo_csv",
    "guardar_perfil_json",
    "cargar_catalogo",
    "cargar_perfil_usuario",
    "generar_slate_inicial",
    "calcular_porcentaje_mejora",
    "graficar_convergencia",
    "mostrar_composicion_slates",
    "mostrar_explicacion_diferencia",
    "mostrar_tabla_comparativa",
]
