"""
Módulo 4: Utilidades de visualización y comparación de resultados.

Proporciona funciones para generar tablas comparativas en consola,
análisis explicativo de los algoritmos y gráficas de convergencia
(Hill Climbing vs Simulated Annealing) usando matplotlib y tabulate.
"""

from collections import Counter
import os
import matplotlib
# Configurar backend no interactivo para asegurar que guarde PNGs sin requerir display GUI
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tabulate import tabulate

from src.algorithms.hill_climbing import HCResult
from src.algorithms.simulated_annealing import SAResult
from src.models.slate import Slate


def calcular_porcentaje_mejora(costo_hc: float, costo_sa: float) -> float:
    """
    Calcula el porcentaje de mejora de Simulated Annealing sobre Hill Climbing.
    
    Fórmula del Plan Maestro:
        % Mejora = (Costo_HC - Costo_SA) / |Costo_HC| * 100%
    
    Dado que Costo = -Fitness, un costo más negativo es mejor.
    Si SA logra un costo más negativo (mayor fitness), la diferencia
    Costo_HC - Costo_SA > 0, resultando en un porcentaje positivo.
    """
    if abs(costo_hc) < 1e-9:
        return 0.0
    return ((costo_hc - costo_sa) / abs(costo_hc)) * 100.0


def contar_categorias(slate: Slate) -> dict[str, int]:
    """Retorna un conteo de categorías presentes en un slate."""
    return dict(Counter(ad.categoria for ad in slate.anuncios))


def formatear_distribucion_categorias(slate: Slate) -> str:
    """Genera una cadena resumen con la distribución de categorías en el slate."""
    conteos = contar_categorias(slate)
    return ", ".join(f"{cat}: {cant}" for cat, cant in sorted(conteos.items()))


def mostrar_tabla_comparativa(
    hc_result: HCResult,
    sa_result: SAResult,
    costo_inicial: float,
    fitness_inicial: float,
) -> None:
    """
    Imprime una tabla comparativa exhaustiva en consola entre
    Hill Climbing y Simulated Annealing.
    """
    pct_mejora = calcular_porcentaje_mejora(hc_result.costo_final, sa_result.costo_final)
    
    filas = [
        ["Costo inicial (S_0)", f"{costo_inicial:.4f}", f"{costo_inicial:.4f}"],
        ["Costo final alcanzado", f"{hc_result.costo_final:.4f}", f"{sa_result.costo_final:.4f}"],
        ["Fitness inicial (retención)", f"{fitness_inicial:.2f} s ({fitness_inicial / 60:.2f} min)", f"{fitness_inicial:.2f} s ({fitness_inicial / 60:.2f} min)"],
        ["Fitness final (retención)", f"{hc_result.fitness_final:.2f} s ({hc_result.fitness_final / 60:.2f} min)", f"{sa_result.fitness_final:.2f} s ({sa_result.fitness_final / 60:.2f} min)"],
        ["Iteraciones totales", f"{hc_result.iteraciones_totales}", f"{sa_result.iteraciones_totales}"],
        ["Evaluaciones función de costo", f"{hc_result.evaluaciones_costo}", f"{sa_result.evaluaciones_costo}"],
        ["Movimientos aceptados", f"{hc_result.movimientos_aceptados}", "N/A (Criterio térmico)"],
        ["Peores soluciones aceptadas", "0 (Rechazo estricto)", f"{sa_result.peores_aceptadas} (Escapes de bache)"],
        ["Punto de estancamiento", f"Iteración {hc_result.iteracion_estancamiento} (Óptimo local)", "No aplica (Exploración global)"],
        ["Categorías representadas", f"{len(contar_categorias(hc_result.mejor_slate))}", f"{len(contar_categorias(sa_result.mejor_slate))}"],
        ["% Mejora SA sobre HC", "—", f"+{pct_mejora:.2f} %" if pct_mejora >= 0 else f"{pct_mejora:.2f} %"],
    ]

    headers = [
        "Métrica / Indicador",
        "Hill Climbing (Módulo 2)",
        "Simulated Annealing (Módulo 3)"
    ]

    print("\n" + "=" * 80)
    print("        MÓDULO 4: TABLA COMPARATIVA DE RESULTADOS EXPERIMENTALES")
    print("=" * 80)
    print(tabulate(filas, headers=headers, tablefmt="grid", stralign="left"))
    print("=" * 80)


def mostrar_composicion_slates(hc_result: HCResult, sa_result: SAResult) -> None:
    """
    Imprime en formato tabular la secuencia de anuncios seleccionada por cada algoritmo,
    permitiendo contrastar la diversidad temática y la mitigación de fatiga.
    """
    print("\n" + "=" * 80)
    print("        COMPOSICIÓN DE LA PARRILLA (SLATE) FINAL: HC vs SA")
    print("=" * 80)

    filas = []
    k = max(len(hc_result.mejor_slate), len(sa_result.mejor_slate))

    for i in range(k):
        ad_hc = hc_result.mejor_slate[i] if i < len(hc_result.mejor_slate) else None
        ad_sa = sa_result.mejor_slate[i] if i < len(sa_result.mejor_slate) else None

        info_hc = (
            f"[ID:{ad_hc.id:>2}] {ad_hc.categoria:<12} | {ad_hc.duracion:.0f}s"
            if ad_hc else "—"
        )
        info_sa = (
            f"[ID:{ad_sa.id:>2}] {ad_sa.categoria:<12} | {ad_sa.duracion:.0f}s"
            if ad_sa else "—"
        )

        filas.append([f"Slot {i + 1}", info_hc, info_sa])

    headers = ["Ranura (Slot)", "Selección Hill Climbing", "Selección Simulated Annealing"]
    print(tabulate(filas, headers=headers, tablefmt="grid", stralign="left"))

    print("\nDistribución de Categorías:")
    print(f"  * Hill Climbing:       {formatear_distribucion_categorias(hc_result.mejor_slate)}")
    print(f"  * Simulated Annealing: {formatear_distribucion_categorias(sa_result.mejor_slate)}")
    print("=" * 80)


def mostrar_explicacion_diferencia(hc_result: HCResult, sa_result: SAResult) -> None:
    """
    Imprime una explicación analítica detallada de por qué ocurrió la diferencia
    entre ambos algoritmos basándose en la topología de la función de fatiga
    y la combinatoria de anuncios.
    """
    pct_mejora = calcular_porcentaje_mejora(hc_result.costo_final, sa_result.costo_final)
    ganancia_segundos = sa_result.fitness_final - hc_result.fitness_final

    print("\n" + "=" * 80)
    print("     ANÁLISIS TEÓRICO Y JUSTIFICACIÓN DEL RENDIMIENTO COMPARATIVO")
    print("=" * 80)
    print(f"""
1. NATURALEZA DEL ESTANCAMIENTO EN HILL CLIMBING:
   * Hill Climbing opera bajo una regla de transición estrictamente codiciosa (greedy):
     acepta un nuevo estado S' si y solo si Costo(S') < Costo(S).
   * En la iteración {hc_result.iteracion_estancamiento}, el algoritmo evaluó una vecindad completa
     sin hallar una mejora directa, quedando atrapado en una meseta o cima local.
   * Aceptó únicamente {hc_result.movimientos_aceptados} movimientos de mejora antes de que la penalización
     por fatiga publicitaria (gamma_fatiga) creara un valle de costo que ninguna mutación simple
     (swap o replace) pudo franquear sin empeorar temporalmente la retención.

2. MECANISMO DE ESCAPE EN SIMULATED ANNEALING:
   * Simulated Annealing implementó el criterio estocástico de Boltzmann:
     P(Aceptar) = exp(-Delta_C / T).
   * Durante su régimen de enfriamiento, aceptó {sa_result.peores_aceptadas} soluciones temporalmente
     subóptimas (peores).
   * Estos movimientos transitorios permitieron alterar simultáneamente la alternancia de categorías
     y escapar de los óptimos locales donde HC quedó varado.
   * Conforme la temperatura T descendió hacia T_min, el algoritmo transitó suavemente hacia
     una búsqueda local de afinamiento fino (explotación).

3. IMPACTO EN EL TIEMPO RETENIDO Y NEGOCIO:
   * Ganancia neta de Simulated Annealing: +{ganancia_segundos:.2f} segundos de atención ({ganancia_segundos / 60:.2f} min).
   * Porcentaje de optimización sobre Hill Climbing: +{pct_mejora:.2f}%.
   * La secuencia de SA mitiga la ceguera publicitaria (Ad Blindness) al intercalar temas
     afines sin saturar las ranuras contiguas con la misma categoría.
""")
    print("=" * 80)


def graficar_convergencia(
    hc_historial: list[float],
    sa_historial: list[float],
    tipo: str = "ambos",
    guardar: bool = True,
    filepath: str = "convergencia_hc_vs_sa.png",
    iter_estancamiento_hc: int | None = None,
) -> str:
    """
    Genera y guarda una gráfica comparativa de convergencia de alta calidad.
    
    Parámetros
    ----------
    hc_historial : list[float]
        Historial de costos por iteración de Hill Climbing.
    sa_historial : list[float]
        Historial de costos por iteración de Simulated Annealing.
    tipo : str
        'ambos', 'costo' o 'fitness'.
    guardar : bool
        Si True, guarda la imagen en disco.
    filepath : str
        Ruta del archivo PNG destino.
    iter_estancamiento_hc : int | None
        Iteración donde HC se estancó.
    
    Retorna
    -------
    str
        Ruta absoluta del archivo generado.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=150)
    
    # ---------------- Gráfico 1: Curva de Costo (Minimización) ----------------
    ax1.plot(hc_historial, label="Hill Climbing (Local)", color="#E63946", linewidth=2.0, alpha=0.9)
    ax1.plot(sa_historial, label="Simulated Annealing (Estocástico)", color="#1D3557", linewidth=1.8, alpha=0.85)

    if iter_estancamiento_hc is not None and iter_estancamiento_hc < len(hc_historial):
        costo_estancado = hc_historial[iter_estancamiento_hc]
        ax1.scatter([iter_estancamiento_hc], [costo_estancado], color="#D62828", s=80, zorder=5)
        ax1.annotate(
            f"Estancamiento HC\n(Iter {iter_estancamiento_hc})",
            xy=(iter_estancamiento_hc, costo_estancado),
            xytext=(iter_estancamiento_hc + max(20, int(len(sa_historial) * 0.05)), costo_estancado + 8),
            arrowprops=dict(facecolor="#D62828", shrink=0.08, width=1.5, headwidth=6),
            fontsize=9,
            fontweight="bold",
            color="#D62828"
        )

    ax1.set_title("Evolución de la Función de Costo (Costo = -Fitness)", fontsize=11, fontweight="bold", pad=10)
    ax1.set_xlabel("Iteración / Evaluación", fontsize=10)
    ax1.set_ylabel("Costo (Menor es mejor)", fontsize=10)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper right", framealpha=0.9)

    # ---------------- Gráfico 2: Curva de Retención (Fitness en Segundos) ----------------
    # Fitness = -Costo
    hc_fitness = [-c for c in hc_historial]
    sa_fitness = [-c for c in sa_historial]

    ax2.plot(hc_fitness, label="Hill Climbing", color="#E63946", linewidth=2.0, alpha=0.9)
    ax2.plot(sa_fitness, label="Simulated Annealing", color="#2A9D8F", linewidth=1.8, alpha=0.85)

    # Líneas horizontales de referencia de resultado final
    final_hc = hc_fitness[-1]
    final_sa = sa_fitness[-1]
    ax2.axhline(final_hc, color="#E63946", linestyle=":", alpha=0.7, label=f"Óptimo HC: {final_hc:.1f}s")
    ax2.axhline(final_sa, color="#2A9D8F", linestyle=":", alpha=0.7, label=f"Óptimo SA: {final_sa:.1f}s")

    ax2.set_title("Tiempo de Retención Retenido (Fitness en Segundos)", fontsize=11, fontweight="bold", pad=10)
    ax2.set_xlabel("Iteración / Evaluación", fontsize=10)
    ax2.set_ylabel("Segundos de Atención Retenida", fontsize=10)
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="lower right", framealpha=0.9)

    plt.suptitle("Comparativa de Convergencia: Búsqueda Local vs Búsqueda Estocástica", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()

    ruta_absoluta = os.path.abspath(filepath)
    if guardar:
        plt.savefig(filepath, bbox_inches="tight")
        print(f"\n[+] Gráfica de convergencia generada exitosamente en:\n    {ruta_absoluta}")
    
    plt.close(fig)
    return ruta_absoluta
