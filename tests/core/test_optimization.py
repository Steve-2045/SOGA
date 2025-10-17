import numpy as np
import pytest

from soga.core.models import (
    OptimizationConstraints,
    OptimizationResult,
    AntennaGeometry,
    PerformanceMetrics,
)
from soga.core.optimization import (
    AntennaProblem,
    OptimizationEngine,
    aperture_efficiency_model,
    SIM_AREAL_DENSITY_KG_PER_M2,
    EFFICIENCY_PEAK,
    OPTIMAL_F_D_RATIO,
)


@pytest.fixture
def constraints():
    """Devuelve un conjunto de restricciones de ejemplo para las pruebas."""
    return OptimizationConstraints(
        min_diameter=0.1,
        max_diameter=2.0,
        max_weight=1.0,  # 1 kg de peso máximo
        min_f_d_ratio=0.3,
        max_f_d_ratio=0.8,
        desired_range_km=10.0,
    )


@pytest.fixture
def tight_constraints():
    """Restricciones muy ajustadas para probar casos límite."""
    return OptimizationConstraints(
        min_diameter=0.15,
        max_diameter=0.25,
        max_weight=0.05,  # Muy restrictivo
        min_f_d_ratio=0.4,
        max_f_d_ratio=0.5,
        desired_range_km=5.0,
    )


class TestApertureEfficiencyModel:
    """Tests para el modelo de eficiencia de apertura."""

    def test_optimal_f_d_ratio(self):
        """El modelo debe retornar eficiencia máxima en el punto óptimo."""
        efficiency = aperture_efficiency_model(OPTIMAL_F_D_RATIO)
        assert efficiency == pytest.approx(EFFICIENCY_PEAK, abs=1e-6)

    def test_efficiency_range(self):
        """La eficiencia debe estar en el rango físico realista [0.40, 0.70]."""
        f_d_values = np.linspace(0.2, 1.5, 100)
        efficiencies = aperture_efficiency_model(f_d_values)

        assert np.all(efficiencies >= 0.40)
        assert np.all(efficiencies <= 0.70)

    def test_efficiency_symmetric_behavior(self):
        """La eficiencia debe decrecer al alejarse del óptimo."""
        # Valores antes y después del óptimo
        f_d_low = OPTIMAL_F_D_RATIO - 0.1
        f_d_high = OPTIMAL_F_D_RATIO + 0.1

        eff_optimal = aperture_efficiency_model(OPTIMAL_F_D_RATIO)
        eff_low = aperture_efficiency_model(f_d_low)
        eff_high = aperture_efficiency_model(f_d_high)

        assert eff_low < eff_optimal
        assert eff_high < eff_optimal

    def test_efficiency_vectorized(self):
        """El modelo debe aceptar arrays de NumPy."""
        f_d_array = np.array([0.3, 0.45, 0.6, 1.0])
        efficiencies = aperture_efficiency_model(f_d_array)

        assert isinstance(efficiencies, np.ndarray)
        assert efficiencies.shape == f_d_array.shape
        assert efficiencies[1] == pytest.approx(EFFICIENCY_PEAK, abs=1e-6)

    def test_efficiency_extreme_values(self):
        """Probar valores extremos del rango f/D."""
        # Valores extremos del rango físico
        eff_min = aperture_efficiency_model(0.2)  # Parábola profunda
        eff_max = aperture_efficiency_model(1.5)  # Parábola muy plana

        # Deben estar en rango válido
        assert 0.40 <= eff_min <= 0.70
        assert 0.40 <= eff_max <= 0.70

        # La eficiencia en f/D=1.5 debe ser menor (más spillover)
        assert eff_max < eff_min


class TestAntennaProblem:
    """Tests para la clase AntennaProblem."""

    def test_antenna_problem_initialization(self, constraints):
        """El problema debe inicializarse correctamente con las restricciones."""
        problem = AntennaProblem(constraints)

        assert problem.n_var == 2  # diámetro, f/D
        assert problem.n_obj == 2  # ganancia, peso
        assert problem.n_constr == 1  # peso <= max_weight

        # Verificar límites del espacio de búsqueda
        np.testing.assert_array_equal(
            problem.xl, [constraints.min_diameter, constraints.min_f_d_ratio]
        )
        np.testing.assert_array_equal(
            problem.xu, [constraints.max_diameter, constraints.max_f_d_ratio]
        )

    def test_antenna_problem_evaluate(self, constraints):
        """
        Prueba la función de evaluación (_evaluate) de la clase AntennaProblem.

        Verifica que para una geometría de antena conocida, los objetivos (ganancia, peso)
        y las violaciones de restricciones se calculan correctamente.
        """
        # 1. Instanciar el problema con las restricciones
        problem = AntennaProblem(constraints)

        # 2. Definir una solución de ejemplo para evaluar: [diámetro, f/D ratio]
        # Usaremos un diámetro de 1 metro para facilitar los cálculos.
        test_solution = np.array([[1.0, 0.5]])

        # 3. Preparar el diccionario de salida que pymoo espera
        out = {}

        # 4. Ejecutar la función de evaluación
        problem._evaluate(test_solution, out)

        # 5. Verificar los resultados

        # --- Verificar Objetivo 1: Ganancia (negativa, porque se minimiza -ganancia)
        # Con el modelo de eficiencia: f/D=0.5 → η_ap≈0.699
        # Para f=2.4GHz, D=1m: ganancia≈26.46 dBi
        expected_gain = 26.46
        assert out["F"][0, 0] == pytest.approx(-expected_gain, abs=0.1)

        # --- Verificar Objetivo 2: Peso
        expected_area = np.pi * (1.0 / 2) ** 2
        expected_weight = expected_area * SIM_AREAL_DENSITY_KG_PER_M2
        assert out["F"][0, 1] == pytest.approx(expected_weight)

        # --- Verificar Restricción 1: Peso
        # La restricción es peso <= max_weight (1.0 kg)
        # La violación es peso - max_weight
        # El peso esperado (~1.17 kg) es mayor que el máximo (1.0 kg)
        expected_violation = expected_weight - constraints.max_weight
        assert expected_violation > 0  # Asegurarse de que la violación es positiva
        assert out["G"][0, 0] == pytest.approx(expected_violation)

    def test_antenna_problem_evaluate_batch(self, constraints):
        """La función debe evaluar múltiples soluciones en batch."""
        problem = AntennaProblem(constraints)

        # Evaluar 5 soluciones simultáneamente
        test_solutions = np.array([
            [0.5, 0.4],
            [1.0, 0.45],
            [1.5, 0.5],
            [2.0, 0.6],
            [0.2, 0.35],
        ])

        out = {}
        problem._evaluate(test_solutions, out)

        # Verificar dimensiones de salida
        assert out["F"].shape == (5, 2)  # 5 soluciones, 2 objetivos
        assert out["G"].shape == (5, 1)  # 5 soluciones, 1 restricción

        # Verificar que todas las ganancias son negativas (minimización)
        assert np.all(out["F"][:, 0] < 0)

        # Verificar que todos los pesos son positivos
        assert np.all(out["F"][:, 1] > 0)

    def test_antenna_problem_satisfiable_constraint(self, constraints):
        """Probar una solución que satisface la restricción de peso."""
        problem = AntennaProblem(constraints)

        # Antena pequeña que cumple la restricción de peso
        # D=0.5m → peso ≈ 0.29 kg < 1.0 kg (satisface)
        test_solution = np.array([[0.5, 0.4]])

        out = {}
        problem._evaluate(test_solution, out)

        # La violación debe ser negativa (cumple restricción)
        assert out["G"][0, 0] < 0


class TestOptimizationEngine:
    """Tests para la clase OptimizationEngine."""

    def test_engine_initialization_default(self):
        """El motor debe inicializarse con parámetros por defecto."""
        engine = OptimizationEngine()

        assert engine.population_size == 40
        assert engine.max_generations == 80
        assert engine.seed == 1

    def test_engine_initialization_custom(self):
        """El motor debe aceptar parámetros personalizados."""
        engine = OptimizationEngine(
            population_size=20, max_generations=50, seed=42
        )

        assert engine.population_size == 20
        assert engine.max_generations == 50
        assert engine.seed == 42

    def test_engine_run_success(self, constraints):
        """El motor debe ejecutar optimización exitosamente."""
        engine = OptimizationEngine(population_size=20, max_generations=10, seed=42)

        result = engine.run(constraints)

        # Verificar tipo de retorno
        assert isinstance(result, OptimizationResult)
        assert isinstance(result.optimal_geometry, AntennaGeometry)
        assert isinstance(result.performance_metrics, PerformanceMetrics)

        # Verificar que la geometría está dentro de límites
        assert constraints.min_diameter <= result.optimal_geometry.diameter <= constraints.max_diameter
        assert constraints.min_f_d_ratio <= result.optimal_geometry.f_d_ratio <= constraints.max_f_d_ratio

        # Verificar que las métricas son razonables
        assert result.performance_metrics.gain > 0
        assert 0 < result.performance_metrics.beamwidth < 180

    def test_engine_run_convergence_history(self, constraints):
        """El motor debe retornar historial de convergencia."""
        engine = OptimizationEngine(population_size=20, max_generations=15, seed=42)

        result = engine.run(constraints)

        # Debe haber historial de convergencia
        assert len(result.convergence_history) > 0
        assert len(result.convergence_history) <= 15  # Máximo = max_generations

        # El historial debe mostrar mejora (ganancia creciente o estable)
        history = np.array(result.convergence_history)
        assert np.all(np.diff(history) >= -0.1)  # Tolerancia para ruido numérico

    def test_engine_run_tight_constraints(self, tight_constraints):
        """El motor debe encontrar soluciones incluso con restricciones ajustadas."""
        engine = OptimizationEngine(population_size=30, max_generations=20, seed=42)

        result = engine.run(tight_constraints)

        # Debe encontrar una solución
        assert result is not None
        assert isinstance(result.optimal_geometry, AntennaGeometry)

        # Verificar que cumple las restricciones
        assert tight_constraints.min_diameter <= result.optimal_geometry.diameter <= tight_constraints.max_diameter
        assert tight_constraints.min_f_d_ratio <= result.optimal_geometry.f_d_ratio <= tight_constraints.max_f_d_ratio

    def test_engine_select_knee_point_single_solution(self):
        """El knee point con una sola solución debe retornar esa solución."""
        engine = OptimizationEngine()

        X = np.array([[1.0, 0.5]])
        F = np.array([[-25.0, 1.0]])

        knee = engine._select_knee_point(X, F)

        np.testing.assert_array_equal(knee, X[0])

    def test_engine_select_knee_point_multiple_solutions(self):
        """El knee point debe seleccionar el mejor balance del frente de Pareto."""
        engine = OptimizationEngine()

        # Frente de Pareto simulado: [ganancia negativa, peso]
        X = np.array([
            [0.5, 0.4],   # Mejor peso, peor ganancia
            [1.0, 0.45],  # Balance intermedio (debería ser el knee)
            [1.5, 0.5],   # Mejor ganancia, peor peso
        ])
        F = np.array([
            [-20.0, 0.3],  # Baja ganancia, bajo peso
            [-25.0, 1.0],  # Balance medio
            [-28.0, 2.5],  # Alta ganancia, alto peso
        ])

        knee = engine._select_knee_point(X, F)

        # El knee point debe ser una de las soluciones
        assert knee in X

    def test_engine_select_knee_point_identical_extremes(self):
        """El knee point debe manejar casos donde los extremos son idénticos."""
        engine = OptimizationEngine()

        # Todas las soluciones tienen los mismos valores normalizados
        X = np.array([
            [1.0, 0.5],
            [1.0, 0.5],
        ])
        F = np.array([
            [-25.0, 1.0],
            [-25.0, 1.0],
        ])

        knee = engine._select_knee_point(X, F)

        # Debe retornar una solución válida sin error
        assert knee in X

    def test_engine_reproducibility(self, constraints):
        """El motor debe producir resultados reproducibles con la misma semilla."""
        engine1 = OptimizationEngine(population_size=20, max_generations=10, seed=123)
        engine2 = OptimizationEngine(population_size=20, max_generations=10, seed=123)

        result1 = engine1.run(constraints)
        result2 = engine2.run(constraints)

        # Los resultados deben ser idénticos
        assert result1.optimal_geometry.diameter == pytest.approx(
            result2.optimal_geometry.diameter
        )
        assert result1.optimal_geometry.focal_length == pytest.approx(
            result2.optimal_geometry.focal_length
        )

    def test_engine_run_with_infeasible_constraints(self):
        """El motor debe lanzar RuntimeError si las restricciones son imposibles de satisfacer."""
        engine = OptimizationEngine(population_size=20, max_generations=10, seed=42)

        # Restricciones imposibles: peso máximo muy bajo
        impossible_constraints = OptimizationConstraints(
            min_diameter=1.5,  # Grande
            max_diameter=2.0,  # Muy grande
            max_weight=0.001,  # Peso imposiblemente bajo (1 gramo)
            min_f_d_ratio=0.3,
            max_f_d_ratio=0.8,
            desired_range_km=10.0,
        )

        # El optimizador debe lanzar RuntimeError cuando no encuentra soluciones viables
        with pytest.raises(RuntimeError, match="no encontró ninguna solución viable"):
            engine.run(impossible_constraints)
