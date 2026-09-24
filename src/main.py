"""
Punto de Entrada Principal — Sistema Inteligente de Optimización de Anuncios Digitales.

Orquesta los 4 módulos del proyecto:
  Módulo 1: Carga de parámetros, catálogo, usuario e inicialización de S_0.
  Módulo 2: Ejecución de Búsqueda Local (Hill Climbing).
  Módulo 3: Ejecución de Búsqueda Estocástica (Simulated Annealing).
  Módulo 4: Comparación de Resultados, tabla métrica, análisis y gráficas.
"""

import os
import sys

# Asegurar que la raíz del proyecto esté en sys.path para ejecución directa (python src/main.py)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Configurar stdout en utf-8 si la plataforma lo soporta
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src import config
from src.algorithms.hill_climbing import run_hill_climbing
from src.algorithms.simulated_annealing import run_simulated_annealing
from src.core.cost_function import calcular_costo, calcular_fitness
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
    graficar_convergencia,
    mostrar_composicion_slates,
    mostrar_explicacion_diferencia,
    mostrar_tabla_comparativa,
)


def crear_sesion() -> dict:
    """Inicializa la estructura del estado de sesión."""
    return {
        "catalogo": None,
        "user": None,
        "slate_inicial": None,
        "costo_inicial": None,
        "fitness_inicial": None,
        "inicializado": False,
        "hc_result": None,
        "sa_result": None,
    }


def mostrar_encabezado_menu() -> None:
    """Muestra el menú principal con el formato exacto requerido."""
    print("\n" + "=" * 50)
    print("       SISTEMA INTELIGENTE DE OPTIMIZACIÓN")
    print("Caso de Estudio: Recomendación de Anuncios Digitales")
    print("=" * 50)
    print("1. Cargar parámetros e inicializar escenario")
    print("2. Ejecutar algoritmo: Hill Climbing")
    print("3. Ejecutar algoritmo: Simulated Annealing")
    print("4. Ver comparación de resultados")
    print("5. Salir")
    print("=" * 50)


def modulo_1_inicializar(session: dict) -> None:
    """
    Módulo 1: Carga parámetros, genera datos sintéticos si es necesario,
    crea la solución inicial S_0 compartida y presenta el problema.
    """
    print("\n" + "#" * 70)
    print("  MODULO 1: INICIALIZACION DEL ESCENARIO DE OPTIMIZACION")
    print("#" * 70)

    # 1. Contexto del mundo real
    print("""
[1] CONTEXTO DEL PROBLEMA:
    En plataformas modernas de redes sociales (TikTok, Instagram Reels, Shorts),
    el consumo de contenido es rapido y continuo. Insertar anuncios sin una
    estrategia adecuada provoca 'Ad Fatigue' (fatiga publicitaria) y abandono
    inmediato (churn) de la sesion.

[2] OBJETIVO DE OPTIMIZACION:
    Disenar una secuencia ordenada de K = 8 ranuras (slots) publicitarias a partir
    de un catalogo de 100 anuncios, maximizando el tiempo total de visualizacion retenido.

[3] MODELADO MATEMATICO DE LA FUNCION DE COSTO:
    * Para cada ranura i:
        T_i(S) = Duracion(a_i) * Afinidad(u, a_i) * gamma_fatiga(S, i) * delta_posicion(i)
    * Donde:
        - Afinidad(u, a_i) in [0, 1] es la similitud coseno entre intereses y tags.
        - delta_posicion(i) = 1 / sqrt(i + 1) representa el desgaste natural de la sesion.
        - gamma_fatiga(S, i) penaliza severamente repeticiones cercanas de igual categoria.
    * Funcion Objetivo: Maximizar Fitness F(S) = Sum(T_i(S)) (segundos de retencion).
    * Funcion de Costo: Minimizar Costo(S) = -F(S). (Menor costo = mayor atencion).
""")

    # 2. Comprobar / generar archivos de datos
    csv_path = os.path.join(PROJECT_ROOT, "data", "ads_catalog.csv")
    json_path = os.path.join(PROJECT_ROOT, "data", "user_profile.json")

    if not os.path.exists(csv_path) or not os.path.exists(json_path):
        print(f"[*] Generando catalogo sintetico y perfil de usuario con seed={config.RANDOM_SEED}...")
        catalogo_gen = generar_catalogo(
            num_anuncios=config.NUM_ADS_CATALOG,
            seed=config.RANDOM_SEED
        )
        user_gen = generar_perfil_usuario(seed=config.RANDOM_SEED)
        guardar_catalogo_csv(catalogo_gen, csv_path)
        guardar_perfil_json(user_gen, json_path)
        print("    Archivos 'data/ads_catalog.csv' y 'data/user_profile.json' creados con exito.")

    # 3. Cargar datos
    catalogo = cargar_catalogo(csv_path)
    user = cargar_perfil_usuario(json_path)

    # 4. Generar estado inicial S_0 idéntico para ambos algoritmos
    slate_inicial = generar_slate_inicial(
        catalogo=catalogo,
        k=config.K_SLOTS,
        seed=config.RANDOM_SEED
    )
    costo_ini = calcular_costo(slate_inicial, user, config.FATIGUE_LAMBDA)
    fitness_ini = calcular_fitness(slate_inicial, user, config.FATIGUE_LAMBDA)

    # 5. Guardar en sesión
    session["catalogo"] = catalogo
    session["user"] = user
    session["slate_inicial"] = slate_inicial
    session["costo_inicial"] = costo_ini
    session["fitness_inicial"] = fitness_ini
    session["inicializado"] = True
    session["hc_result"] = None
    session["sa_result"] = None

    # 6. Mostrar resumen
    print("-" * 70)
    print(f"  Usuario objetivo: {user.nombre} (ID: {user.id})")
    print(f"  Catalogo cargado: {len(catalogo)} anuncios disponibles de {len(config.CATEGORIES)} categorias.")
    print(f"  Slots de la sesion: K = {config.K_SLOTS}")
    print("  Solucion inicial S_0 generada con exito:")
    print(f"    * Costo inicial:   {costo_ini:.4f}")
    print(f"    * Fitness inicial: {fitness_ini:.2f} segundos ({fitness_ini / 60:.2f} min) de retencion estimada.")
    print("-" * 70)
    print("  Detalle de slots en S_0:")
    for i, ad in enumerate(slate_inicial.anuncios):
        print(f"    Slot {i + 1}: [ID:{ad.id:>2d}] {ad.categoria:<14} | {ad.titulo:<22} | Dur: {ad.duracion:4.1f}s")
    print("-" * 70)
    print("[OK] Escenario inicializado correctamente. S_0 queda listo para competir.")


def modulo_2_hill_climbing(session: dict) -> None:
    """
    Módulo 2: Ejecuta Hill Climbing desde la solución inicial S_0.
    """
    if not session["inicializado"]:
        print("\n[!] ALERTA: Primero debe inicializar el escenario (Opcion 1).")
        return

    print("\n" + "#" * 70)
    print("  MODULO 2: BUSQUEDA LOCAL -- HILL CLIMBING")
    print("#" * 70)

    # Usamos una copia fresca de S_0 para garantizar aislamiento
    s0_copia = session["slate_inicial"].copy()

    hc_result = run_hill_climbing(
        slate_inicial=s0_copia,
        catalogo=session["catalogo"],
        user=session["user"],
        lambda_fatiga=config.FATIGUE_LAMBDA,
        max_iters=config.HC_MAX_ITERS,
        max_stagnant=config.HC_MAX_STAGNANT_ITERS,
        operadores=config.NEIGHBOR_OPERATORS,
        seed=config.RANDOM_SEED,
        verbose=True,
    )

    session["hc_result"] = hc_result
    print("\n[OK] Ejecucion de Hill Climbing finalizada y registrada en sesion.")


def modulo_3_simulated_annealing(session: dict) -> None:
    """
    Módulo 3: Ejecuta Simulated Annealing desde la misma solución inicial S_0.
    """
    if not session["inicializado"]:
        print("\n[!] ALERTA: Primero debe inicializar el escenario (Opcion 1).")
        return

    print("\n" + "#" * 70)
    print("  MODULO 3: BUSQUEDA ESTOCASTICA -- SIMULATED ANNEALING")
    print("#" * 70)

    # Usamos exactamente la misma solución S_0
    s0_copia = session["slate_inicial"].copy()

    sa_result = run_simulated_annealing(
        slate_inicial=s0_copia,
        catalogo=session["catalogo"],
        user=session["user"],
        lambda_fatiga=config.FATIGUE_LAMBDA,
        t_inicial=config.SA_TEMP_INITIAL,
        alpha=config.SA_ALPHA,
        t_min=config.SA_TEMP_MIN,
        iters_por_temp=config.SA_ITERATIONS_PER_TEMP,
        operadores=config.SA_NEIGHBOR_OPERATORS,
        seed=config.RANDOM_SEED,
        verbose=True,
    )

    session["sa_result"] = sa_result
    print("\n[OK] Ejecucion de Simulated Annealing finalizada y registrada en sesion.")


def modulo_4_comparacion(session: dict) -> None:
    """
    Módulo 4: Comparación integral de resultados.
    Valida ejecución previa de HC y SA, genera tabla comparativa,
    análisis explicativo y gráfica de convergencia.
    """
    if not session["inicializado"]:
        print("\n[!] ALERTA: Debe inicializar los parametros y el escenario primero (Opcion 1).")
        return

    hc = session.get("hc_result")
    sa = session.get("sa_result")

    # Validación estricta conforme a Directrices
    if hc is None and sa is None:
        print("\n" + "!" * 70)
        print("  [!] ERROR: Ningun algoritmo se ha ejecutado aun en la sesion actual.")
        print("      Por favor, ejecute la Opcion 2 (Hill Climbing)")
        print("      y la Opcion 3 (Simulated Annealing) antes de comparar.")
        print("!" * 70)
        return

    if hc is None:
        print("\n" + "!" * 70)
        print("  [!] ERROR: Hill Climbing aun no ha sido ejecutado.")
        print("      Por favor, ejecute primero la Opcion 2.")
        print("!" * 70)
        return

    if sa is None:
        print("\n" + "!" * 70)
        print("  [!] ERROR: Simulated Annealing aun no ha sido ejecutado.")
        print("      Por favor, ejecute primero la Opcion 3.")
        print("!" * 70)
        return

    print("\n" + "#" * 70)
    print("  MODULO 4: COMPARACION DE RESULTADOS EXPERIMENTALES")
    print("#" * 70)

    # 1. Tabla comparativa de métricas
    mostrar_tabla_comparativa(
        hc_result=hc,
        sa_result=sa,
        costo_inicial=session["costo_inicial"],
        fitness_inicial=session["fitness_inicial"],
    )

    # 2. Comparativa de composición de la secuencia final
    mostrar_composicion_slates(hc, sa)

    # 3. Explicación analítica fundada en el modelado del terreno
    mostrar_explicacion_diferencia(hc, sa)

    # 4. Opción para generar el gráfico de convergencia
    print("-" * 80)
    try:
        opcion_grafica = input("Desea generar y guardar el grafico de convergencia (PNG)? [S/n]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        opcion_grafica = "s"

    if opcion_grafica in ("", "s", "si", "y", "yes"):
        filepath = os.path.join(PROJECT_ROOT, "convergencia_hc_vs_sa.png")
        graficar_convergencia(
            hc_historial=hc.historial_costos,
            sa_historial=sa.historial_costos,
            tipo="ambos",
            guardar=True,
            filepath=filepath,
            iter_estancamiento_hc=hc.iteracion_estancamiento,
        )


def main() -> None:
    """Bucle principal de la aplicación de consola."""
    session = crear_sesion()

    while True:
        mostrar_encabezado_menu()
        try:
            opcion = input("Seleccione una opcion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nSaliendo del sistema...")
            break

        if opcion == "1":
            modulo_1_inicializar(session)
        elif opcion == "2":
            modulo_2_hill_climbing(session)
        elif opcion == "3":
            modulo_3_simulated_annealing(session)
        elif opcion == "4":
            modulo_4_comparacion(session)
        elif opcion == "5":
            print("\nGracias por utilizar el Sistema Inteligente de Optimizacion. Hasta pronto.\n")
            sys.exit(0)
        else:
            print("\n[!] Opcion invalida. Por favor seleccione un numero del 1 al 5.")


if __name__ == "__main__":
    main()
