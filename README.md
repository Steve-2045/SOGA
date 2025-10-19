# SOGA - Software de Optimización Geométrica de Antenas

[![Tests](https://img.shields.io/badge/tests-103%20passed-success)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Code Quality](https://img.shields.io/badge/code%20quality-A+-brightgreen)]()

**SOGA** es un motor de optimización multiobjetivo especializado en el diseño de antenas parabólicas para drones (UAVs). Utiliza algoritmos genéticos avanzados (NSGA-II) para encontrar geometrías óptimas que balancean ganancia, peso y restricciones operacionales.

---

## 🎯 Características Principales

- **Optimización Multiobjetivo**: Algoritmo NSGA-II para balance ganancia/peso
- **Modelos Físicos Rigurosos**: Basado en ecuaciones electromagnéticas de Balanis, Kraus, IEEE y Nikolova
- **Validaciones Inteligentes**: Sistema de diagnóstico detallado con 6 tipos de análisis de infeasibilidad
- **Arquitectura Modular**: Separación clara entre dominio, aplicación e infraestructura
- **Alta Calidad**: 94% de cobertura de tests, 103 tests pasando
- **Configurable**: Todos los parámetros centralizados en `config.toml`
- **Reproducible**: Resultados deterministas con semillas fijas
- **Interfaz Web Moderna**: Dashboard interactivo con Streamlit y diseño profesional oscuro
- **Launcher Inteligente**: Auto-setup con detección y recuperación de entornos virtuales corruptos
- **UI/UX Mejorada**: Tema oscuro con gradientes morados, componentes estilizados y animaciones suaves

---

## 📋 Tabla de Contenidos

- [Instalación](#instalación)
- [Uso Rápido](#uso-rápido)
- [Interfaz Web](#interfaz-web)
- [Arquitectura](#arquitectura)
- [Configuración](#configuración)
- [Desarrollo](#desarrollo)
- [Documentación](#documentación)
- [Tests](#tests)

---

## 💻 Requisitos

- **Python**: 3.9 o superior
- **Sistema Operativo**: Linux, macOS, Windows
- **RAM**: 512 MB mínimo (2 GB recomendado para optimizaciones grandes)

---

## 🚀 Inicio Rápido

### Instalación Automática (Recomendado)

Solo necesitas tener Python instalado. Los scripts de inicio configurarán todo automáticamente.

#### 1. Clonar el repositorio

```bash
git clone https://github.com/Steve-2045/SOGA.git
cd SOGA
```

#### 2. Ejecutar el dashboard

**En Windows:**
```bash
run_dashboard.bat
```

**En Linux/macOS:**
```bash
chmod +x run_dashboard.sh  # Solo la primera vez
./run_dashboard.sh
```

¡Eso es todo! El script automáticamente:
- ✅ Crea el entorno virtual (primera ejecución)
- ✅ Instala todas las dependencias (primera ejecución)
- ✅ Detecta y repara entornos virtuales corruptos
- ✅ Reinstala dependencias faltantes automáticamente
- ✅ Lanza el dashboard en http://localhost:8501

En ejecuciones posteriores, simplemente ejecuta el mismo script y se abrirá el dashboard directamente. Si el entorno virtual presenta problemas, el script lo detectará y recreará automáticamente.

---

### Instalación Manual (Avanzado)

Si prefieres instalar manualmente:

```bash
# 1. Crear entorno virtual
python3 -m venv venv

# 2. Activar entorno virtual
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. Instalar SOGA y dependencias
pip install -e .
pip install -r streamlit_app/requirements.txt

# 4. Verificar instalación
python -m pytest tests/ -q
```

---

## ⚡ Uso Rápido

### Uso Programático

```python
from soga.app.facade import ApplicationFacade

# Crear instancia de la fachada
facade = ApplicationFacade()

# Definir parámetros de optimización
params = {
    "min_diameter_m": 0.2,      # Diámetro mínimo: 20 cm
    "max_diameter_m": 1.5,      # Diámetro máximo: 1.5 m
    "max_payload_g": 800.0,     # Peso máximo: 800 gramos
    "min_f_d_ratio": 0.35,      # Relación focal mínima
    "max_f_d_ratio": 0.65,      # Relación focal máxima
    "desired_range_km": 5.0,    # Alcance deseado: 5 km
}

# Ejecutar optimización
result = facade.run_optimization(params)

# Mostrar resultados
print(f"Diámetro óptimo: {result['optimal_diameter_mm']:.2f} mm")
print(f"Distancia focal: {result['optimal_focal_length_mm']:.2f} mm")
print(f"Ganancia esperada: {result['expected_gain_dbi']:.2f} dBi")
```

### Ejemplos

Consulta los ejemplos en la carpeta `examples/`:

```bash
python examples/basic_optimization.py
python examples/advanced_optimization.py
```

---

## 🌐 Interfaz Web

SOGA incluye una interfaz web interactiva construida con Streamlit.

### Ejecutar el dashboard

**Windows:**
```bash
run_dashboard.bat
```

**Linux/macOS:**
```bash
./run_dashboard.sh
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

### Características del Dashboard

- **Nueva Optimización**: Configura parámetros y ejecuta optimizaciones con validación en tiempo real
- **Diagnóstico Inteligente**: 6 tipos de análisis de infeasibilidad con cálculos matemáticos detallados
  - Restricciones de peso físicamente imposibles
  - Incompatibilidad peso-diámetro
  - Rangos f/D demasiado estrechos
  - Rangos de diámetro limitados
  - Alcance incompatible con tamaño de antena
  - Problemas sobre-restringidos generales
- **Análisis de Resultados**: Visualiza y compara resultados guardados
- **Gráficos Interactivos**: Frentes de Pareto, convergencia, geometrías
- **Exportación**: Descarga resultados en CSV
- **Tema Moderno**: Diseño oscuro profesional con gradientes morados
- **Componentes Estilizados**: Tarjetas, botones y elementos con animaciones suaves
- **Accesibilidad**: WCAG AA compliant con navegación por teclado

### Documentación UI

- [UI_ENHANCEMENTS.md](docs/UI_ENHANCEMENTS.md) - Guía completa de mejoras UI
- [COMPONENT_GUIDE.md](docs/COMPONENT_GUIDE.md) - Referencia de componentes
- [UI_CHANGELOG.md](UI_CHANGELOG.md) - Registro de cambios UI

Para más detalles, consulta [streamlit_app/README.md](streamlit_app/README.md)

---

## 🏗️ Arquitectura

SOGA sigue una **arquitectura en capas** estricta:

```
┌─────────────────────────────────────────┐
│     app/facade.py (Capa de Aplicación)  │
│   - Traducción usuario → dominio        │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│        core/ (Capa de Dominio)          │
│   - models.py: Estructuras de datos     │
│   - physics.py: Ecuaciones físicas      │
│   - optimization.py: Algoritmo NSGA-II  │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  infrastructure/ (Infraestructura)      │
│   - config.py: Configuración TOML       │
│   - file_io.py: Persistencia            │
└─────────────────────────────────────────┘
```

### Estructura de Directorios

```
Proyecto_Dron/
├── src/soga/              # Código fuente
│   ├── core/              # Lógica de dominio
│   ├── app/               # Capa de aplicación
│   └── infrastructure/    # Infraestructura
├── tests/                 # Tests unitarios e integración
├── examples/              # Ejemplos de uso
├── streamlit_app/         # Aplicación web Streamlit
├── docs/                  # Documentación
├── scripts/               # Scripts auxiliares
├── config.toml            # Configuración principal
├── pyproject.toml         # Metadatos del proyecto
└── requirements.txt       # Dependencias
```

---

## ⚙️ Configuración

Edita `config.toml` para personalizar parámetros:

```toml
[simulation]
frequency_ghz = 2.4               # Banda ISM 2.4 GHz
aperture_efficiency = 0.6         # Eficiencia de apertura típica
areal_density_kg_per_m2 = 1.8     # Densidad areal realista (reflector + feed + estructura)
beamwidth_k_factor = 65.0         # Factor k para cálculo de ancho de haz (IEEE Std 145-2013)

[aperture_efficiency_model]
efficiency_peak = 0.70            # Eficiencia máxima alcanzable
optimal_f_d_ratio = 0.45          # f/D óptimo (spillover vs blockage)
curvature_blockage = 0.128        # Curvatura en régimen de blockage (f/D < 0.45)
curvature_spillover = 0.236       # Curvatura en régimen de spillover (f/D ≥ 0.45)

[optimization]
population_size = 40              # Tamaño población NSGA-II
max_generations = 80              # Generaciones
seed = 1                          # Reproducibilidad

[realistic_limits]
min_diameter_m = 0.05             # Diámetro mínimo
max_diameter_m = 3.0              # Diámetro máximo
max_payload_g = 5000.0            # Peso máximo
```

---

## 🛠️ Desarrollo

### Ejecutar tests

```bash
# Todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=src/soga --cov-report=term-missing

# Tests específicos
pytest tests/core/test_physics.py -v
```

### Formateo de código

```bash
# Formatear con black
black src/ tests/

# Linter con ruff
ruff check src/ tests/
```

### Scripts de auditoría

Los scripts de auditoría están en `scripts/audit/`:

```bash
python scripts/audit/auditoria_fase2_physics.py
python scripts/audit/auditoria_fase3_models.py
python scripts/audit/auditoria_fase4_optimization.py
```

---

## 📚 Documentación

La documentación completa está en la carpeta `docs/`:

- [REPORTE_AUDITORIA_FINAL.md](docs/REPORTE_AUDITORIA_FINAL.md): Auditoría completa del sistema
- [soga-architecture-guide.md](docs/soga-architecture-guide.md): Guía de arquitectura
- [GUI_README.md](docs/GUI_README.md): Documentación del dashboard

---

## 📊 Tests

- **103 tests** pasando (100%)
- **94% cobertura** de código
- Tests unitarios, integración y edge cases
- Validación matemática contra literatura (Balanis, Kraus, IEEE)

### Ejecución continua

```bash
# Modo watch
pytest-watch tests/
```

---

## 🔬 Validación Científica

SOGA ha sido validado contra literatura científica estándar:

- **Balanis, C.A.** "Antenna Theory" (2016) - Capítulo 15: Reflector Antennas
- **Kraus, J.D.** "Antennas" (1988) - Capítulo 9: Parabolic Reflectors
- **IEEE Std 145-2013**: Definitions of Terms for Antennas
- **Nikolova, N.K.** (2016) "Lecture 19: Reflector Antennas" - McMaster University
- **Stutzman & Thiele** "Antenna Theory and Design" (2012)
- **Wade, P. N1BWT** "Parabolic Dish Antennas" - ARRL

### Modelo de Eficiencia de Apertura

El modelo implementa una curva asimétrica validada con datos de múltiples fuentes:

```
η(f/D) = η_peak - κ(f/D) × (f/D - f/D_opt)²

donde:
- η_peak = 0.70 (máximo alcanzable)
- f/D_opt = 0.45 (óptimo teórico)
- κ = 0.128 (blockage regime, f/D < 0.45)
- κ = 0.236 (spillover regime, f/D ≥ 0.45)
```

Ratio de asimetría: **1.84×** (spillover degrada ~2× más rápido que blockage)

Todas las fórmulas electromagnéticas implementadas han sido verificadas con:
- Calculadoras de referencia (Pasternack, RF Wireless World)
- Cálculos manuales paso a paso con derivaciones completas
- Validación de propiedades físicas (G ∝ D², θ ∝ 1/D, η vs f/D)
- Datasheets comerciales de antenas parabólicas

---

**Hecho con ❤️ para agricultura de precisión y aplicaciones UAV**
