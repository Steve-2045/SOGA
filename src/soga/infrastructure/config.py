"""
Módulo de gestión de configuración.

Proporciona acceso centralizado a la configuración de la aplicación
cargada desde archivos TOML.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # Fallback para Python < 3.11


@dataclass
class PhysicsConfig:
    """Configuración de constantes físicas."""

    speed_of_light: float

    def __post_init__(self):
        """Valida que las constantes físicas sean correctas."""
        if self.speed_of_light <= 0:
            raise ValueError(
                f"La velocidad de la luz debe ser positiva, recibido: {self.speed_of_light}"
            )


@dataclass
class SimulationConfig:
    """Configuración de parámetros de simulación."""

    frequency_ghz: float
    aperture_efficiency: float
    beamwidth_k_factor: float
    reflector_areal_density_kg_per_m2: float
    fixed_component_weight_kg: float
    efficiency_peak: float
    optimal_f_d_ratio: float
    curvature_low_fd: float
    curvature_high_fd: float

    def __post_init__(self):
        """Valida que los parámetros de simulación sean correctos."""
        if self.frequency_ghz <= 0:
            raise ValueError(
                f"La frecuencia debe ser positiva, recibido: {self.frequency_ghz}"
            )
        if not 0 < self.aperture_efficiency <= 1:
            raise ValueError(
                f"La eficiencia de apertura debe estar entre 0 y 1, recibido: {self.aperture_efficiency}"
            )
        if self.beamwidth_k_factor <= 0:
            raise ValueError(
                f"El factor K debe ser positivo, recibido: {self.beamwidth_k_factor}"
            )
        if self.reflector_areal_density_kg_per_m2 <= 0:
            raise ValueError(
                f"La densidad areal del reflector debe ser positiva, recibido: {self.reflector_areal_density_kg_per_m2}"
            )
        if self.fixed_component_weight_kg < 0:
            raise ValueError(
                f"El peso fijo de componentes debe ser no negativo, recibido: {self.fixed_component_weight_kg}"
            )
        if not 0 < self.efficiency_peak <= 1:
            raise ValueError(
                f"La eficiencia pico debe estar entre 0 y 1, recibido: {self.efficiency_peak}"
            )
        if not 0 < self.optimal_f_d_ratio <= 2:
            raise ValueError(
                f"La relación f/D óptima debe estar entre 0 y 2, recibido: {self.optimal_f_d_ratio}"
            )
        if self.curvature_low_fd < 0:
            raise ValueError(
                f"La curvatura baja debe ser no negativa, recibido: {self.curvature_low_fd}"
            )
        if self.curvature_high_fd < 0:
            raise ValueError(
                f"La curvatura alta debe ser no negativa, recibido: {self.curvature_high_fd}"
            )


@dataclass
class OptimizationConfig:
    """Configuración del algoritmo de optimización."""

    population_size: int
    max_generations: int
    seed: int

    def __post_init__(self):
        """Valida que los parámetros de optimización sean correctos."""
        if self.population_size <= 0:
            raise ValueError(
                f"El tamaño de población debe ser positivo, recibido: {self.population_size}"
            )
        if self.max_generations <= 0:
            raise ValueError(
                f"El número de generaciones debe ser positivo, recibido: {self.max_generations}"
            )
        if self.seed < 0:
            raise ValueError(f"La semilla debe ser no negativa, recibido: {self.seed}")


@dataclass
class UserDefaultsConfig:
    """Valores por defecto para parámetros de usuario."""

    min_diameter_m: float
    max_diameter_m: float
    max_payload_g: float
    min_f_d_ratio: float
    max_f_d_ratio: float
    desired_range_km: float


@dataclass
class LinkBudgetConfig:
    """Parámetros de link budget para validación de comunicación."""

    tx_power_dbm: float
    rx_sensitivity_dbm: float
    rx_noise_figure_db: float
    required_snr_db: float
    fade_margin_db: float
    implementation_loss_db: float
    min_link_margin_db: float

    def __post_init__(self):
        """Valida que los parámetros de link budget sean correctos."""
        if self.tx_power_dbm < -100 or self.tx_power_dbm > 60:
            raise ValueError(
                f"Potencia TX fuera de rango realista [-100, 60] dBm: {self.tx_power_dbm}"
            )
        if self.rx_sensitivity_dbm > -20 or self.rx_sensitivity_dbm < -150:
            raise ValueError(
                f"Sensibilidad RX fuera de rango realista [-150, -20] dBm: {self.rx_sensitivity_dbm}"
            )
        if self.rx_noise_figure_db < 0 or self.rx_noise_figure_db > 20:
            raise ValueError(
                f"Figura de ruido fuera de rango realista [0, 20] dB: {self.rx_noise_figure_db}"
            )
        if self.required_snr_db < 0 or self.required_snr_db > 30:
            raise ValueError(
                f"SNR requerido fuera de rango realista [0, 30] dB: {self.required_snr_db}"
            )
        if self.fade_margin_db < 0 or self.fade_margin_db > 40:
            raise ValueError(
                f"Margen de fade fuera de rango realista [0, 40] dB: {self.fade_margin_db}"
            )
        if self.implementation_loss_db < 0 or self.implementation_loss_db > 20:
            raise ValueError(
                f"Pérdidas de implementación fuera de rango [0, 20] dB: {self.implementation_loss_db}"
            )
        if self.min_link_margin_db < 0 or self.min_link_margin_db > 20:
            raise ValueError(
                f"Margen mínimo de link fuera de rango [0, 20] dB: {self.min_link_margin_db}"
            )


@dataclass
class RegulatoryConfig:
    """Límites regulatorios."""

    max_eirp_dbm: float


@dataclass
class RealisticLimitsConfig:
    """Límites realistas para antenas parabólicas de 2.4 GHz."""

    min_diameter_m: float
    max_diameter_m: float
    min_payload_g: float
    max_payload_g: float
    min_f_d_ratio: float
    max_f_d_ratio: float
    min_range_km: float
    max_range_km: float


@dataclass
class AppConfig:
    """Configuración completa de la aplicación."""

    physics: PhysicsConfig
    simulation: SimulationConfig
    optimization: OptimizationConfig
    user_defaults: UserDefaultsConfig
    link_budget: LinkBudgetConfig
    regulatory: RegulatoryConfig
    realistic_limits: RealisticLimitsConfig


class ConfigLoader:
    """
    Cargador de configuración desde archivos TOML.

    Sigue el principio UNIX: hace una cosa (cargar config) y la hace bien.
    """

    DEFAULT_CONFIG_FILENAME = "config.toml"

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> AppConfig:
        """
        Carga la configuración desde un archivo TOML.

        Args:
            config_path: Ruta al archivo de configuración. Si es None,
                        busca config.toml en el directorio raíz del proyecto.

        Returns:
            AppConfig con toda la configuración cargada.

        Raises:
            FileNotFoundError: Si el archivo de configuración no existe.
            ValueError: Si el archivo de configuración es inválido.

        Examples:
            >>> config = ConfigLoader.load()
            >>> print(config.simulation.frequency_ghz)
            2.4
        """
        # Determinar la ruta del archivo de configuración
        if config_path is None:
            config_path = cls._find_default_config()

        if not config_path.exists():
            raise FileNotFoundError(
                f"Archivo de configuración no encontrado: {config_path}"
            )

        # Cargar el archivo TOML
        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
        except Exception as e:
            raise ValueError(f"Error al leer el archivo de configuración: {e}") from e

        # Construir y validar la configuración
        try:
            config = cls._build_config(data)
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Configuración inválida en {config_path}: {e}") from e

        return config

    @classmethod
    def _find_default_config(cls) -> Path:
        """
        Encuentra el archivo de configuración por defecto.

        Busca config.toml en el directorio raíz del proyecto
        (dos niveles arriba desde este archivo).

        Returns:
            Path al archivo config.toml.
        """
        # Ubicación de este archivo: src/soga/infrastructure/config.py
        # Directorio raíz: ../../../
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        config_path = project_root / cls.DEFAULT_CONFIG_FILENAME
        return config_path

    @classmethod
    def _build_config(cls, data: dict) -> AppConfig:
        """
        Construye el objeto AppConfig desde los datos del TOML.

        Args:
            data: Diccionario con los datos cargados del TOML.

        Returns:
            AppConfig validado.

        Raises:
            KeyError: Si faltan secciones o claves requeridas.
            TypeError: Si los tipos de datos son incorrectos.
        """
        physics = PhysicsConfig(speed_of_light=data["physics"]["speed_of_light"])

        simulation = SimulationConfig(
            frequency_ghz=data["simulation"]["frequency_ghz"],
            aperture_efficiency=data["simulation"]["aperture_efficiency"],
            beamwidth_k_factor=data["simulation"]["beamwidth_k_factor"],
            reflector_areal_density_kg_per_m2=data["simulation"]["reflector_areal_density_kg_per_m2"],
            fixed_component_weight_kg=data["simulation"]["fixed_component_weight_kg"],
            efficiency_peak=data["simulation"]["efficiency_peak"],
            optimal_f_d_ratio=data["simulation"]["optimal_f_d_ratio"],
            curvature_low_fd=data["simulation"]["curvature_low_fd"],
            curvature_high_fd=data["simulation"]["curvature_high_fd"],
        )

        optimization = OptimizationConfig(
            population_size=data["optimization"]["population_size"],
            max_generations=data["optimization"]["max_generations"],
            seed=data["optimization"]["seed"],
        )

        user_defaults = UserDefaultsConfig(
            min_diameter_m=data["user_defaults"]["min_diameter_m"],
            max_diameter_m=data["user_defaults"]["max_diameter_m"],
            max_payload_g=data["user_defaults"]["max_payload_g"],
            min_f_d_ratio=data["user_defaults"]["min_f_d_ratio"],
            max_f_d_ratio=data["user_defaults"]["max_f_d_ratio"],
            desired_range_km=data["user_defaults"]["desired_range_km"],
        )

        link_budget = LinkBudgetConfig(
            tx_power_dbm=data["link_budget"]["tx_power_dbm"],
            rx_sensitivity_dbm=data["link_budget"]["rx_sensitivity_dbm"],
            rx_noise_figure_db=data["link_budget"]["rx_noise_figure_db"],
            required_snr_db=data["link_budget"]["required_snr_db"],
            fade_margin_db=data["link_budget"]["fade_margin_db"],
            implementation_loss_db=data["link_budget"]["implementation_loss_db"],
            min_link_margin_db=data["link_budget"]["min_link_margin_db"],
        )

        regulatory = RegulatoryConfig(max_eirp_dbm=data["regulatory"]["max_eirp_dbm"])

        realistic_limits = RealisticLimitsConfig(
            min_diameter_m=data["realistic_limits"]["min_diameter_m"],
            max_diameter_m=data["realistic_limits"]["max_diameter_m"],
            min_payload_g=data["realistic_limits"]["min_payload_g"],
            max_payload_g=data["realistic_limits"]["max_payload_g"],
            min_f_d_ratio=data["realistic_limits"]["min_f_d_ratio"],
            max_f_d_ratio=data["realistic_limits"]["max_f_d_ratio"],
            min_range_km=data["realistic_limits"]["min_range_km"],
            max_range_km=data["realistic_limits"]["max_range_km"],
        )

        return AppConfig(
            physics=physics,
            simulation=simulation,
            optimization=optimization,
            user_defaults=user_defaults,
            link_budget=link_budget,
            regulatory=regulatory,
            realistic_limits=realistic_limits,
        )


# Instancia global de configuración (singleton lazy)
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """
    Obtiene la configuración de la aplicación.

    Implementa un patrón singleton lazy: carga la configuración
    la primera vez que se llama y la cachea para llamadas subsiguientes.

    Returns:
        AppConfig con la configuración cargada.

    Examples:
        >>> config = get_config()
        >>> freq = config.simulation.frequency_ghz
    """
    global _config
    if _config is None:
        _config = ConfigLoader.load()
    return _config


def reload_config(config_path: Optional[Path] = None) -> AppConfig:
    """
    Recarga la configuración desde el archivo.

    Útil para tests o para cambios de configuración en tiempo de ejecución.

    Args:
        config_path: Ruta opcional al archivo de configuración.

    Returns:
        AppConfig recargada.
    """
    global _config
    _config = ConfigLoader.load(config_path)
    return _config
