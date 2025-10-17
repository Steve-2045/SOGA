"""Tests para el módulo app.facade."""

from unittest.mock import MagicMock, patch

import pytest

from soga.app.facade import (
    ApplicationFacade,
    FacadeValidationError,
    DEFAULT_USER_PARAMS,
)
from soga.core.models import (
    AntennaGeometry,
    OptimizationConstraints,
    OptimizationResult,
    PerformanceMetrics,
)


@pytest.fixture
def valid_user_params():
    """Parámetros de ejemplo que simulan una entrada válida de la GUI."""
    return {
        "min_diameter_m": 0.2,
        "max_diameter_m": 1.5,
        "max_payload_g": 800,
        "min_f_d_ratio": 0.4,
        "max_f_d_ratio": 0.6,
        "desired_range_km": 8.0,
    }


@pytest.fixture
def mock_optimization_result():
    """Resultado de optimización simulado para tests."""
    geometry = AntennaGeometry(diameter=0.85, focal_length=0.425)
    metrics = PerformanceMetrics(gain=35.0, beamwidth=2.5)
    return OptimizationResult(
        optimal_geometry=geometry,
        performance_metrics=metrics,
        convergence_history=[30.0, 32.0, 34.0, 35.0],
    )


class TestApplicationFacadeInit:
    """Tests para la inicialización de ApplicationFacade."""

    def test_init_default_engine(self):
        """Prueba que se crea un motor por defecto si no se proporciona uno."""
        facade = ApplicationFacade()
        assert facade._engine is not None

    def test_init_custom_engine(self):
        """Prueba que se puede inyectar un motor personalizado."""
        mock_engine = MagicMock()
        facade = ApplicationFacade(engine=mock_engine)
        assert facade._engine is mock_engine


class TestRunOptimization:
    """Tests para el método run_optimization."""

    @patch("soga.app.facade.OptimizationEngine")
    def test_return_type_and_structure(
        self, MockEngine, valid_user_params, mock_optimization_result
    ):
        """Verifica que retorna un diccionario con la estructura correcta."""
        mock_engine_instance = MockEngine.return_value
        mock_engine_instance.run.return_value = mock_optimization_result

        facade = ApplicationFacade()
        result = facade.run_optimization(valid_user_params)

        # Verificar tipo
        assert isinstance(result, dict)

        # Verificar claves esperadas
        expected_keys = [
            "optimal_diameter_mm",
            "optimal_focal_length_mm",
            "optimal_depth_mm",
            "f_d_ratio",
            "expected_gain_dbi",
            "beamwidth_deg",
            "convergence",
        ]
        for key in expected_keys:
            assert key in result

        # Verificar tipos de valores
        assert isinstance(result["optimal_diameter_mm"], float)
        assert isinstance(result["convergence"], list)

    @patch("soga.app.facade.OptimizationEngine")
    def test_unit_conversion_meters_to_millimeters(
        self, MockEngine, valid_user_params, mock_optimization_result
    ):
        """Verifica la conversión correcta de metros a milímetros."""
        mock_engine_instance = MockEngine.return_value
        mock_engine_instance.run.return_value = mock_optimization_result

        facade = ApplicationFacade()
        result = facade.run_optimization(valid_user_params)

        # diameter = 0.85m → 850mm
        assert result["optimal_diameter_mm"] == pytest.approx(850.0)
        # focal_length = 0.425m → 425mm
        assert result["optimal_focal_length_mm"] == pytest.approx(425.0)

    @patch("soga.app.facade.OptimizationEngine")
    def test_empty_params_uses_defaults(self, MockEngine, mock_optimization_result):
        """Verifica que un diccionario vacío usa todos los valores por defecto."""
        mock_engine_instance = MockEngine.return_value
        mock_engine_instance.run.return_value = mock_optimization_result

        facade = ApplicationFacade()
        facade.run_optimization({})

        # Verificar que el motor fue llamado
        mock_engine_instance.run.assert_called_once()

        # Verificar que se usaron los defaults
        call_args = mock_engine_instance.run.call_args
        constraints = call_args.args[0]

        assert constraints.min_diameter == DEFAULT_USER_PARAMS["min_diameter_m"]
        assert constraints.max_diameter == DEFAULT_USER_PARAMS["max_diameter_m"]
        assert constraints.desired_range_km == DEFAULT_USER_PARAMS["desired_range_km"]


class TestBuildConstraints:
    """Tests para el método _build_constraints."""

    @patch("soga.app.facade.OptimizationEngine")
    def test_parameter_translation(
        self, MockEngine, valid_user_params, mock_optimization_result
    ):
        """Verifica la traducción correcta de parámetros a restricciones."""
        mock_engine_instance = MockEngine.return_value
        mock_engine_instance.run.return_value = mock_optimization_result

        facade = ApplicationFacade()
        facade.run_optimization(valid_user_params)

        # Capturar el objeto constraints pasado al motor
        call_args = mock_engine_instance.run.call_args
        constraints = call_args.args[0]

        # Verificar tipo
        assert isinstance(constraints, OptimizationConstraints)

        # Verificar valores directos
        assert constraints.min_diameter == 0.2
        assert constraints.max_diameter == 1.5
        assert constraints.min_f_d_ratio == 0.4
        assert constraints.max_f_d_ratio == 0.6
        assert constraints.desired_range_km == 8.0

        # Verificar conversión de unidades: gramos → kilogramos
        assert constraints.max_weight == pytest.approx(0.8)

    @patch("soga.app.facade.OptimizationEngine")
    def test_partial_params_merges_with_defaults(
        self, MockEngine, mock_optimization_result
    ):
        """Verifica que parámetros parciales se mezclan con defaults."""
        mock_engine_instance = MockEngine.return_value
        mock_engine_instance.run.return_value = mock_optimization_result

        facade = ApplicationFacade()
        partial_params = {"max_diameter_m": 3.0}  # Solo un parámetro
        facade.run_optimization(partial_params)

        call_args = mock_engine_instance.run.call_args
        constraints = call_args.args[0]

        # El parámetro provisto debe usarse
        assert constraints.max_diameter == 3.0

        # Los demás deben ser defaults
        assert constraints.min_diameter == DEFAULT_USER_PARAMS["min_diameter_m"]
        assert constraints.min_f_d_ratio == DEFAULT_USER_PARAMS["min_f_d_ratio"]


class TestErrorHandling:
    """Tests para el manejo de errores."""

    def test_invalid_type_raises_validation_error(self):
        """Verifica que tipos inválidos lanzan FacadeValidationError."""
        facade = ApplicationFacade()

        # String en lugar de número
        invalid_params = {"max_payload_g": "ochocientos"}

        with pytest.raises(
            FacadeValidationError, match="Error al construir restricciones"
        ):
            facade.run_optimization(invalid_params)

    def test_none_value_raises_validation_error(self):
        """Verifica que valores None lanzan FacadeValidationError."""
        facade = ApplicationFacade()
        invalid_params = {"min_diameter_m": None}

        with pytest.raises(
            FacadeValidationError, match="Error al construir restricciones"
        ):
            facade.run_optimization(invalid_params)

    def test_invalid_constraints_raises_validation_error(self):
        """Verifica que restricciones inválidas lanzan FacadeValidationError."""
        facade = ApplicationFacade()

        # min > max (inválido)
        invalid_params = {
            "min_diameter_m": 2.0,
            "max_diameter_m": 1.0,
        }

        with pytest.raises(
            FacadeValidationError, match="Error al construir restricciones"
        ):
            facade.run_optimization(invalid_params)

    @patch("soga.app.facade.OptimizationEngine")
    def test_runtime_error_from_engine_raises_validation_error(
        self, MockEngine, valid_user_params
    ):
        """Verifica que RuntimeError del motor se convierte a FacadeValidationError."""
        mock_engine_instance = MockEngine.return_value
        mock_engine_instance.run.side_effect = RuntimeError(
            "No se encontró solución viable"
        )

        facade = ApplicationFacade()

        with pytest.raises(
            FacadeValidationError, match="Error durante la optimización"
        ):
            facade.run_optimization(valid_user_params)


class TestFormatOutput:
    """Tests para el método _format_output."""

    def test_all_fields_present(self, mock_optimization_result):
        """Verifica que todos los campos están presentes en la salida."""
        facade = ApplicationFacade()
        output = facade._format_output(mock_optimization_result)

        expected_keys = [
            "optimal_diameter_mm",
            "optimal_focal_length_mm",
            "optimal_depth_mm",
            "f_d_ratio",
            "expected_gain_dbi",
            "beamwidth_deg",
            "convergence",
        ]

        for key in expected_keys:
            assert key in output

    def test_convergence_history_preserved(self, mock_optimization_result):
        """Verifica que el historial de convergencia se preserva correctamente."""
        facade = ApplicationFacade()
        output = facade._format_output(mock_optimization_result)

        assert output["convergence"] == [30.0, 32.0, 34.0, 35.0]
        assert len(output["convergence"]) == 4

    def test_metrics_values_preserved(self, mock_optimization_result):
        """Verifica que los valores de métricas se preservan sin alteración."""
        facade = ApplicationFacade()
        output = facade._format_output(mock_optimization_result)

        assert output["expected_gain_dbi"] == 35.0
        assert output["beamwidth_deg"] == 2.5
        assert output["f_d_ratio"] == pytest.approx(0.5)
