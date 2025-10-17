# Guía Arquitectónica: Software de Optimización Geométrica de Antenas (SOGA)

## Sección 1: Visión Arquitectónica y Principios de Diseño

### 1.1. Resumen Ejecutivo

Este documento establece la guía arquitectónica para el proyecto "Software de Optimización Geométrica de Antenas" (SOGA). El objetivo es proporcionar una herramienta de ingeniería de nivel profesional, caracterizada por su robustez, escalabilidad y mantenibilidad, para el diseño avanzado de antenas para el sector de la agricultura de precisión y vehículos aéreos no tripulados (UAVs).

El desafío arquitectónico fundamental reside en gestionar la alta complejidad inherente a la simulación electromagnética y la optimización multiobjetivo. El software debe abstraer la física subyacente y los algoritmos heurísticos, traduciendo parámetros operativos de alto nivel (ej. "alcance deseado") en soluciones geométricas óptimas y conformes con la regulación. Esta guía define una arquitectura modular que garantiza un proceso de construcción sistemático, predecible y de alta calidad.

### 1.2. Patrón Arquitectónico Principal: Arquitectura en Capas (Layered Architecture)

La base de la arquitectura del software SOGA es un estricto patrón de **Arquitectura en Capas**. Esta decisión es fundamental para lograr los principios de bajo acoplamiento y alta cohesión, esenciales para un software de nivel empresarial. La estructura separa las responsabilidades del sistema en tres capas lógicas distintas, cada una con un propósito bien definido y una interfaz clara.

1. **Capa de Aplicación (Facade):** Actúa como un intermediario y orquestador. Proporciona una API simplificada que las interfaces de usuario pueden consumir. Su responsabilidad es recibir solicitudes, invocar a la capa de dominio para satisfacerlas y formatear los resultados para su presentación.

2. **Capa de Dominio (Core Engine):** Es el corazón de la aplicación. Contiene toda la lógica de negocio, los modelos físicos, las ecuaciones matemáticas y los algoritmos de optimización. Esta capa es completamente agnóstica a la interfaz de usuario y a cualquier sistema externo, lo que la hace intrínsecamente reutilizable y testable de forma aislada.

3. **Capa de Infraestructura (I/O & Persistence):** Gestiona todas las preocupaciones externas y transversales, como el acceso al sistema de archivos (guardar/cargar proyectos, exportar resultados), la gestión de la configuración y las interacciones con librerías de bajo nivel.

Se impone una regla de dependencia estricta: una capa solo puede comunicarse con la capa inmediatamente inferior. La Capa de Aplicación solo puede llamar a la Capa de Dominio. Tanto la Capa de Aplicación como la de Dominio pueden utilizar servicios de la Capa de Infraestructura. Esta restricción previene dependencias no deseadas y es un paso crítico para mantener una aplicación mantenible a largo plazo.

### 1.3. Aplicación de Filosofías de Diseño

La arquitectura se fundamenta en principios de ingeniería de software probados para garantizar la calidad y la longevidad del producto.

- **Filosofía UNIX / Principio de Responsabilidad Única (SRP):** Cada componente del sistema, desde los módulos de alto nivel hasta las clases y funciones individuales, se diseña para "hacer una sola cosa y hacerla bien". El módulo de cálculo electromagnético se centra exclusivamente en la física. Esta especialización reduce la complejidad y facilita las pruebas y el mantenimiento.

- **KISS (Keep It Simple, Stupid):** La complejidad es gestionada activamente en lugar de permitirse que emerja de forma orgánica. La Capa de Aplicación (Facade) es la encarnación principal de este principio. La fachada expone una API simplificada que oculta la complejidad del motor de dominio. En lugar de construir complejos objetos de configuración, simplemente se pasan diccionarios con valores simples, delegando la complejidad de la traducción a la fachada.

- **Bajo Acoplamiento, Alta Cohesión:** Este es el resultado directo de la aplicación de la Arquitectura en Capas y el SRP. Los módulos son diseñados para ser lo más independientes posible (bajo acoplamiento), comunicándose a través de interfaces estables y bien definidas (APIs) en lugar de compartir estados internos. Al mismo tiempo, los elementos dentro de cada módulo están fuertemente relacionados en su propósito (alta cohesión).

La Capa de Aplicación funciona como una **capa de traducción inteligente**. El proceso es el siguiente: los parámetros de entrada especifican restricciones prácticas y de alto nivel, como "alcance operativo deseado de 5 km" o "carga útil máxima del dron de 500 g". El motor de dominio, por otro lado, requiere parámetros físicos de bajo nivel, como "ganancia objetivo mínima de 18 dBi" o "función de penalización para un peso superior a 0.5 kg". La Capa de Aplicación contiene la lógica de negocio para traducir las metas de usuario en un problema de optimización formal y bien definido que el motor de dominio puede resolver.

## Sección 2: Arquitectura Detallada de Módulos

### 2.1. Diagrama de Dependencia de Módulos

El siguiente diagrama ilustra las dependencias entre los módulos principales, reforzando la regla de comunicación unidireccional hacia abajo de la Arquitectura en Capas.

```
┌─────────────────────────────────┐
│      Capa de Aplicación         │
│        (app/facade.py)          │
│                                 │
│  - Traducción de parámetros     │
│  - Orquestación                 │
│  - Formateo de resultados       │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│       Capa de Dominio           │
│          (core/)                │
│                                 │
│  - models.py                    │
│  - physics.py                   │
│  - optimization.py              │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│    Capa de Infraestructura      │
│      (infrastructure/)          │
│                                 │
│  - config.py                    │
│  - file_io.py                   │
└─────────────────────────────────┘
```

### 2.2. Módulo 1: core (El Motor de Dominio)

- **Propósito:** Encapsular toda la lógica de negocio, el conocimiento del dominio (física electromagnética, matemáticas) y los algoritmos de optimización. Este módulo es el "cerebro" de la aplicación y es completamente independiente de cualquier interfaz de usuario o formato de archivo específico.

- **Sub-módulos:**

  - **core.models:** Contiene las estructuras de datos fundamentales (implementadas como Python dataclasses) que representan los conceptos del dominio: `AntennaGeometry` (diámetro, profundidad, etc.), `PerformanceMetrics` (ganancia, ancho de haz), `OptimizationConstraints` (límites de peso, tamaño, regulatorios) y `OptimizationResult`.

  - **core.physics:** Implementa las ecuaciones fundamentales como la ganancia teórica G = η_ap × (πD/λ)² y la relación geométrica d = D²/(16f). También incluye modelos de eficiencia de apertura en función de la relación f/D.

  - **core.optimization:** Contiene la implementación del optimizador multiobjetivo NSGA-II. Su componente central es la función de fitness multiobjetivo, que evalúa la calidad de cada solución candidata: fitness = f(ganancia, peso, cumplimiento_regulatorio).

- **Interfaz Pública (API):** Una clase `OptimizationEngine` que expone un método principal: `run(constraints: OptimizationConstraints) -> OptimizationResult`.

- **Dependencias Externas:** NumPy, SciPy, pymoo.

### 2.3. Módulo 2: app (La Fachada de la Aplicación)

- **Propósito:** Servir como el punto de entrada para interfaces externas, desacoplando la lógica de presentación de la complejidad del core. Provee una API estable y simplificada que traduce las intenciones del usuario en comandos para el motor de dominio.

- **Responsabilidades:**

  1. Recibir datos simples y de alto nivel (ej. un diccionario Python).
  2. **Traducir** estos datos en los objetos `OptimizationConstraints` requeridos por el core.engine.
  3. Invocar el método `run` del core.engine.
  4. Recibir el objeto `OptimizationResult` y formatearlo en una estructura de datos simple (ej. otro diccionario) lista para ser consumida, sin exponer los modelos internos del dominio.

- **Interfaz Pública (API):** Una clase `ApplicationFacade` con métodos como `run_optimization(user_parameters: dict) -> dict`.

- **Dependencias Internas:** core.

### 2.4. Módulo 3: infrastructure (La Capa de Infraestructura)

- **Propósito:** Aislar todas las interacciones con sistemas externos (sistema de archivos, configuración), asegurando que el resto de la aplicación no dependa de implementaciones concretas de I/O.

- **Responsabilidades:**

  - **infrastructure.file_io:** Lógica para guardar y cargar sesiones de proyecto (parámetros de entrada y resultados) en formato JSON. También se encarga de exportar resultados a formatos estándar como CSV para análisis de datos.

  - **infrastructure.config:** Gestionar la configuración de la aplicación, leyendo desde un archivo de configuración (config.toml). Esto incluye constantes físicas, parámetros por defecto del optimizador y los límites regulatorios de la ANE (ej. PIRE máximo de 36 dBm).

- **Dependencias Internas:** Ninguna.

### 2.5. Matriz de Responsabilidades de Módulos

La siguiente tabla formaliza las responsabilidades y límites de cada módulo, sirviendo como un contrato de diseño para el proceso de desarrollo.

| Módulo | Sub-módulo | Responsabilidad Primaria | Clases Clave | Dependencias Externas |
|--------|-----------|-------------------------|--------------|---------------------|
| **core** | core.models | Definir las entidades de datos del dominio. | AntennaGeometry, OptimizationResult | dataclasses |
| | core.physics | Implementar las ecuaciones electromagnéticas y modelos de propagación. | Funciones de cálculo | NumPy, SciPy |
| | core.optimization | Implementar el algoritmo de optimización y la función de fitness. | OptimizationEngine | pymoo |
| **app** | app.facade | Orquestar el flujo de la aplicación y traducir entre interfaces y el core. | ApplicationFacade | N/A |
| **infrastructure** | infrastructure.file_io | Gestionar la lectura/escritura de archivos de proyecto y exportaciones. | SessionManager, ResultsExporter | json, csv |
| | infrastructure.config | Cargar y proporcionar acceso a la configuración de la aplicación. | ConfigLoader | toml |

## Sección 3: Especificaciones Técnicas por Módulo

### 3.1. Especificación de core.engine

- **Propósito:** Realizar los cálculos electromagnéticos y la optimización geométrica de forma precisa y eficiente.

- **Entradas (I/O):** Un objeto `OptimizationConstraints` que encapsula todos los requisitos del problema: rango de diámetros, peso máximo, rango de relación f/D, objetivo de alcance operativo, y restricciones regulatorias.

- **Salidas (I/O):** Un objeto `OptimizationResult` que contiene la `AntennaGeometry` óptima encontrada, sus `PerformanceMetrics` calculadas, y el historial de convergencia del algoritmo para análisis.

- **Lógica Detallada:**

  - Las ecuaciones físicas se implementan siguiendo referencias estándar como Balanis (2016) para el cálculo de ganancia, eficiencia de apertura e iluminación.

  - La función de fitness para el optimizador NSGA-II es una función multiobjetivo que busca maximizar la ganancia mientras aplica penalizaciones por violación de restricciones. Por ejemplo: minimizar(-ganancia, peso) sujeto a restricciones de peso_max y PIRE_max (36 dBm).

- **Estrategia de Pruebas:** Se utiliza pytest para pruebas unitarias. Se crean casos de prueba con resultados conocidos de la literatura para cada ecuación física, con una tolerancia aceptable (ej. 0.1 dB en ganancia). El optimizador se valida contra funciones de benchmark estándar para asegurar su correcta convergencia.

### 3.2. Especificación de app.facade

- **Propósito:** Simplificar la interacción con el core.engine y desacoplar las interfaces externas de la lógica de dominio.

- **Entradas (I/O):** Un diccionario Python con parámetros de alto nivel comprensibles, como `{'desired_range_km': 5, 'max_payload_g': 500, 'min_diameter_m': 0.2, 'max_diameter_m': 1.5}`.

- **Salidas (I/O):** Un diccionario con resultados listos para ser consumidos, como `{'optimal_diameter_mm': 250.5, 'expected_gain_dbi': 20.1, 'weight_estimation_g': 450.0, 'convergence': [...]}`.

- **Lógica Detallada:** Contiene las heurísticas para la traducción. Por ejemplo, el `desired_range_km` se convierte en un requisito de ganancia mínima utilizando la ecuación de transmisión de Friis, asumiendo una potencia de transmisor y sensibilidad de receptor estándar para drones comerciales.

- **Estrategia de Pruebas:** Pruebas de integración que verifican que la fachada invoca correctamente el core.engine con el objeto `OptimizationConstraints` correctamente construido a partir de parámetros de entrada simples.

### 3.3. Especificación de infrastructure.io

- **Propósito:** Gestionar la persistencia de datos y la configuración de la aplicación de manera robusta.

- **Lógica Detallada:** Se utilizan librerías estándar como `json` y `toml` para la serialización de la configuración y las sesiones de proyecto. Para la exportación de resultados se emplea el módulo `csv` estándar de Python. La lógica de carga de configuración es tolerante a fallos, utilizando valores por defecto si el archivo de configuración está ausente o corrupto.

- **Estrategia de Pruebas:** Las pruebas operan en un sistema de archivos temporal. Escriben archivos de configuración y de sesión, los leen de nuevo y afirman que los datos deserializados son idénticos a los originales. Se prueban casos de borde como archivos corruptos o inexistentes.

## Sección 4: Stack Tecnológico y Estándares de Desarrollo

La selección del stack tecnológico se basa en la madurez del ecosistema científico de Python, la productividad del desarrollador y consideraciones pragmáticas.

### 4.1. Lenguaje y Entorno

- **Lenguaje Principal:** Python 3.11+
- **Gestión de Dependencias:** pip con `requirements.txt` y `pyproject.toml`
- **Entorno Virtual:** venv o virtualenv

### 4.2. Librerías Principales

#### Cálculo Científico
- **NumPy:** Operaciones matriciales y vectoriales de alto rendimiento
- **SciPy:** Funciones científicas avanzadas

#### Optimización
- **pymoo:** Framework de optimización multiobjetivo de nivel investigación, soporta NSGA-II y permite extensibilidad para problemas complejos

#### Visualización (para generación de gráficos 2D)
- **Matplotlib:** Gráficos 2D estáticos
- **Plotly:** Gráficos interactivos

#### Configuración y Persistencia
- **toml:** Parseo de archivos de configuración
- **json:** Serialización de sesiones (biblioteca estándar)
- **csv:** Exportación de resultados tabulares (biblioteca estándar)

### 4.3. Testing y Calidad de Código

- **pytest:** Framework de testing principal
- **pytest-cov:** Cobertura de código
- **black:** Formateo automático de código
- **ruff:** Linter rápido y completo

### 4.4. Estándares de Código

1. **Estilo:** Adherencia estricta a PEP 8, aplicado automáticamente con black
2. **Documentación:** Docstrings en formato Google/NumPy para todas las funciones públicas
3. **Type Hints:** Uso de anotaciones de tipo para mejorar la legibilidad y detectabilidad de errores
4. **Testing:** Objetivo de 95%+ de cobertura de código con tests

## Sección 5: Flujo de Datos y Casos de Uso

### 5.1. Caso de Uso Principal: Optimización de Antena

```
1. Usuario → Proporciona parámetros
   ↓
2. ApplicationFacade → Valida y traduce parámetros
   ↓
3. OptimizationConstraints → Creado con restricciones físicas
   ↓
4. OptimizationEngine → Ejecuta NSGA-II
   ↓
5. OptimizationResult → Geometría óptima + métricas
   ↓
6. ApplicationFacade → Formatea resultados
   ↓
7. Usuario ← Recibe resultados en formato simple
```

### 5.2. Flujo de Persistencia

```
1. SessionManager.save_session()
   → Serializa user_parameters + OptimizationResult
   → Guarda en JSON

2. SessionManager.load_session()
   → Lee JSON
   → Deserializa y reconstruye OptimizationResult
```

### 5.3. Flujo de Configuración

```
1. get_config() → Lee config.toml
   ↓
2. Crea objetos de configuración tipados
   ↓
3. Cachea para uso posterior (singleton)
   ↓
4. Proporciona acceso a parámetros en toda la aplicación
```

## Sección 6: Principios de Extensibilidad

### 6.1. Agregar Nuevas Ecuaciones Físicas

Para agregar un nuevo modelo físico:

1. Crear función en `core/physics.py`
2. Documentar con referencias bibliográficas
3. Agregar tests unitarios con valores conocidos
4. Integrar en `OptimizationEngine` si es necesario

### 6.2. Modificar el Algoritmo de Optimización

Para cambiar el algoritmo:

1. Modificar `core/optimization.py`
2. Mantener la interfaz `run(constraints) -> result`
3. Actualizar tests de integración
4. Validar con funciones benchmark

### 6.3. Agregar Nuevos Formatos de Exportación

Para agregar un nuevo formato:

1. Crear método en `infrastructure/file_io.py`
2. Seguir patrón de `SessionManager` o `ResultsExporter`
3. Agregar tests con archivos temporales
4. Documentar formato y casos de uso

## Sección 7: Consideraciones de Despliegue

### 7.1. Instalación

```bash
# Clonar repositorio
git clone <url>
cd Proyecto_Dron

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS

# Instalar dependencias
pip install -e .

# Verificar instalación
pytest tests/ -q
```

### 7.2. Uso Programático

```python
from soga.app.facade import ApplicationFacade

facade = ApplicationFacade()
params = {
    "min_diameter_m": 0.2,
    "max_diameter_m": 1.5,
    "max_payload_g": 800.0,
    "min_f_d_ratio": 0.35,
    "max_f_d_ratio": 0.65,
    "desired_range_km": 5.0,
}
result = facade.run_optimization(params)
print(f"Diámetro óptimo: {result['optimal_diameter_mm']:.2f} mm")
```

### 7.3. Configuración

Todos los parámetros configurables están en `config.toml`:

```toml
[simulation]
frequency_ghz = 2.4
efficiency_peak = 0.70

[optimization]
population_size = 40
max_generations = 80
```

## Sección 8: Referencias

1. Balanis, C.A. (2016). Antenna Theory: Analysis and Design (4th ed.)
2. IEEE Std 145-2013: Definitions of Terms for Antennas
3. Kraus, J.D. (1988). Antennas (3rd ed.)
4. Deb, K. et al. (2002). "A fast and elitist multiobjective genetic algorithm: NSGA-II"

---

**Documento Actualizado:** Octubre 2025
**Versión:** 2.0 (Sin componentes de interfaz gráfica)
