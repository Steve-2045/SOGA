"""
Módulo de fachada de aplicación.

Proporciona una API simplificada que desacopla la interfaz de usuario de la lógica
de negocio del motor de optimización. Traduce parámetros de usuario de alto nivel a
restricciones físicas del dominio.
"""

from typing import Any, Dict

from soga.core.models import OptimizationConstraints, OptimizationResult
from soga.core.optimization import OptimizationEngine
from soga.core.physics import validate_range_feasibility
from soga.infrastructure.config import get_config

# Cargar configuración
_config = get_config()

# Límites realistas cargados desde config.toml
REALISTIC_LIMITS = {
    "min_diameter_m": _config.realistic_limits.min_diameter_m,
    "max_diameter_m": _config.realistic_limits.max_diameter_m,
    "min_payload_g": _config.realistic_limits.min_payload_g,
    "max_payload_g": _config.realistic_limits.max_payload_g,
    "min_f_d_ratio": _config.realistic_limits.min_f_d_ratio,
    "max_f_d_ratio": _config.realistic_limits.max_f_d_ratio,
    "min_range_km": _config.realistic_limits.min_range_km,
    "max_range_km": _config.realistic_limits.max_range_km,
}

# Valores por defecto cargados desde config.toml
DEFAULT_USER_PARAMS: Dict[str, float] = {
    "min_diameter_m": _config.user_defaults.min_diameter_m,
    "max_diameter_m": _config.user_defaults.max_diameter_m,
    "max_payload_g": _config.user_defaults.max_payload_g,
    "min_f_d_ratio": _config.user_defaults.min_f_d_ratio,
    "max_f_d_ratio": _config.user_defaults.max_f_d_ratio,
    "desired_range_km": _config.user_defaults.desired_range_km,
}


class FacadeValidationError(Exception):
    """
    Excepción para errores de validación en la capa de fachada.

    Se lanza cuando los parámetros de usuario no pueden ser traducidos
    a restricciones válidas del dominio.
    """

    pass


class ApplicationFacade:
    """
    Fachada de aplicación que desacopla la interfaz de usuario del motor de optimización.

    Responsabilidades:
    - Traducir parámetros de usuario (alto nivel) a restricciones del dominio
    - Ejecutar el motor de optimización
    - Formatear resultados para la presentación

    Siguiendo el principio KISS, esta clase mantiene la lógica simple
    y delega la complejidad al módulo core.
    """

    def __init__(self, engine: OptimizationEngine = None):
        """
        Inicializa la fachada de aplicación.

        Args:
            engine: Motor de optimización a utilizar. Si es None, se crea uno
                    con parámetros por defecto.

        Raises:
            TypeError: Si engine no es None y no tiene un método 'run' callable.
        """
        if engine is None:
            self._engine = OptimizationEngine()
        elif hasattr(engine, 'run') and callable(getattr(engine, 'run')):
            self._engine = engine
        else:
            raise TypeError(
                f"El parámetro 'engine' debe tener un método 'run' callable, "
                f"pero se recibió: {type(engine).__name__}"
            )

    def run_optimization(self, user_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el flujo completo de optimización.

        Proceso:
        1. Traduce parámetros de usuario a restricciones del dominio
        2. Ejecuta el motor de optimización
        3. Formatea resultados para presentación

        Args:
            user_parameters: Diccionario con parámetros del usuario. Claves esperadas:
                - min_diameter_m: float (metros)
                - max_diameter_m: float (metros)
                - max_payload_g: float (gramos)
                - min_f_d_ratio: float (adimensional)
                - max_f_d_ratio: float (adimensional)
                - desired_range_km: float (kilómetros)

        Returns:
            Diccionario con resultados listos para presentación:
                - optimal_diameter_mm: float
                - optimal_focal_length_mm: float
                - optimal_depth_mm: float
                - f_d_ratio: float
                - expected_gain_dbi: float
                - beamwidth_deg: float
                - convergence: List[float]

        Raises:
            FacadeValidationError: Si los parámetros son inválidos o inconsistentes.

        Examples:
            >>> facade = ApplicationFacade()
            >>> params = {"min_diameter_m": 0.2, "max_diameter_m": 1.5}
            >>> result = facade.run_optimization(params)
        """
        # 1. Traducir parámetros de usuario a restricciones del dominio
        try:
            constraints = self._build_constraints(user_parameters)
        except (KeyError, TypeError, ValueError) as e:
            raise FacadeValidationError(f"Error al construir restricciones: {e}") from e

        # 2. Ejecutar optimización
        try:
            result: OptimizationResult = self._engine.run(constraints)
        except RuntimeError as e:
            raise FacadeValidationError(f"Error durante la optimización: {e}") from e

        # 3. Formatear resultado para presentación
        output = self._format_output(result)

        return output

    def _build_constraints(
        self, user_parameters: Dict[str, Any]
    ) -> OptimizationConstraints:
        """
        Construye objeto de restricciones a partir de parámetros de usuario.

        Aplica valores por defecto, valida rangos realistas y realiza conversiones de unidades.

        Args:
            user_parameters: Parámetros proporcionados por el usuario.

        Returns:
            OptimizationConstraints validado.

        Raises:
            ValueError: Si los parámetros resultan en restricciones inválidas.
            TypeError: Si los parámetros no son del tipo esperado.
        """
        # Función auxiliar para validar y convertir parámetros
        def _validate_and_convert(
            param_name: str,
            default_value: float,
            min_limit: float,
            max_limit: float,
            unit: str = ""
        ) -> float:
            """Valida tipo, convierte a float y verifica rangos realistas."""
            raw_value = user_parameters.get(param_name, default_value)

            # Validar que no sea None
            if raw_value is None:
                raise ValueError(
                    f"El parámetro '{param_name}' no puede ser None. "
                    f"Use un valor numérico o omítalo para usar el valor por defecto."
                )

            # Intentar convertir a float con mensaje de error claro
            try:
                value = float(raw_value)
            except (TypeError, ValueError) as e:
                raise TypeError(
                    f"El parámetro '{param_name}' debe ser un número, "
                    f"pero recibió: {type(raw_value).__name__} = {raw_value}"
                ) from e

            # Validar rango realista
            if value < min_limit or value > max_limit:
                raise ValueError(
                    f"El parámetro '{param_name}' = {value}{unit} está fuera del rango "
                    f"realista para aplicaciones de drones: [{min_limit}{unit}, {max_limit}{unit}]. "
                    f"Este límite garantiza fabricabilidad y operación práctica."
                )

            return value

        # Validar y obtener todos los parámetros con sus límites realistas
        min_diameter = _validate_and_convert(
            "min_diameter_m",
            DEFAULT_USER_PARAMS["min_diameter_m"],
            REALISTIC_LIMITS["min_diameter_m"],
            REALISTIC_LIMITS["max_diameter_m"],
            "m"
        )

        max_diameter = _validate_and_convert(
            "max_diameter_m",
            DEFAULT_USER_PARAMS["max_diameter_m"],
            REALISTIC_LIMITS["min_diameter_m"],
            REALISTIC_LIMITS["max_diameter_m"],
            "m"
        )

        max_payload_g = _validate_and_convert(
            "max_payload_g",
            DEFAULT_USER_PARAMS["max_payload_g"],
            REALISTIC_LIMITS["min_payload_g"],
            REALISTIC_LIMITS["max_payload_g"],
            "g"
        )

        min_f_d_ratio = _validate_and_convert(
            "min_f_d_ratio",
            DEFAULT_USER_PARAMS["min_f_d_ratio"],
            REALISTIC_LIMITS["min_f_d_ratio"],
            REALISTIC_LIMITS["max_f_d_ratio"],
            ""
        )

        max_f_d_ratio = _validate_and_convert(
            "max_f_d_ratio",
            DEFAULT_USER_PARAMS["max_f_d_ratio"],
            REALISTIC_LIMITS["min_f_d_ratio"],
            REALISTIC_LIMITS["max_f_d_ratio"],
            ""
        )

        desired_range_km = _validate_and_convert(
            "desired_range_km",
            DEFAULT_USER_PARAMS["desired_range_km"],
            REALISTIC_LIMITS["min_range_km"],
            REALISTIC_LIMITS["max_range_km"],
            "km"
        )

        # Validar consistencia de rangos min/max ANTES de crear restricciones
        if min_diameter >= max_diameter:
            raise ValueError(
                f"El diámetro mínimo ({min_diameter}m) debe ser menor que "
                f"el diámetro máximo ({max_diameter}m). "
                f"Verifique los parámetros 'min_diameter_m' y 'max_diameter_m'."
            )

        if min_f_d_ratio >= max_f_d_ratio:
            raise ValueError(
                f"La relación f/D mínima ({min_f_d_ratio}) debe ser menor que "
                f"la relación f/D máxima ({max_f_d_ratio}). "
                f"Verifique los parámetros 'min_f_d_ratio' y 'max_f_d_ratio'."
            )

        # Convertir unidades: gramos → kilogramos
        max_weight_kg = max_payload_g / 1000.0

        # Construir restricciones (validación adicional ocurre en __post_init__)
        constraints = OptimizationConstraints(
            min_diameter=min_diameter,
            max_diameter=max_diameter,
            max_weight=max_weight_kg,
            min_f_d_ratio=min_f_d_ratio,
            max_f_d_ratio=max_f_d_ratio,
            desired_range_km=desired_range_km,
        )

        # Validar viabilidad del link budget (física de comunicaciones RF)
        # Verifica que el alcance deseado sea físicamente alcanzable con
        # las restricciones de tamaño de antena dadas
        is_feasible, error_message, link_result = validate_range_feasibility(
            min_antenna_diameter_m=min_diameter,
            max_antenna_diameter_m=max_diameter,
            desired_range_km=desired_range_km,
            frequency_ghz=_config.simulation.frequency_ghz,
            antenna_efficiency=_config.simulation.aperture_efficiency,
            tx_power_dbm=_config.link_budget.tx_power_dbm,
            rx_sensitivity_dbm=_config.link_budget.rx_sensitivity_dbm,
            required_snr_db=_config.link_budget.required_snr_db,
            fade_margin_db=_config.link_budget.fade_margin_db,
            implementation_loss_db=_config.link_budget.implementation_loss_db,
            min_link_margin_db=_config.link_budget.min_link_margin_db,
        )

        if not is_feasible:
            raise FacadeValidationError(
                f"Restricciones físicamente incompatibles:\n\n{error_message}"
            )

        return constraints

    def _format_output(self, result: OptimizationResult) -> Dict[str, Any]:
        """
        Formatea el resultado de optimización para presentación.

        Convierte unidades de metros a milímetros y redondea a precisiones
        apropiadas para fabricación.

        Args:
            result: Resultado de la optimización.

        Returns:
            Diccionario con valores formateados para presentación.

        Raises:
            ValueError: Si el resultado de optimización está incompleto o es inválido.

        Note:
            Precisiones de redondeo:
            - Dimensiones (mm): 2 decimales (0.01 mm = 10 μm, precisión de fabricación)
            - Relación f/D: 3 decimales (suficiente para reproducibilidad)
            - Ganancia (dBi): 2 decimales (precisión típica de mediciones)
            - Ancho de haz (°): 2 decimales (precisión angular adecuada)
        """
        # Validar que el resultado tenga todos los componentes necesarios
        if result.optimal_geometry is None:
            raise ValueError("El resultado de optimización no contiene geometría óptima")
        if result.performance_metrics is None:
            raise ValueError("El resultado de optimización no contiene métricas de rendimiento")

        return {
            # Dimensiones en mm con precisión de 0.01 mm (10 micrones)
            "optimal_diameter_mm": round(result.optimal_geometry.diameter * 1000, 2),
            "optimal_focal_length_mm": round(result.optimal_geometry.focal_length * 1000, 2),
            "optimal_depth_mm": round(result.optimal_geometry.depth * 1000, 2),

            # Relación adimensional con 3 decimales
            "f_d_ratio": round(result.optimal_geometry.f_d_ratio, 3),

            # Métricas de rendimiento con precisión apropiada
            "expected_gain_dbi": round(result.performance_metrics.gain, 2),
            "beamwidth_deg": round(result.performance_metrics.beamwidth, 2),

            # Historial de convergencia (mantener precisión completa para análisis)
            "convergence": result.convergence_history,
        }
