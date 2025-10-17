# Estructura del Proyecto SOGA

Este documento describe la organización del proyecto siguiendo los estándares de Python.

## Estructura de Directorios

```
Proyecto_Dron/
│
├── src/soga/                   # Código fuente del paquete
│   ├── __init__.py
│   ├── core/                   # Lógica de dominio (domain layer)
│   │   ├── __init__.py
│   │   ├── models.py          # Modelos de datos (AntennaGeometry, etc.)
│   │   ├── physics.py         # Ecuaciones electromagnéticas
│   │   └── optimization.py    # Motor de optimización NSGA-II
│   │
│   ├── app/                    # Capa de aplicación
│   │   ├── __init__.py
│   │   └── facade.py          # Fachada de aplicación (API principal)
│   │
│   └── infrastructure/         # Infraestructura
│       ├── __init__.py
│       ├── config.py          # Gestión de configuración TOML
│       └── file_io.py         # Persistencia (JSON, CSV)
│
├── tests/                      # Tests unitarios e integración
│   ├── __init__.py
│   ├── core/
│   │   ├── test_models.py
│   │   ├── test_physics.py
│   │   └── test_optimization.py
│   ├── app/
│   │   └── test_facade.py
│   └── infrastructure/
│       ├── test_config.py
│       └── test_file_io.py
│
├── examples/                   # Ejemplos de uso
│   ├── basic_optimization.py
│   └── advanced_optimization.py
│
├── streamlit_app/              # Aplicación web
│   ├── app.py                 # Aplicación principal Streamlit
│   ├── pages/                 # Páginas multi-página
│   │   ├── 1_🚀_New_Optimization.py
│   │   ├── 2_📊_Results_Analysis.py
│   │   └── 3_ℹ️_About.py
│   ├── .streamlit/
│   │   └── config.toml        # Configuración de Streamlit
│   └── README.md
│
├── docs/                       # Documentación
│   ├── REPORTE_AUDITORIA_FINAL.md
│   ├── soga-architecture-guide.md
│   ├── GUI_README.md
│   └── PROJECT_STRUCTURE.md   # Este archivo
│
├── scripts/                    # Scripts auxiliares
│   └── audit/                 # Scripts de auditoría
│       ├── auditoria_fase2_physics.py
│       ├── auditoria_fase3_models.py
│       ├── auditoria_fase4_optimization.py
│       └── auditoria_eficiencia_vs_fd.png
│
├── config.toml                 # Configuración principal del sistema
├── pyproject.toml              # Metadatos del proyecto (PEP 621)
├── requirements.txt            # Dependencias
├── MANIFEST.in                 # Archivos a incluir en distribución
├── .gitignore                  # Archivos ignorados por Git
├── README.md                   # Documentación principal
│
└── venv/                       # Entorno virtual (no versionado)
```

---

## Descripción de Carpetas

### `src/soga/`
Código fuente del paquete Python. Dividido en 3 capas:

- **core/**: Lógica de negocio pura, sin dependencias externas
- **app/**: Capa de aplicación que orquesta el dominio
- **infrastructure/**: Detalles de implementación (config, I/O)

### `tests/`
Tests organizados reflejando la estructura de `src/`. Incluye:
- Tests unitarios (funciones individuales)
- Tests de integración (interacción entre módulos)
- Tests de edge cases

### `examples/`
Scripts de ejemplo mostrando cómo usar la librería.

### `streamlit_app/`
Aplicación web independiente. Puede ejecutarse separadamente del paquete core.

### `docs/`
Toda la documentación del proyecto:
- Reportes de auditoría
- Guías de arquitectura
- Documentación técnica

### `scripts/`
Scripts auxiliares que no son parte del paquete distribuible:
- Scripts de auditoría
- Herramientas de desarrollo

---

## Archivos de Configuración

### `pyproject.toml`
Archivo estándar PEP 621 con metadatos del proyecto:
- Información del paquete (nombre, versión, autores)
- Dependencias
- Configuración de herramientas (pytest, coverage, black)

### `config.toml`
Configuración específica de SOGA:
- Parámetros físicos
- Configuración de optimización
- Límites realistas

### `requirements.txt`
Lista de dependencias para instalación con pip.

### `MANIFEST.in`
Especifica qué archivos incluir en la distribución del paquete.

### `.gitignore`
Archivos y carpetas ignorados por Git (venv, __pycache__, etc.)

---

## Convenciones de Nomenclatura

### Archivos Python
- Módulos: `snake_case.py` (ej: `file_io.py`)
- Clases: `PascalCase` (ej: `ApplicationFacade`)
- Funciones/métodos: `snake_case` (ej: `calculate_gain`)
- Constantes: `UPPER_SNAKE_CASE` (ej: `SPEED_OF_LIGHT`)

### Directorios
- Minúsculas con guiones bajos: `streamlit_app`, `test_cases`
- Paquetes Python: minúsculas sin guiones (ej: `soga`)

---

## Importaciones

### Desde el paquete instalado
```python
from soga.app.facade import ApplicationFacade
from soga.core.models import AntennaGeometry
from soga.core.physics import calculate_gain
```

### Importaciones relativas (dentro del paquete)
```python
# En src/soga/app/facade.py
from soga.core.models import OptimizationConstraints
from soga.infrastructure.config import get_config
```

---

## Instalación del Paquete

### Modo desarrollo (editable)
```bash
pip install -e .
```

Permite editar el código sin reinstalar.

### Modo producción
```bash
pip install .
```

Instala el paquete en site-packages.

---

## Tests

### Ejecutar todos los tests
```bash
pytest tests/ -v
```

### Con cobertura
```bash
pytest tests/ --cov=src/soga --cov-report=html
```

Genera reporte HTML en `htmlcov/`.

---

## Distribución

### Crear paquete distribuible
```bash
python -m build
```

Genera archivos en `dist/`:
- `.tar.gz` (source distribution)
- `.whl` (wheel, built distribution)

---

## Limpieza

### Archivos temporales a eliminar
```bash
# Cache de Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Cache de pytest
rm -rf .pytest_cache

# Reporte de cobertura
rm -rf htmlcov .coverage

# Build artifacts
rm -rf build dist *.egg-info
```

---

## Mejores Prácticas Aplicadas

✅ **Separación de responsabilidades**: Código en capas (domain, app, infrastructure)

✅ **Organización estándar**: Estructura `src/` layout (PEP 420)

✅ **Tests co-localizados**: Estructura de tests refleja estructura de código

✅ **Documentación separada**: `docs/` para toda la documentación

✅ **Ejemplos accesibles**: `examples/` para casos de uso

✅ **Configuración centralizada**: Todos los archivos de config en raíz o `.streamlit/`

✅ **Archivos ignorados**: `.gitignore` completo

✅ **Metadatos estándar**: `pyproject.toml` (PEP 621)

✅ **Manifesto de distribución**: `MANIFEST.in` para paquete

---

## Referencias

- [PEP 420](https://peps.python.org/pep-0420/) - Implicit Namespace Packages
- [PEP 621](https://peps.python.org/pep-0621/) - pyproject.toml project metadata
- [Python Packaging User Guide](https://packaging.python.org/)
- [Structuring Your Project (Hitchhiker's Guide)](https://docs.python-guide.org/writing/structure/)
