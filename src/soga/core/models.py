from dataclasses import dataclass, field
from typing import List, Optional

# Límites físicos para relación focal según literatura
MIN_F_D_RATIO = 0.2  # Límite práctico inferior (parábolas muy profundas)
MAX_F_D_RATIO = 1.5  # Límite práctico superior (parábolas muy planas)


@dataclass
class AntennaGeometry:
    """
    Representa la geometría física de una antena parabólica.

    Attributes:
        diameter (float): Diámetro del reflector principal en metros (m).
        focal_length (float): Distancia desde el vértice al punto focal en metros (m).

    Raises:
        ValueError: Si los parámetros no son físicamente válidos.

    Note:
        La relación f/D debe estar entre 0.2 y 1.5 para ser práctica.
        Valores fuera de este rango son matemáticamente válidos pero
        físicamente ineficientes o impracticables.
    """

    diameter: float
    focal_length: float

    def __post_init__(self):
        """Valida que los parámetros sean físicamente válidos."""
        if self.diameter <= 0:
            raise ValueError(
                f"El diámetro debe ser positivo, recibido: {self.diameter}"
            )
        if self.focal_length <= 0:
            raise ValueError(
                f"La distancia focal debe ser positiva, recibido: {self.focal_length}"
            )

        # Validar que la relación f/D esté en un rango práctico
        f_d = self.f_d_ratio
        if f_d < MIN_F_D_RATIO:
            raise ValueError(
                f"La relación f/D ({f_d:.3f}) es demasiado baja. "
                f"Mínimo práctico: {MIN_F_D_RATIO} (parábola demasiado profunda)"
            )
        if f_d > MAX_F_D_RATIO:
            raise ValueError(
                f"La relación f/D ({f_d:.3f}) es demasiado alta. "
                f"Máximo práctico: {MAX_F_D_RATIO} (parábola demasiado plana)"
            )

    @property
    def depth(self) -> float:
        """Calcula la profundidad de la antena parabólica en metros (m)."""
        return self.diameter**2 / (16 * self.focal_length)

    @property
    def f_d_ratio(self) -> float:
        """Calcula la relación focal adimensional (f/D)."""
        return self.focal_length / self.diameter


@dataclass
class PerformanceMetrics:
    """
    Representa las métricas de rendimiento clave de una antena.

    Attributes:
        gain (float): Ganancia de la antena en decibelios isótropos (dBi).
        beamwidth (float): Ancho de haz a -3dB en grados (°).

    Raises:
        ValueError: Si los parámetros no son físicamente válidos.
    """

    gain: float
    beamwidth: float

    def __post_init__(self):
        """Valida que las métricas sean físicamente válidas."""
        if self.beamwidth <= 0 or self.beamwidth > 180:
            raise ValueError(
                f"El ancho de haz debe estar entre 0 y 180 grados, recibido: {self.beamwidth}"
            )


@dataclass
class OptimizationConstraints:
    """
    Encapsula todos los requisitos y límites para un problema de optimización.

    Attributes:
        min_diameter (float): Límite inferior para el diámetro de la antena en metros (m).
        max_diameter (float): Límite superior para el diámetro de la antena en metros (m).
        max_weight (float): Límite superior para el peso de la antena en kilogramos (kg).
        min_f_d_ratio (float): Límite inferior para la relación focal (adimensional).
        max_f_d_ratio (float): Límite superior para la relación focal (adimensional).
        desired_range_km (float): Alcance de comunicación deseado en kilómetros (km).
            NOTA: Actualmente este parámetro es INFORMATIVO/REFERENCIAL.
            No se usa como restricción en la optimización porque el alcance depende
            del sistema completo (potencia TX, sensibilidad RX, pérdidas), no solo
            de la geometría de la antena. Reservado para futuras implementaciones
            de link budget completo.

    Raises:
        ValueError: Si las restricciones no son físicamente válidas o son inconsistentes.
    """

    min_diameter: float
    max_diameter: float
    max_weight: float
    min_f_d_ratio: float
    max_f_d_ratio: float
    desired_range_km: float

    def __post_init__(self):
        """Valida que las restricciones sean físicamente válidas y consistentes."""
        if self.min_diameter <= 0:
            raise ValueError(
                f"min_diameter debe ser positivo, recibido: {self.min_diameter}"
            )
        if self.max_diameter <= 0:
            raise ValueError(
                f"max_diameter debe ser positivo, recibido: {self.max_diameter}"
            )
        if self.min_diameter >= self.max_diameter:
            raise ValueError(
                f"min_diameter ({self.min_diameter}) debe ser menor que "
                f"max_diameter ({self.max_diameter})"
            )
        if self.max_weight <= 0:
            raise ValueError(
                f"max_weight debe ser positivo, recibido: {self.max_weight}"
            )
        if self.min_f_d_ratio <= 0:
            raise ValueError(
                f"min_f_d_ratio debe ser positivo, recibido: {self.min_f_d_ratio}"
            )
        if self.max_f_d_ratio <= 0:
            raise ValueError(
                f"max_f_d_ratio debe ser positivo, recibido: {self.max_f_d_ratio}"
            )
        if self.min_f_d_ratio >= self.max_f_d_ratio:
            raise ValueError(
                f"min_f_d_ratio ({self.min_f_d_ratio}) debe ser menor que "
                f"max_f_d_ratio ({self.max_f_d_ratio})"
            )
        if self.desired_range_km <= 0:
            raise ValueError(
                f"desired_range_km debe ser positivo, recibido: {self.desired_range_km}"
            )


@dataclass
class OptimizationResult:
    """
    Contiene el resultado de un proceso de optimización.

    Attributes:
        optimal_geometry (AntennaGeometry): La geometría óptima encontrada.
        performance_metrics (PerformanceMetrics): Las métricas de rendimiento calculadas
            para la geometría óptima.
        convergence_history (Optional[List[float]]): Una lista que registra la evolución
            de la mejor solución a lo largo de las generaciones del optimizador.
    """

    optimal_geometry: AntennaGeometry
    performance_metrics: PerformanceMetrics
    convergence_history: Optional[List[float]] = field(default_factory=list)
