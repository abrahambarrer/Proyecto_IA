# 📋 PLAN MAESTRO DE PROYECTO DE INTELIGENCIA ARTIFICIAL (ENTREGA 1)

## 📌 Proyecto: Sistema de Asignación y Recomendación Óptima de Anuncios Digitales en Social Media
**Algoritmos de Búsqueda:** Búsqueda Local (*Hill Climbing*) vs. Búsqueda Estocástica (*Simulated Annealing*)  
**Directrices de Referencia:** `Directrices.pdf`  
**Lenguaje de Desarrollo:** Python 3.10+  

---

## 1. 🎯 Definición del Problema del Mundo Real

### 1.1 Contexto
En las plataformas modernas de redes sociales (Instagram Reels, TikTok, YouTube Shorts, Meta Feed), los usuarios consumen flujos continuos de contenido orgánico intercalado con **anuncios publicitarios patrocinados (Digital Ads)**. 

El modelo de monetización depende de la efectividad del anuncio, pero existe un dilema fundamental:
* Mostrar demasiados anuncios o anuncios irrelevantes genera **fatiga publicitaria (*Ad Fatigue*)** y abandono de la plataforma (*churn*).
* Colocar anuncios en secuencias o momentos no óptimos reduce el **tiempo de visualización (*Watch Time / Dwell Time*)** del usuario.
* Ciertos anuncios tienen sinergia positiva cuando se muestran después de ciertos tópicos, mientras que anuncios repetidos de la misma categoría provocan ceguera publicitaria inmediata (*Banner/Ad Blindness*).

### 1.2 Problema Específico a Resolver
> **Optimizar la secuencia y selección de una parrilla (*slate*) de $K$ anuncios digitales dentro de una sesión de usuario para maximizar el tiempo total de visualización retenido**, respetando restricciones de diversidad temática, duración de los anuncios y afinidad del perfil de usuario.

---

## 2. 🗺️ Modelado Matemático: Terreno y Función de Costo

### 2.1 Representación del Estado (Solución Candidata)
Sea un catálogo publicitario de $M$ anuncios disponibles: $\mathcal{A} = \{a_1, a_2, \dots, a_M\}$.  
Una solución o estado $S$ se representa como una secuencia ordenada de $K$ anuncios asignados a $K$ ranuras (*slots*) de visualización:

$$S = [a_{s_1}, a_{s_2}, \dots, a_{s_K}] \quad \text{donde } a_{s_i} \in \mathcal{A}$$

### 2.2 Modelado del Terreno: ¿Por qué es un Terreno No Convexo con Valles y Cimas Locales?
El comportamiento humano frente a anuncios en redes sociales no es lineal ni aditivo:
1. **Afinidad Usuario-Anuncio:** Cada anuncio tiene una compatibilidad base con el vector de intereses del usuario.
2. **Penalización por Fatiga y Repetición (Ad Fatigue):** La función de aptitud **penaliza severamente** la repetición de categorías de forma cercana a través del factor $\gamma_{\text{fatiga}}$.
3. **Efecto de Duración y Desgaste Temporal:** Anuncios muy largos colocados al inicio causan abandono temprano.

> **Consecuencia (El Óptimo Local y el Estancamiento):** 
> * Dado que la función de aptitud penaliza la fatiga, Hill Climbing rápidamente encuentra una mezcla razonable que alterna categorías de forma aceptable (un óptimo local).
> * Sin embargo, **no puede alcanzar el óptimo global** porque para mejorar sustancialmente se requeriría cambiar 2 o 3 anuncios de forma simultánea. Cualquier intercambio (swap) individual desordena el equilibrio actual y empeora la función de aptitud. 
> * **Ejemplo de Estancamiento:** Hill Climbing puede llegar a una secuencia como `[Gaming, Tech, Gaming, Food, Gaming, Tech, Fashion, Fitness]` (buena diversidad, pero el patrón inicial causa fatiga moderada). El óptimo global podría ser `[Gaming, Food, Tech, Fashion, Gaming, Fitness, Tech, Food]` (alternancia perfecta), pero llegar ahí requiere varios intercambios. Cualquier intercambio simple desde el óptimo local parece ser peor a corto plazo.
> * **Efecto Meseta (Plateau):** Al intercambiar dos anuncios de duraciones similares y afinidades comparables en ranuras adyacentes, el cambio en la aptitud es marginal ($\Delta F \approx 0$), dejando al Hill Climbing sin una pendiente clara para ascender.

**Aquí es donde Hill Climbing queda inevitablemente atrapado en un óptimo local (al no aceptar cambios que temporalmente empeoren la aptitud) y Simulated Annealing logra escapar (aceptando soluciones subóptimas temporalmente con cierta probabilidad).**

### 2.3 Formulación de la Función de Aptitud (Fitness) y Función de Costo

#### A. Tiempo de Visualización Esperado para el slot $i$:
Para un anuncio $a_{s_i}$ colocado en el slot $i$, su tiempo de visualización estimado $T_i$ se modela como:

$$T_i(S) = D(a_{s_i}) \cdot \text{Afinidad}(u, a_{s_i}) \cdot \gamma_{\text{fatiga}}(S, i) \cdot \delta_{\text{posición}}(i)$$

Donde:
* $D(a)$ es la duración en segundos del anuncio.
* $\text{Afinidad}(u, a) \in [0, 1]$ es el producto punto o similitud coseno entre el perfil del usuario $u$ y los tags del anuncio $a$.
* $\delta_{\text{posición}}(i) = \frac{1}{\sqrt{i}}$ es el factor de desgaste natural de la sesión.
* $\gamma_{\text{fatiga}}(S, i)$ es el factor de penalización por saturación de categoría:

$$\gamma_{\text{fatiga}}(S, i) = \prod_{j < i, \text{cat}(a_{s_j}) = \text{cat}(a_{s_i})} \lambda^{(i - j)^{-1}} \quad (\lambda \in (0, 1))$$

#### B. Función Objetivo Total (Tiempo Total de Visualización):
$$F(S) = \sum_{i=1}^{K} T_i(S) \quad \text{[Segundos de atención retenida - a MAXIMIZAR]}$$

#### C. Definición de la Función de Costo (para MINIMIZACIÓN estándar en Algoritmos de Búsqueda):
Dado que los algoritmos clásicos de búsqueda de minimización evalúan "costo" a reducir, definimos el costo como el **déficit de atención** respecto al máximo teórico posible ($T_{\max}$):

$$\text{Costo}(S) = T_{\max} - F(S) \quad \text{o alternativamente } \text{Costo}(S) = -F(S)$$

* Menor Costo $\implies$ Mayor Tiempo de Visualización retenido.
* En el reporte de consola se presentarán tanto el costo como los segundos de visualización equivalentes.

---

## 3. 🔄 Espacio de Búsqueda y Generación de Vecinos

Para pasar de un estado actual $S$ a un estado vecino $S'$, se implementan tres operadores estocásticos:
1. **Swap (Intercambio de Slots):** Intercambiar la posición de dos anuncios en la secuencia actual:
   $$[a_1, \mathbf{a_2}, a_3, \mathbf{a_4}, a_5] \longrightarrow [a_1, \mathbf{a_4}, a_3, \mathbf{a_2}, a_5]$$
2. **Replace (Sustitución desde Catálogo):** Reemplazar un anuncio en la posición $i$ por otro anuncio aleatorio del catálogo $\mathcal{A}$ que no esté en la secuencia actual:
   $$[a_1, \mathbf{a_2}, a_3] \longrightarrow [a_1, \mathbf{a_{new}}, a_3]$$
3. **Scramble / Inversion (Inversión de Subsecuencia):** Invertir el orden de una subsecuencia de slots contiguos para romper patrones de fatiga estancados.

---

## 4. 📊 Fuentes de Datos (Datasets)

Para alimentar el Módulo 1 se contemplan dos fuentes integradas y reproducibles:

### 4.1 Datasets Reales Recomendados
1. **KuaiRand / KuaiRec (Kaggle / GitHub):**
   * *Descripción:* Dataset de microvideos y recomendaciones secuenciales en social media de Kuaishou (competidor de TikTok). Contiene logs reales de usuarios, con categorías de video y **tiempo exacto de visualización en segundos (`play_duration`)** y tiempo total del video (`duration`).
   * *URL:* [KuaiRand Official](https://kuairand.com/) / Kaggle Search: `KuaiRand-1K`.
2. **Social Network Ads / Ad Click Prediction (Kaggle):**
   * *Descripción:* Datasets clásicos de targeting de anuncios en redes sociales con datos demográficos, intereses y métricas de engagement.
3. **Simulated Social Media User Interaction dataset**
    * *URL:* [Dataset](https://www.kaggle.com/datasets/aaidoudi/user-social-network-interaction-temporal).

### 4.2 Generador de Datos Sintéticos Calibrados (`data_generator.py`)
Para garantizar que el proyecto se ejecute de manera inmediata sin requerir descargas pesadas de gigabytes:
* Se incluye un generador con semillas aleatorias fijas (`seed=42`) que crea:
  * **Catálogo de 100 anuncios:** ID, Título, Categoría (Gaming, Moda, Finanzas, Gastronomía, Tecnología, Fitness), Duración (5s a 60s), Tasa base de retención.
  * **Perfil del Usuario Objetivo:** Vector de intereses en cada categoría $\in [0, 1]$, nivel de tolerancia a la fatiga publicitaria, tiempo disponible de sesión.

---

## 5. 🛠️ Stack Tecnológico y Librerías de Python

| Categoría | Librería | Propósito |
| :--- | :--- | :--- |
| **Computación Numérica** | `numpy` | Operaciones matriciales rápidas, muestreo aleatorio y cálculo de costos. |
| **Manipulación de Datos** | `pandas` | Carga y manejo tabular del catálogo de anuncios y perfiles. |
| **Visualización en Consola** | `rich` o `tabulate` | Impresión de tablas con formato profesional en terminal y menús visuales. |
| **Visualización Gráfica** | `matplotlib` | Gráficas comparativas de convergencia (Curvas de Costo vs. Iteraciones). |
| **Generación de Reportes** | `json` / `csv` (std) | Persistencia de métricas intermedias de los algoritmos. |

```txt
# requirements.txt
numpy>=1.24.0
pandas>=2.0.0
tabulate>=0.9.0
rich>=13.0.0
matplotlib>=3.7.0
```

---

## 6. 🏗️ Arquitectura de Software y Estructura del Proyecto

La estructura sigue principios de arquitectura limpia, modular y desacoplada:

```
Proyecto_IA/
│
├── Directrices.pdf               # Documento original de requisitos
├── PLAN_PROYECTO.md              # Este plan detallado de trabajo
├── requirements.txt              # Dependencias de Python
├── README.md                     # Documentación general y guía de ejecución
│
├── data/
│   ├── ads_catalog.csv           # Catálogo de anuncios (generado o real)
│   └── user_profile.json         # Perfil y preferencias del usuario de prueba
│
├── src/
│   ├── __init__.py
│   ├── config.py                 # Hiperparámetros (T_inicial, alpha, slots_K, iteraciones)
│   │
│   ├── models/                   # Definición de Entidades
│   │   ├── __init__.py
│   │   ├── ad.py                 # Clase Ad (ID, categoría, duración, click_weight)
│   │   ├── user.py               # Clase UserProfile (intereses, tolerancia a fatiga)
│   │   └── slate.py              # Clase State (secuencia de anuncios en los slots)
│   │
│   ├── core/                     # Lógica Matemática de Optimización
│   │   ├── __init__.py
│   │   ├── cost_function.py      # Cálculo de retención, fatiga y costo
│   │   └── neighborhood.py       # Operadores de vecindad (swap, replace, invert)
│   │
│   ├── algorithms/               # Algoritmos Requeridos
│   │   ├── __init__.py
│   │   ├── hill_climbing.py      # Módulo 2: Búsqueda Local Estricta
│   │   └── simulated_annealing.py# Módulo 3: Búsqueda Estocástica con Boltzmann
│   │
│   ├── utils/                    # Utilerías de Carga y Visualización
│   │   ├── __init__.py
│   │   ├── data_loader.py        # Módulo 1: Carga y validación de datos
│   │   └── visualizer.py         # Gráficas de convergencia y visualización
│   │
│   └── main.py                   # Menú Interactivo en Consola (Módulos 1 al 4)
│
└── tests/                        # Pruebas Unitarias
    ├── test_cost.py              # Verificación de monotonía y fatiga
    └── test_algorithms.py        # Verificación de reglas de transición
```

---

## 7. ⚙️ Desglose Detallado por Módulos (Conforme a `Directrices.pdf`)

```
============================================
SISTEMA INTELIGENTE DE OPTIMIZACIÓN
Caso de Estudio: Recomendación de Anuncios Digitales
============================================
1. Cargar parámetros e inicializar escenario
2. Ejecutar algoritmo: Hill Climbing
3. Ejecutar algoritmo: Simulated Annealing
4. Ver comparación de resultados
5. Salir
============================================
Seleccione una opción:
```

### 🔹 Módulo 1: Inicialización y Datos del Escenario
* **Acción:**
  1. Carga del archivo `ads_catalog.csv` (100 anuncios de 6 categorías distintas con duraciones de 10 a 60s).
  2. Carga del perfil de usuario (`user_profile.json`), definiendo sus gustos predominantes (ej. 80% Tecnología, 60% Gaming, 10% Cosméticos).
  3. Fijación del número de slots en la sesión: $K = 8$ espacios publicitarios.
  4. Generación y fijación de la **Solución Inicial ($S_0$)** generada de forma aleatoria o voraz simple. Esta misma $S_0$ se guardará en memoria para que **ambos algoritmos compitan en igualdad de condiciones**.
* **Salida en Consola requerida:**
  * Breve descripción del escenario del mundo real simulado.
  * Explicación matemática de qué representa la función de costo (déficit de tiempo de visualización y fatiga).
  * Resumen del estado inicial: anuncios elegidos, categorías, costo inicial y tiempo de retención proyectado.

---

### 🔹 Módulo 2: Búsqueda Local (*Hill Climbing*)
* **Reglas de Implementación:**
  * Parte de la solución inicial fija $S_0$.
  * En cada iteración genera un vecino $S'$ mediante un operador de vecindad (swap / replace).
  * **Condición Estricta:** Acepta $S'$ **únicamente si** $\text{Costo}(S') < \text{Costo}(S_{\text{actual}})$ (mejora estricta). Si es igual o peor, se rechaza.
  * Criterio de parada: Cuando tras $N_{\text{max\_intentos}}$ evaluaciones de vecinos no se encuentra ninguna mejora (óptimo local alcanzado) o límite de iteraciones.
* **Salida en Consola requerida:**
  * Traza paso a paso de cada movimiento aceptado: número de paso, operador aplicado, reducción de costo, ganancia en segundos de atención.
  * **Punto exacto de estancamiento:** Notificación explícita en consola indicando:  
    `"¡ALGORITMO ESTANCADO EN ÓPTIMO LOCAL! Ningún vecino evaluado ofrece mejora directa."`
  * Mostrar el costo final y configuración del slate en el que quedó atrapado.
  * Almacenar en una variable de sesión: `hc_costo_final`, `hc_iteraciones`, `hc_historial_costos`.

---

### 🔹 Módulo 3: Búsqueda Estocástica (*Simulated Annealing*)
* **Reglas de Implementación:**
  * Parte **exactamente de la misma solución inicial $S_0$**.
  * Parámetros térmicos:
    * Temperatura Inicial: $T_0 = 100.0$ (o calibrada a la escala de $\Delta F$).
    * Tasa de Enfriamiento geométrica: $T_{k+1} = \alpha \cdot T_k$ con $\alpha \in [0.90, 0.98]$.
    * Temperatura Mínima de Parada: $T_{\min} = 0.001$.
  * **Probabilidad de Aceptación de Boltzmann Obligatoria:**
    * Sea $\Delta C = \text{Costo}(S') - \text{Costo}(S_{\text{actual}})$.
    * Si $\Delta C < 0$ (es mejor): se acepta incondicionalmente.
    * Si $\Delta C \ge 0$ (es peor solución): se acepta si y solo si:
      $$r < \exp\left(-\frac{\Delta C}{T}\right) \quad \text{donde } r \sim \mathcal{U}(0, 1)$$
      *(O en términos de fitness $\Delta F = F' - F < 0 \implies \exp(\Delta F / T)$ conforme a la fórmula de las directrices).*
* **Salida en Consola requerida:**
  * Trazabilidad en tiempo real indicando cuándo se aceptó una peor solución gracias a la temperatura alta:  
    `"[Paso 42 | T=65.4] Peor solución aceptada (ΔC=+12.3, Prob=0.828, Rand=0.312) -> ESCAPANDO DE BACHE LOCAL"`.
  * Mostrar cómo la temperatura decae gradualmente hasta converger a la solución cuasi-óptima global.
  * Almacenar en variable de sesión: `sa_costo_final`, `sa_iteraciones`, `sa_historial_costos`.

---

### 🔹 Módulo 4: Comparación de Resultados
* **Acción:**
  * Lee los datos guardados en las variables de sesión de los Módulos 2 y 3.
  * Si alguno no se ha ejecutado, alerta al usuario para que lo ejecute primero.
* **Salida en Consola requerida:**
  * Tabla comparativa detallada con:
    1. Costo final obtenido por Hill Climbing (resaltando el estancamiento).
    2. Costo final obtenido por Simulated Annealing (resaltando la optimización lograda).
    3. Tiempo total de visualización equivalente retenido (en segundos y minutos).
    4. Porcentaje de mejora de Simulated Annealing sobre Hill Climbing:
       $$\% \text{ Mejora} = \frac{\text{Costo}_{\text{HC}} - \text{Costo}_{\text{SA}}}{\text{Costo}_{\text{HC}}} \times 100\%$$
    5. Total de iteraciones y evaluaciones de la función de costo efectuadas por cada método.
  * Explicación de por qué ocurrió la diferencia basada en el paisaje de fatiga y combinatoria de anuncios.
  * Opción de generar y guardar el gráfico de convergencia `convergencia_hc_vs_sa.png`.

---

## 8. 📅 Cronograma y Fases de Desarrollo (Equipos de 5 Miembros)

```text
Fase 1: Preparación y Arquitectura Base (Días 1-2)
  ├── Integrante 1: Generación de datos sintéticos (data_generator.py), creación de mockups.
  ├── Integrante 2: Definición de las clases base (models/) y esqueleto matemático.
  ├── Integrante 5: Setup del repositorio, main.py vacío y estructura del menú.
  └── [Hito 1] Reunión de Integración: Definir contratos de datos exactos entre Módulos.

Fase 2: Modelado Matemático y Entorno (Días 3-4)
  ├── Integrante 2: Implementación completa y pruebas de cost_function.py.
  ├── Integrantes 3 y 4: Pair programming en core/neighborhood.py (operadores de vecindad).
  ├── Integrante 1: Funciones de carga de datos (utils/data_loader.py).
  └── [Hito 2] Módulo 1 completado. Función de Costo validada.

Fase 3: Implementación Algorítmica Paralela (Días 5-6)
  ├── Integrante 3: Módulo 2 (Hill Climbing) con logs de estancamiento explícitos.
  ├── Integrante 4: Módulo 3 (Simulated Annealing) con probabilidad Boltzmann y trazabilidad térmica.
  └── Integrante 5: Integración algorítmica en main.py y captura de métricas.

Fase 4: Comparación, Visualización y Ajustes (Días 7-8)
  ├── Integrante 5: Visualizador y gráficos (utils/visualizer.py), Módulo 4 terminado.
  ├── Todos: Calibración final de hiperparámetros (T0, alpha, iteraciones).
  └── [Hito 3] Pruebas completas del sistema (end-to-end).

Fase 5: Documentación y Entrega (Día 9)
  ├── Integrante 5: Pulido del README.md.
  └── Todos: Verificación estricta contra Directrices.pdf.
```

---

## 9. ✅ Criterios de Éxito y Validación (Checklist de Directrices)

- [ ] **Módulo 1:** Datos programados a medida con impresión del contexto del mundo real y significado de la función de costo.
- [ ] **Módulo 2:** Condición estricta de Hill Climbing (solo mejoras directas) e impresión explícita del punto exacto donde se atora en el óptimo local.
- [ ] **Módulo 3:** Simulated Annealing con fórmula de Boltzmann `exp(deltaF / T)` y muestra en consola de cómo sale de los baches.
- [ ] **Módulo 4:** Tabla comparativa clara con costos finales, iteraciones y porcentaje de mejora.
- [ ] **Interfaz:** Menú en consola idéntico al diagrama provisto en las directrices.

---

## 10. 👥 Organización del Equipo (5 Miembros)

### 10.1 Asignación de Roles y Responsabilidades
* **Integrante 1 - Arquitecto de Datos:**
  * Archivos: `data_generator.py`, `utils/data_loader.py`, `data/ads_catalog.csv`, `data/user_profile.json`.
  * Responsabilidad: Garantizar la integridad y correcta generación de los escenarios de prueba.
* **Integrante 2 - Ingeniero de Modelado Matemático:**
  * Archivos: `models/ad.py`, `models/user.py`, `models/slate.py`, `core/cost_function.py`.
  * Responsabilidad: Programar de manera exacta las matemáticas de afinidad, fatiga y cálculo del déficit de atención.
* **Integrante 3 - Desarrollador de Algoritmo HC:**
  * Archivos: `algorithms/hill_climbing.py`, comparte `core/neighborhood.py` con el Integrante 4.
  * Responsabilidad: Implementar búsqueda local rigurosa y asegurar la detección correcta de estancamiento.
* **Integrante 4 - Desarrollador de Algoritmo SA:**
  * Archivos: `algorithms/simulated_annealing.py`, comparte `core/neighborhood.py` con el Integrante 3.
  * Responsabilidad: Implementar el esquema de enfriamiento térmico y el criterio de aceptación de Boltzmann.
* **Integrante 5 - Integrador y Presentador:**
  * Archivos: `main.py`, `utils/visualizer.py`, `README.md`, `tests/`.
  * Responsabilidad: Controlar el repositorio, ensamblar el menú de usuario interactivo, manejar variables de sesión y generar los reportes comparativos.

### 10.2 Contratos de Interfaz (Inputs/Outputs)
1. **Datos -> Modelos:** El `data_loader` retorna objetos tipados (listas de `Ad` y un `UserProfile`) que serán inyectados en la sesión.
2. **Estado -> Costo:** `cost_function(state: Slate)` recibe la secuencia propuesta y retorna el valor flotante del costo $C(S)$.
3. **Vecindad:** `get_neighbors(state: Slate)` retorna un nuevo `Slate` modificado para que el algoritmo lo evalúe.
4. **Algoritmos -> Main:** Ambos algoritmos (`run_hc()`, `run_sa()`) deben retornar un diccionario o tupla estándar: `(mejor_estado, costo_final, historial_costos, iteraciones)`.

### 10.3 Grafo de Dependencias
```text
(Data) ---> (Models) <--- (Cost Function & Neighborhood)
                 \                      /
                  +--> (Algorithms) <---+
                             |
                       (Main / UI) ---> (Visualizer)
```

### 10.4 Puntos de Control (Checkpoints)
* **Reunión 1 (Inicio):** Acordar estructuras de datos exactas en `models/`.
* **Reunión 2 (Mitad):** Verificar que `cost_function` coincida en cálculos a mano para ambos algoritmos.
* **Reunión 3 (Pre-entrega):** Validar que la interfaz cumpla estéticamente con el esquema exigido y que Simulated Annealing supere sistemáticamente a Hill Climbing.

---

## 11. 🔍 Ejemplo Ilustrativo del Estancamiento

Para comprender la naturaleza del óptimo local, consideremos un caso numérico simplificado.

**Perfil del Usuario:** Altísima afinidad por *Tecnología* (0.9) y moderada por *Gaming* (0.7). Alta penalización por fatiga $\lambda = 0.5$.

**Parrilla Actual ($S_{\text{actual}}$):**
1. Tech (15s, Afinidad 0.9) $\rightarrow$ T_vis = 15 * 0.9 * 1.0 (no fatiga) = **13.5s**
2. Gaming (15s, Afinidad 0.7) $\rightarrow$ T_vis = 15 * 0.7 * 1.0 = **10.5s**
3. Tech (15s, Afinidad 0.9) $\rightarrow$ T_vis = 15 * 0.9 * 0.5 (fatiga distancia 2) = **6.75s**
4. Tech (15s, Afinidad 0.9) $\rightarrow$ T_vis = 15 * 0.9 * 0.25 (fatiga severa distancia 1) = **3.37s**

*(Se ignora el desgaste temporal para el ejemplo).*
**Aptitud Total (Fitness) $S_{\text{actual}}$ = 34.12s**

A partir de este estado $S_{\text{actual}}$, el algoritmo *Hill Climbing* analiza sus vecinos. 
Un operador común es intercambiar dos anuncios adyacentes (Swap). Si evaluamos intercambiar el Slot 2 (Gaming) con el Slot 3 (Tech):

**Vecino 1 (Intercambio Slot 2 y 3):**
1. Tech (15s) $\rightarrow$ T_vis = **13.5s**
2. Tech (15s) $\rightarrow$ Fatiga severa por estar junto al Tech 1. T_vis = 15 * 0.9 * 0.5 = **6.75s**
3. Gaming (15s) $\rightarrow$ T_vis = **10.5s**
4. Tech (15s) $\rightarrow$ Fatiga desde los Slots 1 y 2. T_vis = 15 * 0.9 * 0.25 (o similar) $\approx$ **3.37s**

**Aptitud Total Vecino 1 $\approx$ 34.12s (Sin mejora, o ligeramente peor por la matemática exacta de la distancia)**

Si evaluamos insertar un anuncio de *Moda* (Afinidad 0.2) en el Slot 4 para romper la fatiga del Tech:
**Vecino 2 (Reemplazo Slot 4 por Moda):**
1. Tech (15s) $\rightarrow$ **13.5s**
2. Gaming (15s) $\rightarrow$ **10.5s**
3. Tech (15s) $\rightarrow$ **6.75s**
4. Moda (15s, Afinidad 0.2) $\rightarrow$ T_vis = 15 * 0.2 * 1.0 = **3.0s**

**Aptitud Total Vecino 2 = 33.75s (¡Peor aptitud!)**

**El Estancamiento:**
Como el *Vecino 1* tiene aptitud idéntica o inferior, y el *Vecino 2* tiene peor aptitud (33.75s < 34.12s), **Hill Climbing rechaza ambos**. El algoritmo ha llegado a un valle o meseta y concluye la ejecución.

**La Solución Estocástica (Simulated Annealing):**
Simulated Annealing, en cambio, evalúa el *Vecino 2* (que reduce la aptitud a 33.75s, un $\Delta C > 0$). Debido a su **alta temperatura inicial**, evalúa la probabilidad de Boltzmann $P \approx \exp(- \Delta C / T) \approx 0.85$. Como el número aleatorio tirado es menor que $0.85$, **ACEPTA** el movimiento al *Vecino 2* a pesar de ser temporalmente peor.

Gracias a aceptar ese anuncio de *Moda*, en las iteraciones siguientes el algoritmo ahora tiene un "espacio" para reacomodar otros anuncios de *Tech* y *Gaming* sin que colisionen. Esto le permite llegar a la configuración óptima global: `[Tech, Gaming, Moda, Tech]`, cuya aptitud total supera los **36.0s**. Al escapar del óptimo local aceptando una pérdida inicial, SA maximiza el objetivo final.
