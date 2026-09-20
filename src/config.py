"""
Configuración global y parámetros (hiperparámetros) del proyecto.
"""

NUM_ADS_CATALOG = 100
NUM_CATEGORIES = 6
CATEGORIES = ['Gaming', 'Moda', 'Finanzas', 'Gastronomía', 'Tecnología', 'Fitness']
K_SLOTS = 8
AD_DURATION_MIN = 10
AD_DURATION_MAX = 60
FATIGUE_LAMBDA = 0.7

SA_TEMP_INITIAL = 100.0
SA_ALPHA = 0.95
SA_TEMP_MIN = 0.001
SA_ITERATIONS_PER_TEMP = 50

HC_MAX_STAGNANT_ITERS = 200
HC_MAX_ITERS = 2000
SA_MAX_ITERS = 5000

RANDOM_SEED = 42

NEIGHBOR_OPERATORS = ['swap', 'replace']
SA_NEIGHBOR_OPERATORS = ['swap', 'replace', 'invert']
