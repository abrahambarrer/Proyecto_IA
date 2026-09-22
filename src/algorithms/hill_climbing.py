"""
Módulo 2: Algoritmo de Búsqueda Local — Hill Climbing (Ascenso de Colina).

Implementa búsqueda local estricta: acepta un vecino ÚNICAMENTE si su costo
es estrictamente menor que el del estado actual (mejora estricta).
Se detiene al alcanzar un óptimo local (sin mejora tras N intentos consecutivos)
o al agotar el límite máximo de iteraciones.
"""
import numpy as np
from dataclasses import dataclass, field

from src.models.ad import Ad
from src.models.user import UserProfile
from src.models.slate import Slate
from src.core.cost_function import calcular_costo, calcular_fitness
from src.core.neighborhood import generar_vecino
from src import config


@dataclass
class HCResult:
    """Resultado completo de una ejecución de Hill Climbing."""
    mejor_slate: Slate
    costo_final: float
    fitness_final: float
    iteraciones_totales: int
    evaluaciones_costo: int
    historial_costos: list[float] = field(default_factory=list)
    historial_fitness: list[float] = field(default_factory=list)
    movimientos_aceptados: int = 0
    iteracion_estancamiento: int = 0
    log_movimientos: list[dict] = field(default_factory=list)


def run_hill_climbing(
    slate_inicial: Slate,
    catalogo: list[Ad],
    user: UserProfile,
    lambda_fatiga: float = config.FATIGUE_LAMBDA,
    max_iters: int = config.HC_MAX_ITERS,
    max_stagnant: int = config.HC_MAX_STAGNANT_ITERS,
    operadores: list[str] = None,
    seed: int = config.RANDOM_SEED,
    verbose: bool = True,
) -> HCResult:
    """
    Ejecuta el algoritmo Hill Climbing.

    Parámetros
    ----------
    slate_inicial : Slate
        Solución inicial S₀ (la misma que usará Simulated Annealing).
    catalogo : list[Ad]
        Catálogo completo de anuncios disponibles.
    user : UserProfile
        Perfil del usuario objetivo.
    lambda_fatiga : float
        Factor λ de penalización por fatiga (0 < λ < 1).
    max_iters : int
        Número máximo de iteraciones totales.
    max_stagnant : int
        Número máximo de iteraciones consecutivas sin mejora antes de declarar
        estancamiento en óptimo local.
    operadores : list[str]
        Operadores de vecindad a usar (por defecto: config.NEIGHBOR_OPERATORS).
    seed : int
        Semilla para reproducibilidad.
    verbose : bool
        Si True, imprime traza paso a paso en consola.

    Retorna
    -------
    HCResult
        Objeto con el mejor estado encontrado, costo final, historial y métricas.
    """
    if operadores is None:
        operadores = config.NEIGHBOR_OPERATORS

    rng = np.random.default_rng(seed)

    # Estado inicial
    estado_actual = slate_inicial.copy()
    costo_actual = calcular_costo(estado_actual, user, lambda_fatiga)
    fitness_actual = calcular_fitness(estado_actual, user, lambda_fatiga)
    evaluaciones = 1  # Primera evaluación del estado inicial

    # Mejor solución encontrada
    mejor_slate = estado_actual.copy()
    mejor_costo = costo_actual
    mejor_fitness = fitness_actual

    # Historial para gráficas de convergencia
    historial_costos = [costo_actual]
    historial_fitness = [fitness_actual]

    # Contadores
    movimientos_aceptados = 0
    iters_sin_mejora = 0
    iteracion_estancamiento = 0
    log_movimientos = []

    if verbose:
        print("=" * 70)
        print("       HILL CLIMBING — BÚSQUEDA LOCAL ESTRICTA")
        print("=" * 70)
        print(f"  Estado inicial:  {estado_actual}")
        print(f"  Costo inicial:   {costo_actual:.4f}")
        print(f"  Fitness inicial: {fitness_actual:.4f}s de visualización")
        print(f"  Max iteraciones: {max_iters}")
        print(f"  Max estancamiento: {max_stagnant} iteraciones sin mejora")
        print(f"  Operadores:      {operadores}")
        print(f"  Seed:            {seed}")
        print("-" * 70)

    # Bucle principal
    for iteracion in range(1, max_iters + 1):

        # Generar vecino
        vecino, operador_usado = generar_vecino(
            estado_actual, catalogo, operadores, rng
        )
        costo_vecino = calcular_costo(vecino, user, lambda_fatiga)
        fitness_vecino = calcular_fitness(vecino, user, lambda_fatiga)
        evaluaciones += 1

        delta_costo = costo_vecino - costo_actual

        # Condición estricta: aceptar SOLO si mejora
        if costo_vecino < costo_actual:
            # Movimiento aceptado
            reduccion_costo = costo_actual - costo_vecino
            ganancia_fitness = fitness_vecino - fitness_actual

            if verbose:
                print(
                    f"  [Paso {iteracion:>4d}] MEJORA ACEPTADA  |  "
                    f"Op: {operador_usado:<8s}  |  "
                    f"Costo: {costo_actual:.4f} → {costo_vecino:.4f}  "
                    f"(ΔC = {delta_costo:+.4f})  |  "
                    f"Fitness: {fitness_actual:.4f}s → {fitness_vecino:.4f}s  "
                    f"(+{ganancia_fitness:.4f}s)"
                )

            log_movimientos.append({
                'iteracion': iteracion,
                'operador': operador_usado,
                'costo_anterior': costo_actual,
                'costo_nuevo': costo_vecino,
                'delta_costo': delta_costo,
                'fitness_anterior': fitness_actual,
                'fitness_nuevo': fitness_vecino,
                'ganancia_fitness': ganancia_fitness,
            })

            # Actualizar estado actual
            estado_actual = vecino
            costo_actual = costo_vecino
            fitness_actual = fitness_vecino
            movimientos_aceptados += 1
            iters_sin_mejora = 0

            # Actualizar mejor solución global
            if costo_actual < mejor_costo:
                mejor_slate = estado_actual.copy()
                mejor_costo = costo_actual
                mejor_fitness = fitness_actual

        else:
            # Movimiento rechazado — no hay mejora
            iters_sin_mejora += 1

        # Registrar historial (siempre el costo del estado actual)
        historial_costos.append(costo_actual)
        historial_fitness.append(fitness_actual)

        # Criterio de parada: estancamiento
        if iters_sin_mejora >= max_stagnant:
            iteracion_estancamiento = iteracion
            if verbose:
                print()
                print("!" * 70)
                print(
                    "  ¡ALGORITMO ESTANCADO EN ÓPTIMO LOCAL! "
                    "Ningún vecino evaluado ofrece mejora directa."
                )
                print(
                    f"  Se evaluaron {max_stagnant} vecinos consecutivos "
                    f"sin encontrar mejora estricta."
                )
                print(f"  Iteración de estancamiento: {iteracion}")
                print("!" * 70)
            break
    else:
        # Se agotó el límite de iteraciones sin estancarse
        iteracion_estancamiento = max_iters
        if verbose:
            print()
            print("-" * 70)
            print(
                f"  Límite de {max_iters} iteraciones alcanzado "
                f"(sin estancamiento total detectado)."
            )

    # Resumen final
    if verbose:
        print()
        print("=" * 70)
        print("       RESULTADO FINAL — HILL CLIMBING")
        print("=" * 70)
        print(f"  Mejor slate encontrado:   {mejor_slate}")
        print(f"  Costo final:              {mejor_costo:.4f}")
        print(f"  Fitness final (retención): {mejor_fitness:.4f} segundos")
        print(f"  Iteraciones totales:      {iteracion_estancamiento}")
        print(f"  Evaluaciones de costo:    {evaluaciones}")
        print(f"  Movimientos aceptados:    {movimientos_aceptados}")
        print()
        print("  Composición del slate óptimo local:")
        for i, ad in enumerate(mejor_slate.anuncios):
            print(
                f"    Slot {i + 1}: [ID:{ad.id:>3d}] {ad.titulo:<30s}  "
                f"Cat: {ad.categoria:<14s}  Dur: {ad.duracion:.1f}s"
            )
        print("=" * 70)

    return HCResult(
        mejor_slate=mejor_slate,
        costo_final=mejor_costo,
        fitness_final=mejor_fitness,
        iteraciones_totales=iteracion_estancamiento,
        evaluaciones_costo=evaluaciones,
        historial_costos=historial_costos,
        historial_fitness=historial_fitness,
        movimientos_aceptados=movimientos_aceptados,
        iteracion_estancamiento=iteracion_estancamiento,
        log_movimientos=log_movimientos,
    )
