# Mejores Prácticas del Proyecto SOGA

Este documento describe las mejores prácticas implementadas en el proyecto SOGA para garantizar calidad, mantenibilidad y robustez del código.

## 1. Arquitectura y Organización

### Estructura Modular
```
src/soga/
├── core/           # Lógica de negocio pura (sin dependencias externas)
├── infrastructure/ # Servicios de infraestructura (config, I/O)
└── app/            # Capa de aplicación (facade para UI)
```

**Principios aplicados:**
- **Separación de responsabilidades**: Cada módulo tiene una responsabilidad única
- **Inversión de dependencias**: La lógica de negocio no depende de la infraestructura
- **Facade Pattern**: API simplificada para interfaces de usuario

## 2. Validación de Datos

### Validación en Dataclasses
Todos los dataclasses implementan validación en `__post_init__`:

```python
@dataclass
class AntennaGeometry:
    diameter: float
    focal_length: float

    def __post_init__(self):
        if self.diameter <= 0:
            raise ValueError(f"El diámetro debe ser positivo")
        # Más validaciones...
```

**Beneficios:**
- Falla rápido (fail-fast) con errores claros
- Los objetos siempre están en estado válido
- Previene errores en cascada

### Validación de Configuración
Las configuraciones se validan al cargar:

```python
@dataclass
class SimulationConfig:
    frequency_ghz: float

    def __post_init__(self):
        if self.frequency_ghz <= 0:
            raise ValueError("La frecuencia debe ser positiva")
```

## 3. Manejo de Errores

### Jerarquía de Excepciones
```python
class FacadeValidationError(Exception):
    """Errores específicos de la capa de aplicación"""
    pass
```

### Mensajes de Error Informativos
```python
raise ValueError(
    f"El parámetro '{param_name}' = {value}{unit} está fuera del rango "
    f"realista: [{min_limit}{unit}, {max_limit}{unit}]"
)
```

**Características:**
- Incluyen contexto: qué falló y por qué
- Sugieren soluciones cuando es posible
- Valores actuales vs esperados

## 4. Testing

### Cobertura Completa
- **103 tests** cubriendo todos los módulos
- Tests unitarios para cada función pública
- Tests de integración para flujos completos

### Organización de Tests
```
tests/
├── core/           # Tests de lógica de negocio
├── infrastructure/ # Tests de servicios
└── app/            # Tests de facade
```

### Configuración de Pytest
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
filterwarnings = [
    "error",  # Convertir warnings en errores
    "ignore::DeprecationWarning:pymoo.*",  # Excepto librerías externas
]
```

## 5. Gestión de Warnings

### Supresión Selectiva
Solo suprimimos warnings de librerías externas que no podemos controlar:

```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pymoo.*")
```

**Política:**
- Nuestro código debe estar libre de warnings
- Warnings de librerías externas se suprimen de forma controlada
- Todos los demás warnings se convierten en errores

## 6. Configuración Centralizada

### Archivo TOML
Toda la configuración está en `config.toml`:
- Constantes físicas
- Parámetros de simulación
- Configuración de algoritmos
- Límites realistas

### Singleton Pattern
```python
_config: Optional[AppConfig] = None

def get_config() -> AppConfig:
    global _config
    if _config is None:
        _config = ConfigLoader.load()
    return _config
```

**Beneficios:**
- Una única fuente de verdad
- Fácil de modificar sin tocar código
- Carga lazy para mejor rendimiento

## 7. Documentación

### Docstrings Completos
Todas las funciones públicas tienen docstrings que incluyen:
- Descripción clara
- Args con tipos y unidades
- Returns con tipo y descripción
- Raises con condiciones de error
- Examples cuando es apropiado

```python
def calculate_gain(
    diameter: Union[float, np.ndarray],
    frequency_ghz: Union[float, np.ndarray],
    aperture_efficiency: Union[float, np.ndarray],
) -> Union[float, np.ndarray]:
    """
    Calcula la ganancia teórica de una antena parabólica.

    Args:
        diameter: Diámetro de la antena en metros (m).
        frequency_ghz: Frecuencia de operación en gigahertz (GHz).
        aperture_efficiency: Eficiencia de apertura (η_ap), 0-1.

    Returns:
        Ganancia en decibelios isótropos (dBi).

    Raises:
        ValueError: Si los parámetros no son físicamente válidos.

    Examples:
        >>> calculate_gain(1.0, 10.0, 0.65)
        38.54
    """
```

## 8. Convenciones de Código

### Nombres Descriptivos
- Variables: `optimal_diameter_mm` (incluye unidades)
- Funciones: `calculate_gain` (verbos para acciones)
- Clases: `OptimizationEngine` (sustantivos)
- Constantes: `SPEED_OF_LIGHT` (UPPERCASE)

### Tipos Explícitos
```python
from typing import Union, Optional, List, Dict, Any

def process_data(
    input_data: Dict[str, Any]
) -> Optional[List[float]]:
    ...
```

### Formateo
- **Black** para formateo automático
- **Ruff** para linting
- Límite de 88 caracteres por línea (Black default)

## 9. Versionado y Dependencias

### Requirements Mínimos
```txt
numpy>=2.0
scipy>=1.16
pymoo>=0.6
matplotlib>=3.0
```

### Compatibilidad
- Python 3.11+ (usando `tomllib`)
- Fallback a `tomli` para versiones anteriores

## 10. Flujo de Desarrollo

### Antes de Commit
1. Ejecutar tests: `pytest`
2. Verificar formato: `black --check src/`
3. Linting: `ruff check src/`
4. Cobertura: `pytest --cov=src`

### Integración Continua (Futuro)
- Tests automáticos en cada push
- Verificación de cobertura mínima (80%)
- Verificación de estilo de código

## 11. Seguridad

### Validación de Entrada
- Nunca confiar en datos de usuario
- Validar rangos y tipos
- Conversión explícita de tipos

### Límites Realistas
Todos los parámetros tienen límites basados en física real:
```python
REALISTIC_LIMITS = {
    "min_diameter_m": 0.05,  # 5 cm: mínimo práctico
    "max_diameter_m": 3.0,   # 3 m: máximo para UAV
}
```

## 12. Performance

### Vectorización
Usar NumPy para operaciones vectorizadas:
```python
# Bueno: Vectorizado
gains = calculate_gain(diameters, frequencies, efficiencies)

# Malo: Loop
gains = [calculate_gain(d, f, e) for d, f, e in zip(...)]
```

### Lazy Loading
- Configuración cargada solo cuando se necesita
- Singleton para evitar recargas

## Conclusión

Estas prácticas garantizan que el código sea:
- ✓ **Robusto**: Validaciones en todos los niveles
- ✓ **Mantenible**: Código limpio y bien documentado
- ✓ **Testeable**: Alta cobertura de tests
- ✓ **Extensible**: Arquitectura modular
- ✓ **Profesional**: Sigue estándares de la industria
