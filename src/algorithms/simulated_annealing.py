"""
Módulo 3: Algoritmo de Búsqueda Estocástica — Simulated Annealing.

Implementa búsqueda con criterio de Boltzmann: acepta vecinos que mejoran el costo
y, con cierta probabilidad que decae con la temperatura, acepta temporalmente 
vecinos peores para escapar de óptimos locales.
"""
import math
import numpy as np
from dataclasses import dataclass, field

from src.models.ad import Ad
from src.models.user import UserProfile
from src.models.slate import Slate
from src.core.cost_function import calcular_costo, calcular_fitness
from src.core.neighborhood import generar_vecino
from src import config

@dataclass
class SAResult:
    """Resultado completo de una ejecución de Simulated Annealing."""
    mejor_slate: Slate
    costo_final: float
    fitness_final: float
    iteraciones_totales: int
    evaluaciones_costo: int
    peores_aceptadas: int
    historial_costos: list[float] = field(default_factory=list)
    historial_fitness: list[float] = field(default_factory=list)

def run_simulated_annealing(
    slate_inicial: Slate,
    catalogo: list[Ad],
    user: UserProfile,
    lambda_fatiga: float = config.FATIGUE_LAMBDA,
    t_inicial: float = config.SA_TEMP_INITIAL,
    alpha: float = config.SA_ALPHA,
    t_min: float = config.SA_TEMP_MIN,
    iters_por_temp: int = config.SA_ITERATIONS_PER_TEMP,
    operadores: list[str] = None,
    seed: int = config.RANDOM_SEED,
    verbose: bool = True,
) -> SAResult:
    """
    Ejecuta el algoritmo Simulated Annealing.
    """
    if operadores is None:
        operadores = config.NEIGHBOR_OPERATORS

    rng = np.random.default_rng(seed)

    # Estado inicial
    estado_actual = slate_inicial.copy()
    costo_actual = calcular_costo(estado_actual, user, lambda_fatiga)
    fitness_actual = calcular_fitness(estado_actual, user, lambda_fatiga)
    evaluaciones = 1

    # Guardián de la mejor solución global
    mejor_slate = estado_actual.copy()
    mejor_costo = costo_actual
    mejor_fitness = fitness_actual

    # Historiales
    historial_costos = [costo_actual]
    historial_fitness = [fitness_actual]

    T = t_inicial
    paso_global = 0
    peores_aceptadas = 0

    if verbose:
        print("=" * 70)
        print("       SIMULATED ANNEALING — BÚSQUEDA ESTOCÁSTICA")
        print("=" * 70)
        print(f"  Estado inicial:  {estado_actual}")
        print(f"  Costo inicial:   {costo_actual:.4f}")
        print(f"  Fitness inicial: {fitness_actual:.4f}s de visualización")
        print(f"  Temperatura T0:  {t_inicial} | Alpha: {alpha} | T_min: {t_min}")
        print(f"  Iters por Temp:  {iters_por_temp}")
        print(f"  Operadores:      {operadores}")
        print(f"  Seed:            {seed}")
        print("-" * 70)

    # Bucle Térmico
    while T > t_min:
        for _ in range(iters_por_temp):
            paso_global += 1
            
            vecino, operador_usado = generar_vecino(estado_actual, catalogo, operadores, rng)
            costo_vecino = calcular_costo(vecino, user, lambda_fatiga)
            evaluaciones += 1
            
            delta_costo = costo_vecino - costo_actual
            aceptar = False
            
            if delta_costo < 0:
                # Mejora
                aceptar = True
            else:
                # Criterio de Boltzmann
                exponente = -delta_costo / T
                if exponente < -700:
                    probabilidad = 0.0
                else:
                    probabilidad = math.exp(exponente)
                
                if rng.random() < probabilidad:
                    aceptar = True
                    peores_aceptadas += 1
                    
                    if verbose and peores_aceptadas % 5 == 0:
                        print(f"  [Paso {paso_global:>4d} | T={T:06.2f}] Peor solución aceptada "
                              f"(ΔC = {delta_costo:+.4f}, Prob = {probabilidad:.3f}) -> SALIENDO DE ÓPTIMO LOCAL")

            if aceptar:
                estado_actual = vecino
                costo_actual = costo_vecino
                # Solo calculamos el fitness del estado actual si fue aceptado para ahorrar cómputo
                fitness_actual = calcular_fitness(estado_actual, user, lambda_fatiga)
                
                if costo_actual < mejor_costo:
                    mejor_slate = estado_actual.copy()
                    mejor_costo = costo_actual
                    mejor_fitness = fitness_actual
                    
            historial_costos.append(costo_actual)
            historial_fitness.append(fitness_actual)
            
        # Enfriamiento geométrico
        T *= alpha

    if verbose:
        print()
        print("=" * 70)
        print("       RESULTADO FINAL — SIMULATED ANNEALING")
        print("=" * 70)
        print(f"  Mejor slate encontrado:   {mejor_slate}")
        print(f"  Costo final:              {mejor_costo:.4f}")
        print(f"  Fitness final (retención): {mejor_fitness:.4f} segundos")
        print(f"  Iteraciones totales:      {paso_global}")
        print(f"  Evaluaciones de costo:    {evaluaciones}")
        print(f"  Peores movs. aceptados:   {peores_aceptadas} (vitales para escapar)")
        print()
        print("  Composición del slate óptimo global:")
        for i, ad in enumerate(mejor_slate.anuncios):
            print(
                f"    Slot {i + 1}: [ID:{ad.id:>3d}] {ad.titulo:<30s}  "
                f"Cat: {ad.categoria:<14s}  Dur: {ad.duracion:.1f}s"
            )
        print("=" * 70)

    return SAResult(
        mejor_slate=mejor_slate,
        costo_final=mejor_costo,
        fitness_final=mejor_fitness,
        iteraciones_totales=paso_global,
        evaluaciones_costo=evaluaciones,
        peores_aceptadas=peores_aceptadas,
        historial_costos=historial_costos,
        historial_fitness=historial_fitness,
    )