"""
Acerca del Proyecto - SOGA Dashboard
=====================================

Information page providing project context, scientific background, and technical documentation.

Author: SOGA Development Team
License: MIT
"""

import sys
from pathlib import Path

import streamlit as st

# Ensure the backend is importable
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from soga.infrastructure.config import get_config

# Page configuration
st.set_page_config(
    page_title="Acerca del Proyecto - SOGA",
    page_icon="ℹ️",
    layout="wide",
)


def load_readme() -> str:
    """Load the project README.md file."""
    readme_path = project_root / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return "README.md no encontrado."


def main() -> None:
    """Main page rendering function."""
    st.title("ℹ️ Acerca de SOGA")
    st.markdown("Documentación técnica, fundamentos científicos y contexto del proyecto")

    st.markdown("---")

    # Tabs for organized information
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📖 Descripción General",
            "🏗️ Arquitectura del Sistema",
            "🔬 Fundamentos Científicos",
            "📄 README del Proyecto",
        ]
    )

    # Tab 1: General Description
    with tab1:
        st.header("Software de Optimización Geométrica de Antenas")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(
                """
                ### ¿Qué es SOGA?

                **SOGA** (Software de Optimización Geométrica de Antenas) es un motor de optimización
                multi-objetivo especializado en el diseño de antenas parabólicas para aplicaciones
                de Vehículos Aéreos No Tripulados (UAVs).

                ### Objetivo Principal

                Encontrar la geometría óptima de una antena parabólica que maximice la ganancia directiva
                mientras satisface restricciones de peso, tamaño y operación en plataformas móviles aéreas.

                ### Contexto de Aplicación

                - **Agricultura de Precisión**: Telemetría de sensores en campos agrícolas
                - **Monitoreo Ambiental**: Recolección de datos de estaciones remotas
                - **Comunicaciones de Emergencia**: Enlaces de larga distancia en zonas de desastre
                - **Investigación Científica**: Estudios atmosféricos y geológicos

                ### Características Destacadas

                - Optimización multi-objetivo con algoritmo genético NSGA-II
                - Validación física contra ecuaciones de Balanis, Kraus e IEEE
                - Arquitectura modular y extensible (Clean Architecture)
                - 94% de cobertura de tests con 103 tests unitarios
                - Configuración centralizada y reproducibilidad garantizada
                - Interfaz web profesional para visualización y análisis
                """
            )

        with col2:
            st.markdown("### Especificaciones Técnicas")

            # Load configuration
            config = get_config()

            specs = {
                "Frecuencia": f"{config.simulation.frequency_ghz} GHz",
                "Banda": "ISM 2.4 GHz",
                "Algoritmo": "NSGA-II",
                "Tamaño Población": config.optimization.population_size,
                "Generaciones": config.optimization.max_generations,
                "Eficiencia Apertura": f"{config.simulation.aperture_efficiency * 100:.0f}%",
                "Factor K Beamwidth": config.simulation.beamwidth_k_factor,
                "EIRP Máximo": f"{config.regulatory.max_eirp_dbm} dBm",
            }

            for key, value in specs.items():
                st.metric(key, value)

        st.markdown("---")

        # Key benefits
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                """
                #### 🎯 Precisión Científica

                - Ecuaciones electromagnéticas rigurosas
                - Validación contra literatura estándar
                - Modelos físicos verificables
                """
            )

        with col2:
            st.markdown(
                """
                #### ⚡ Alto Rendimiento

                - Algoritmo evolutivo eficiente
                - Convergencia rápida (40-80 generaciones)
                - Reproducibilidad con semillas fijas
                """
            )

        with col3:
            st.markdown(
                """
                #### 🛠️ Mantenibilidad

                - Arquitectura en capas clara
                - Cobertura de tests del 94%
                - Documentación técnica completa
                """
            )

    # Tab 2: Architecture
    with tab2:
        st.header("Arquitectura del Sistema")

        st.markdown(
            """
            SOGA implementa una **arquitectura en capas** (Clean Architecture) que separa claramente
            las responsabilidades y facilita el mantenimiento, testing y extensibilidad.
            """
        )

        # Architecture diagram
        st.markdown("### Diagrama de Arquitectura")

        st.code(
            """
┌──────────────────────────────────────────────────────────┐
│                  INTERFAZ DE USUARIO                      │
│                                                           │
│  - Streamlit Dashboard (streamlit_app/)                  │
│  - API Programática (Python)                             │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ↓
┌──────────────────────────────────────────────────────────┐
│             CAPA DE APLICACIÓN (app/)                     │
│                                                           │
│  - ApplicationFacade                                      │
│    • Traducción de parámetros usuario → dominio          │
│    • Validación de entrada contra límites realistas      │
│    • Formateo de salida (m → mm, precisión)              │
│    • Manejo de errores (FacadeValidationError)           │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ↓
┌──────────────────────────────────────────────────────────┐
│              CAPA DE DOMINIO (core/)                      │
│                                                           │
│  models.py - Estructuras de Datos                        │
│    • AntennaGeometry: diameter, focal_length, f/D        │
│    • PerformanceMetrics: gain, beamwidth                 │
│    • OptimizationConstraints: restricciones físicas      │
│    • OptimizationResult: resultado completo              │
│                                                           │
│  physics.py - Ecuaciones Electromagnéticas               │
│    • AntennaPhysics                                      │
│      - calculate_gain() [Balanis, Kraus]                │
│      - calculate_beamwidth() [IEEE Std 145-2013]         │
│      - efficiency_curve() [Modelo parabólico validado]   │
│                                                           │
│  optimization.py - Algoritmo NSGA-II                     │
│    • OptimizationEngine                                  │
│      - run(): Ejecuta optimización multi-objetivo        │
│      - Función objetivo: maximizar ganancia              │
│      - Restricciones: peso, geometría, f/D               │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ↓
┌──────────────────────────────────────────────────────────┐
│         CAPA DE INFRAESTRUCTURA (infrastructure/)         │
│                                                           │
│  config.py - Gestión de Configuración                    │
│    • ConfigLoader: Carga y valida config.toml            │
│    • AppConfig: Configuración tipada con dataclasses     │
│    • get_config(): Singleton lazy-loading                │
│                                                           │
│  file_io.py - Persistencia de Datos                      │
│    • SessionManager: save/load sesiones JSON             │
│    • ResultsExporter: exportar a CSV                     │
└──────────────────────────────────────────────────────────┘
            """,
            language="text",
        )

        st.markdown("---")

        # Layers description
        st.markdown("### Descripción de Capas")

        with st.expander("📱 Interfaz de Usuario", expanded=True):
            st.markdown(
                """
                **Responsabilidades:**
                - Presentación de datos al usuario
                - Recolección de parámetros de entrada
                - Visualización interactiva de resultados
                - Gestión de sesiones y exportación

                **Implementaciones:**
                - `streamlit_app/`: Dashboard web profesional con Plotly
                - API programática: Uso directo de `ApplicationFacade`

                **Tecnologías:**
                - Streamlit 1.28+
                - Plotly para gráficos interactivos
                - Pandas para tablas de datos
                """
            )

        with st.expander("🎯 Capa de Aplicación", expanded=True):
            st.markdown(
                """
                **Responsabilidades:**
                - Traducir entre términos de usuario y conceptos de dominio
                - Validar entrada contra límites físicos realistas
                - Aplicar valores por defecto
                - Convertir unidades (metros ↔ milímetros, gramos ↔ kilogramos)
                - Formatear salida con precisión de manufactura

                **Componente Principal: `ApplicationFacade`**

                ```python
                facade = ApplicationFacade()
                result = facade.run_optimization(user_parameters)
                ```

                **Validaciones Implementadas:**
                - Rangos de parámetros contra `realistic_limits`
                - Consistencia de valores (min < max)
                - Tipos de datos correctos
                - Conversión segura de unidades
                """
            )

        with st.expander("🧠 Capa de Dominio", expanded=True):
            st.markdown(
                """
                **Responsabilidades:**
                - Lógica de negocio central
                - Ecuaciones electromagnéticas
                - Algoritmos de optimización
                - Modelos de datos del dominio

                **Módulos:**

                1. **models.py**: Estructuras de datos inmutables con validación
                   - `AntennaGeometry`: Geometría de antena parabólica
                   - `PerformanceMetrics`: Métricas de rendimiento RF
                   - `OptimizationConstraints`: Restricciones de diseño
                   - `OptimizationResult`: Resultado completo de optimización

                2. **physics.py**: Ecuaciones electromagnéticas científicamente validadas
                   - Ganancia según Balanis y Kraus
                   - Beamwidth según IEEE Std 145-2013
                   - Curva de eficiencia vs. f/D ratio

                3. **optimization.py**: Algoritmo genético NSGA-II
                   - Optimización multi-objetivo
                   - Función objetivo: maximizar ganancia
                   - Restricciones: peso, geometría física, f/D ratio

                **Independencia:**
                Esta capa NO conoce nada de UI, archivos o configuración externa.
                Todas las dependencias están inyectadas.
                """
            )

        with st.expander("🔧 Capa de Infraestructura", expanded=True):
            st.markdown(
                """
                **Responsabilidades:**
                - Carga y validación de configuración
                - Persistencia de datos (JSON, CSV)
                - Acceso a recursos externos
                - Servicios de infraestructura

                **Módulos:**

                1. **config.py**: Sistema de configuración robusto
                   - Carga desde `config.toml`
                   - Validación exhaustiva de valores
                   - Singleton pattern para eficiencia
                   - Dataclasses tipadas para seguridad

                2. **file_io.py**: Persistencia de sesiones y resultados
                   - `SessionManager`: Guardar/cargar sesiones completas
                   - `ResultsExporter`: Exportar a CSV para análisis externo

                **Beneficios:**
                - Toda la configuración centralizada
                - Validación temprana de parámetros
                - Separación de concerns
                """
            )

        st.markdown("---")

        # Design principles
        st.markdown("### Principios de Diseño")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
                #### Clean Architecture

                - Separación de responsabilidades
                - Independencia de frameworks
                - Testabilidad
                - Flujo de dependencias unidireccional

                #### SOLID Principles

                - Single Responsibility
                - Open/Closed Principle
                - Dependency Inversion
                """
            )

        with col2:
            st.markdown(
                """
                #### Type Safety

                - Type hints en todo el código
                - Validación en tiempo de ejecución
                - Dataclasses para estructuras

                #### Testing

                - 103 tests unitarios
                - 94% de cobertura
                - Tests de integración
                """
            )

    # Tab 3: Scientific Background
    with tab3:
        st.header("Fundamentos Científicos")

        st.markdown(
            """
            SOGA está basado en principios electromagnéticos rigurosos validados contra
            literatura científica estándar del campo de antenas.
            """
        )

        # Gain calculation
        with st.expander("📡 Cálculo de Ganancia (Balanis & Kraus)", expanded=True):
            st.markdown(
                r"""
                ### Ecuación de Ganancia

                La ganancia de una antena parabólica se calcula según:

                $$
                G = \eta_{ap} \cdot \left(\frac{\pi D}{\lambda}\right)^2
                $$

                Donde:
                - $G$ = Ganancia adimensional (lineal)
                - $\eta_{ap}$ = Eficiencia de apertura (0-1)
                - $D$ = Diámetro de la apertura (metros)
                - $\lambda$ = Longitud de onda (metros)

                ### Conversión a dBi

                $$
                G_{dBi} = 10 \log_{10}(G)
                $$

                ### Eficiencia de Apertura

                La eficiencia de apertura depende de la relación f/D y sigue una curva
                parabólica con máximo en f/D ≈ 0.45:

                $$
                \eta(f/D) = \eta_{peak} - c_{low}(f/D - f/D_{opt})^2 \quad \text{si } f/D < f/D_{opt}
                $$

                $$
                \eta(f/D) = \eta_{peak} - c_{high}(f/D - f/D_{opt})^2 \quad \text{si } f/D \geq f/D_{opt}
                $$

                **Referencias:**
                - Balanis, C.A. "Antenna Theory: Analysis and Design" (2016)
                - Kraus, J.D. "Antennas" (1988)
                """
            )

        # Beamwidth calculation
        with st.expander("📐 Ancho de Haz (IEEE Std 145-2013)", expanded=True):
            st.markdown(
                r"""
                ### Half-Power Beamwidth (HPBW)

                El ancho de haz a -3dB (HPBW) se calcula como:

                $$
                \theta_{3dB} = k \cdot \frac{\lambda}{D}
                $$

                Donde:
                - $\theta_{3dB}$ = Ancho de haz en radianes
                - $k$ = Factor de forma (típicamente 65° para parábolas)
                - $\lambda$ = Longitud de onda (metros)
                - $D$ = Diámetro de apertura (metros)

                ### Conversión a Grados

                $$
                \theta_{deg} = \theta_{3dB} \cdot \frac{180}{\pi}
                $$

                **Significado Físico:**

                El HPBW define el ángulo dentro del cual la potencia radiada es al menos
                la mitad (-3 dB) de la potencia máxima en la dirección de máxima ganancia.

                **Referencias:**
                - IEEE Std 145-2013: Definitions of Terms for Antennas
                """
            )

        # Optimization algorithm
        with st.expander("🧬 Algoritmo NSGA-II", expanded=True):
            st.markdown(
                """
                ### Non-dominated Sorting Genetic Algorithm II

                NSGA-II es un algoritmo evolutivo multi-objetivo que encuentra un conjunto
                de soluciones óptimas (Frente de Pareto) balanceando múltiples objetivos.

                ### Características

                - **Elitismo**: Preserva las mejores soluciones entre generaciones
                - **Crowding Distance**: Mantiene diversidad en el frente de Pareto
                - **Fast Non-dominated Sorting**: Clasificación eficiente de soluciones

                ### Función Objetivo en SOGA

                ```python
                maximize: gain(diameter, f_d_ratio)

                subject to:
                    min_diameter ≤ diameter ≤ max_diameter
                    min_f_d ≤ f_d_ratio ≤ max_f_d
                    weight(diameter, f_d) ≤ max_weight
                ```

                ### Parámetros de Configuración

                - **Tamaño de Población**: 40 individuos
                - **Generaciones Máximas**: 80 iteraciones
                - **Operadores Genéticos**:
                  - Crossover: SBX (Simulated Binary Crossover)
                  - Mutación: Polynomial Mutation
                  - Probabilidades adaptativas

                ### Convergencia

                El algoritmo típicamente converge en 40-60 generaciones, mejorando
                la ganancia en ~2-5 dB respecto a la población inicial aleatoria.

                **Referencias:**
                - Deb, K. et al. "A fast and elitist multiobjective genetic algorithm: NSGA-II" (2002)
                - Coello Coello, C.A. "Evolutionary Algorithms for Solving Multi-Objective Problems" (2007)
                """
            )

        # Physical constraints
        with st.expander("⚖️ Restricciones Físicas y Realistas", expanded=True):
            st.markdown(
                """
                ### Límites de Diseño

                SOGA valida todas las soluciones contra restricciones físicas y operacionales
                basadas en capacidades reales de UAVs y fabricación de antenas.

                ### Diámetro de Antena

                - **Mínimo**: 5 cm (50 mm)
                  - Justificación: Ganancia mínima útil a 2.4 GHz
                  - Menor a esto: ganancia insuficiente para enlaces confiables

                - **Máximo**: 3 m (3000 mm)
                  - Justificación: Límite de transportabilidad en UAVs comerciales
                  - Mayor a esto: problemas de estabilidad aerodinámica

                ### Relación f/D

                - **Mínimo**: 0.2
                  - Justificación: Parábola muy profunda, difícil de fabricar
                  - Problemas de bloqueo del feed

                - **Máximo**: 1.5
                  - Justificación: Parábola muy plana, baja eficiencia
                  - Spillover excesivo

                - **Óptimo**: 0.45
                  - Maximiza eficiencia de apertura
                  - Balance entre bloqueo y spillover

                ### Peso (Payload)

                - **Mínimo**: 10 g
                  - Justificación: Peso mínimo con estructura mecánica

                - **Máximo**: 5 kg (5000 g)
                  - Justificación: Capacidad típica de UAVs comerciales (DJI, etc.)

                ### Alcance de Comunicación

                - **Mínimo**: 100 m (0.1 km)
                  - Justificación: Aplicaciones de corto alcance

                - **Máximo**: 50 km
                  - Justificación: Límite práctico con EIRP regulatorio (36 dBm)
                  - Ecuación de Friis con sensibilidad de receptor típica
                """
            )

        # Validation
        st.markdown("---")
        st.markdown("### Validación Científica")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
                #### Literatura de Referencia

                1. **Balanis, C.A.** "Antenna Theory: Analysis and Design" (2016)
                   - Ecuaciones de ganancia y eficiencia

                2. **Kraus, J.D.** "Antennas" (1988)
                   - Propiedades de antenas parabólicas

                3. **IEEE Std 145-2013**
                   - Definiciones estándar de términos

                4. **Stutzman & Thiele** "Antenna Theory and Design" (2012)
                   - Diseño y optimización de antenas
                """
            )

        with col2:
            st.markdown(
                """
                #### Métodos de Validación

                - **Cálculos Manuales**: Verificación paso a paso de ecuaciones

                - **Calculadoras de Referencia**: Comparación con herramientas comerciales
                  (Pasternack, RF Wireless World)

                - **Propiedades Físicas**: Verificación de relaciones fundamentales
                  - G ∝ D² (ganancia proporcional al área)
                  - θ ∝ 1/D (beamwidth inversamente proporcional)

                - **Tests Unitarios**: 103 tests verificando todas las ecuaciones
                """
            )

    # Tab 4: README
    with tab4:
        st.header("README del Proyecto")

        st.markdown(
            "A continuación se muestra el contenido completo del archivo README.md del proyecto:"
        )

        readme_content = load_readme()
        st.markdown(readme_content)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #667eea;'>
            <p>Para más información, consulta la documentación completa en la carpeta <code>docs/</code></p>
            <p>GitHub: <a href="https://github.com/tu-repo/soga" style="color: #667eea;">https://github.com/tu-repo/soga</a></p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
