"""
Módulo de optimización multiobjetivo para diseño de antenas parabólicas.

Implementa el motor de optimización usando NSGA-II para encontrar la geometría
óptima de antenas considerando múltiples objetivos y restricciones.
"""

import warnings
import numpy as np
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

# Suprimir warnings de deprecación de librerías externas
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pymoo.*")

from soga.core.models import (
    AntennaGeometry,
    OptimizationConstraints,
    OptimizationResult,
    PerformanceMetrics,
)
from soga.core.physics import calculate_gain, calculate_beamwidth
from soga.infrastructure.config import get_config

# Cargar configuración
_config = get_config()

# --- Constantes de simulación cargadas desde config.toml ---
SIM_FREQUENCY_GHZ = _config.simulation.frequency_ghz
SIM_AREAL_DENSITY_KG_PER_M2 = _config.simulation.areal_density_kg_per_m2
EFFICIENCY_PEAK = _config.simulation.efficiency_peak
OPTIMAL_F_D_RATIO = _config.simulation.optimal_f_d_ratio
CURVATURE_LOW_FD = _config.simulation.curvature_low_fd
CURVATURE_HIGH_FD = _config.simulation.curvature_high_fd


def aperture_efficiency_model(f_d_ratio: np.ndarray) -> np.ndarray:
    """
    Calcula la eficiencia de apertura en función de la relación f/D.

    Modelo empírico mejorado basado en literatura que refleja el trade-off entre:
    - Spillover loss (mayor en f/D altos - pérdida más pronunciada)
    - Blockage loss (mayor en f/D bajos - pérdida más suave)

    La eficiencia es máxima alrededor de f/D ≈ 0.45 según estudios típicos
    de antenas parabólicas. El modelo usa curvaturas asimétricas para reflejar
    el comportamiento físico real donde el spillover penaliza más que el blockage.

    Args:
        f_d_ratio: Relación focal f/D (puede ser escalar o array).

    Returns:
        Eficiencia de apertura (valor entre 0.40 y 0.70).

    References:
        - Balanis, C.A. "Antenna Theory" (2016), Chapter 15
        - Kraus, J.D. "Antennas" (1988), Chapter 9
        - IEEE Std 145-2013: Definitions of Terms for Antennas

    Note:
        Modelo validado para el rango f/D ∈ [0.2, 1.5]:
        - f/D = 0.20: eff ≈ 0.68 (parábola profunda, blockage moderado)
        - f/D = 0.45: eff = 0.70 (óptimo)
        - f/D = 1.00: eff ≈ 0.55 (parábola plana, spillover significativo)
        - f/D = 1.50: eff ≈ 0.44 (parábola muy plana, spillover severo)
    """
    # Convertir a array para soportar tanto escalares como arrays
    f_d_ratio = np.asarray(f_d_ratio)

    # Modelo asimétrico: usar curvaturas diferentes antes y después del óptimo
    deviation = f_d_ratio - OPTIMAL_F_D_RATIO

    # Seleccionar curvatura según si estamos antes o después del óptimo
    curvature = np.where(
        deviation < 0,
        CURVATURE_LOW_FD,   # f/D < óptimo: pérdida suave (blockage)
        CURVATURE_HIGH_FD   # f/D > óptimo: pérdida pronunciada (spillover)
    )

    # Calcular eficiencia con modelo cuadrático asimétrico
    efficiency = EFFICIENCY_PEAK - curvature * deviation**2

    # Garantizar que permanecemos dentro del rango físico realista
    # No usar clip para detectar errores de modelado
    min_eff = 0.40  # Mínimo físicamente realista
    max_eff = 0.70  # Máximo físicamente alcanzable

    # Validar que el modelo no produce valores fuera de rango
    if np.any(efficiency < min_eff - 0.01) or np.any(efficiency > max_eff + 0.01):
        # Advertencia: el modelo necesita recalibración
        import warnings
        warnings.warn(
            f"El modelo de eficiencia produjo valores fuera del rango esperado "
            f"[{min_eff}, {max_eff}]. Esto sugiere que los parámetros del modelo "
            f"necesitan ajuste. Valores: min={np.min(efficiency):.3f}, "
            f"max={np.max(efficiency):.3f}",
            RuntimeWarning
        )

    return np.clip(efficiency, min_eff, max_eff)


class AntennaProblem(Problem):
    """
    Define el problema de optimización de antena como un problema multiobjetivo.

    Optimiza la geometría de la antena considerando dos objetivos en conflicto:
    1. Maximizar la ganancia (minimizar -ganancia)
    2. Minimizar el peso

    Sujeto a restricciones de peso máximo.
    """

    def __init__(self, constraints: OptimizationConstraints):
        """
        Inicializa el problema de optimización.

        Args:
            constraints: Restricciones y límites del problema.
        """
        self.constraints = constraints

        # Definir el espacio de búsqueda
        # Variables: [diámetro (m), relación f/D (adimensional)]
        # Objetivos: [ganancia (negativa), peso]
        # Restricciones: [violación de peso máximo]
        super().__init__(
            n_var=2,
            n_obj=2,
            n_constr=1,
            xl=np.array([constraints.min_diameter, constraints.min_f_d_ratio]),
            xu=np.array([constraints.max_diameter, constraints.max_f_d_ratio]),
        )

    def _evaluate(self, x, out, *args, **kwargs):
        """
        Evalúa la función de fitness para un lote de soluciones candidatas.

        Args:
            x: Array de NumPy donde cada fila es [diámetro, f_d_ratio].
            out: Diccionario para almacenar objetivos (F) y restricciones (G).
        """
        # Extraer variables de diseño
        diameters = x[:, 0]
        f_d_ratios = x[:, 1]

        # Calcular eficiencia de apertura en función de f/D
        aperture_efficiencies = aperture_efficiency_model(f_d_ratios)

        # --- Objetivo 1: Maximizar ganancia (minimizar -ganancia) ---
        gains = calculate_gain(
            diameter=diameters,
            frequency_ghz=SIM_FREQUENCY_GHZ,
            aperture_efficiency=aperture_efficiencies,
        )
        f1 = -gains  # Negativo porque pymoo minimiza

        # --- Objetivo 2: Minimizar peso ---
        # Optimización: precalcular constante π * densidad / 4
        # peso = π * (D/2)² * densidad = (π/4) * D² * densidad
        WEIGHT_FACTOR = np.pi * SIM_AREAL_DENSITY_KG_PER_M2 / 4.0
        weights = WEIGHT_FACTOR * diameters**2
        f2 = weights

        # --- Restricción: peso <= max_weight ---
        # Formulada como g(x) <= 0 según convención de pymoo
        g1 = weights - self.constraints.max_weight

        # Asignar resultados
        out["F"] = np.column_stack([f1, f2])
        out["G"] = np.column_stack([g1])


class OptimizationEngine:
    """
    Motor de optimización multiobjetivo para diseño de antenas.

    Utiliza el algoritmo genético NSGA-II para encontrar el frente de Pareto
    de geometrías óptimas que balancean ganancia y peso.
    """

    def __init__(
        self,
        population_size: int = None,
        max_generations: int = None,
        seed: int = None
    ):
        """
        Inicializa el motor de optimización.

        Args:
            population_size: Tamaño de la población del algoritmo genético.
                Si es None, usa el valor de config.toml.
            max_generations: Número máximo de generaciones.
                Si es None, usa el valor de config.toml.
            seed: Semilla para reproducibilidad.
                Si es None, usa el valor de config.toml.
        """
        # Cargar valores por defecto desde configuración si no se especifican
        self.population_size = (
            population_size if population_size is not None
            else _config.optimization.population_size
        )
        self.max_generations = (
            max_generations if max_generations is not None
            else _config.optimization.max_generations
        )
        self.seed = (
            seed if seed is not None
            else _config.optimization.seed
        )

    def _select_knee_point(self, X: np.ndarray, F: np.ndarray) -> np.ndarray:
        """
        Selecciona el "knee point" del frente de Pareto.

        El knee point es el punto donde hay el mejor balance entre los objetivos.
        Se calcula como el punto con mayor distancia perpendicular a la línea
        que une los extremos del frente de Pareto normalizado.

        Args:
            X: Array de variables de decisión (soluciones)
            F: Array de valores de objetivos

        Returns:
            Variables de la solución knee point

        References:
            - Branke et al. (2004): "Finding Knees in Multi-objective Optimization"
        """
        # Si solo hay una solución, retornarla
        if len(X) == 1:
            return X[0]

        # Normalizar objetivos al rango [0, 1] para cada objetivo
        F_min = np.min(F, axis=0)
        F_max = np.max(F, axis=0)

        # Evitar división por cero si todos los valores son iguales
        F_range = F_max - F_min
        F_range[F_range == 0] = 1.0

        F_norm = (F - F_min) / F_range

        # Encontrar puntos extremos en el frente normalizado
        # Punto con mínimo f1 (mejor ganancia, peor peso)
        idx_min_f1 = np.argmin(F_norm[:, 0])
        # Punto con mínimo f2 (mejor peso, peor ganancia)
        idx_min_f2 = np.argmin(F_norm[:, 1])

        p1 = F_norm[idx_min_f1]
        p2 = F_norm[idx_min_f2]

        # Calcular distancias perpendiculares de cada punto a la línea p1-p2
        # Fórmula: d = |cross((p2-p1), (p1-point))| / ||p2-p1||
        line_vec = p2 - p1
        line_length = np.linalg.norm(line_vec)

        if line_length == 0:
            # Los extremos son el mismo punto, retornar cualquiera
            return X[0]

        # Calcular distancia perpendicular para cada punto
        distances = np.zeros(len(F_norm))
        for i, point in enumerate(F_norm):
            point_vec = p1 - point
            # Producto cruz en 2D: |a×b| = |a_x*b_y - a_y*b_x|
            cross_product = abs(line_vec[0]*point_vec[1] - line_vec[1]*point_vec[0])
            distances[i] = cross_product / line_length

        # El knee point es el que tiene máxima distancia perpendicular
        knee_idx = np.argmax(distances)

        return X[knee_idx]

    def run(self, constraints: OptimizationConstraints) -> OptimizationResult:
        """
        Ejecuta el proceso de optimización completo usando NSGA-II.

        Args:
            constraints: Restricciones del problema de optimización.

        Returns:
            OptimizationResult con la geometría óptima y métricas de rendimiento.

        Raises:
            RuntimeError: Si la optimización no encuentra una solución viable.
        """
        # Configurar el problema de optimización
        problem = AntennaProblem(constraints)

        # Configurar el algoritmo NSGA-II
        algorithm = NSGA2(pop_size=self.population_size, eliminate_duplicates=True)

        # Ejecutar la optimización
        res = minimize(
            problem,
            algorithm,
            ("n_gen", self.max_generations),
            save_history=True,
            seed=self.seed,
            verbose=False,
        )

        # Validar que se encontró al menos una solución
        if res.X is None or len(res.X) == 0:
            raise RuntimeError(
                "La optimización no encontró ninguna solución viable. "
                "Verifique las restricciones del problema."
            )

        # Seleccionar el "knee point" del frente de Pareto
        # El knee point es la solución con mejor balance ganancia/peso
        best_vars = self._select_knee_point(res.X, res.F)
        optimal_diameter, optimal_f_d_ratio = best_vars

        # Construir la geometría óptima
        optimal_geometry = AntennaGeometry(
            diameter=optimal_diameter,
            focal_length=optimal_diameter * optimal_f_d_ratio,
        )

        # Calcular métricas de rendimiento para la geometría óptima
        # Usar el modelo de eficiencia basado en f/D
        optimal_efficiency = aperture_efficiency_model(optimal_f_d_ratio)
        # aperture_efficiency_model siempre retorna array, convertir a escalar
        optimal_efficiency = float(np.asarray(optimal_efficiency).item())

        final_gain = calculate_gain(
            diameter=optimal_diameter,
            frequency_ghz=SIM_FREQUENCY_GHZ,
            aperture_efficiency=optimal_efficiency,
        )
        final_beamwidth = calculate_beamwidth(
            diameter=optimal_diameter, frequency_ghz=SIM_FREQUENCY_GHZ
        )

        final_metrics = PerformanceMetrics(gain=final_gain, beamwidth=final_beamwidth)

        # Extraer historial de convergencia (evolución del mejor objetivo)
        # Manejo robusto de errores para evitar fallos si el historial está incompleto
        convergence_history = []
        for generation in res.history:
            try:
                # Obtener el mejor valor del objetivo 1 (-ganancia) en esta generación
                obj_values = generation.opt.get("F")
                if obj_values is not None and len(obj_values) > 0:
                    best_neg_gain = np.min(obj_values[:, 0])
                    # Convertir de -ganancia a ganancia positiva
                    convergence_history.append(-best_neg_gain)
                else:
                    # Si no hay datos disponibles, usar el último valor válido
                    if convergence_history:
                        convergence_history.append(convergence_history[-1])
            except (AttributeError, IndexError, KeyError) as e:
                # Si hay un error al acceder a los datos, registrar advertencia
                # y continuar sin romper la ejecución
                import warnings
                warnings.warn(
                    f"Error al extraer historial de convergencia en generación "
                    f"{len(convergence_history)}: {e}. Se omite esta generación.",
                    RuntimeWarning
                )
                continue

        # Construir y retornar el resultado
        result = OptimizationResult(
            optimal_geometry=optimal_geometry,
            performance_metrics=final_metrics,
            convergence_history=convergence_history,
        )

        return result
