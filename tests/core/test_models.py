import pytest
from soga.core.models import (
    AntennaGeometry,
    PerformanceMetrics,
    OptimizationConstraints,
    OptimizationResult,
)


class TestAntennaGeometry:
    """Tests para la clase AntennaGeometry."""

    def test_valid_geometry(self):
        """Prueba la creación de una geometría válida."""
        geometry = AntennaGeometry(diameter=1.0, focal_length=0.5)
        assert geometry.diameter == 1.0
        assert geometry.focal_length == 0.5
        assert geometry.f_d_ratio == 0.5
        # depth = D^2 / (16*f) = 1.0^2 / (16*0.5) = 1/8 = 0.125
        assert geometry.depth == pytest.approx(0.125)

    def test_invalid_diameter_zero(self):
        """Prueba que se rechaza un diámetro cero."""
        with pytest.raises(ValueError, match="El diámetro debe ser positivo"):
            AntennaGeometry(diameter=0, focal_length=0.5)

    def test_invalid_diameter_negative(self):
        """Prueba que se rechaza un diámetro negativo."""
        with pytest.raises(ValueError, match="El diámetro debe ser positivo"):
            AntennaGeometry(diameter=-1.0, focal_length=0.5)

    def test_invalid_focal_length_zero(self):
        """Prueba que se rechaza una distancia focal cero."""
        with pytest.raises(ValueError, match="La distancia focal debe ser positiva"):
            AntennaGeometry(diameter=1.0, focal_length=0)

    def test_invalid_focal_length_negative(self):
        """Prueba que se rechaza una distancia focal negativa."""
        with pytest.raises(ValueError, match="La distancia focal debe ser positiva"):
            AntennaGeometry(diameter=1.0, focal_length=-0.5)

    def test_f_d_ratio_calculation(self):
        """Prueba el cálculo de la relación focal f/D."""
        geometry = AntennaGeometry(diameter=2.0, focal_length=1.0)
        assert geometry.f_d_ratio == 0.5

    def test_depth_calculation(self):
        """Prueba el cálculo de la profundidad."""
        geometry = AntennaGeometry(diameter=1.0, focal_length=0.5)
        expected_depth = (1.0**2) / (16 * 0.5)
        assert geometry.depth == pytest.approx(expected_depth)

    def test_invalid_f_d_ratio_too_low(self):
        """Prueba que se rechaza una relación f/D demasiado baja."""
        # f/D = 0.1 < 0.2 (mínimo práctico)
        with pytest.raises(ValueError, match="f/D.*demasiado baja"):
            AntennaGeometry(diameter=1.0, focal_length=0.1)

    def test_invalid_f_d_ratio_too_high(self):
        """Prueba que se rechaza una relación f/D demasiado alta."""
        # f/D = 2.0 > 1.5 (máximo práctico)
        with pytest.raises(ValueError, match="f/D.*demasiado alta"):
            AntennaGeometry(diameter=1.0, focal_length=2.0)

    def test_valid_f_d_ratio_at_boundaries(self):
        """Prueba que se aceptan valores en los límites del rango práctico."""
        # f/D = 0.2 (mínimo exacto)
        geom_min = AntennaGeometry(diameter=1.0, focal_length=0.2)
        assert geom_min.f_d_ratio == pytest.approx(0.2)

        # f/D = 1.5 (máximo exacto)
        geom_max = AntennaGeometry(diameter=1.0, focal_length=1.5)
        assert geom_max.f_d_ratio == pytest.approx(1.5)


class TestPerformanceMetrics:
    """Tests para la clase PerformanceMetrics."""

    def test_valid_metrics(self):
        """Prueba la creación de métricas válidas."""
        metrics = PerformanceMetrics(gain=35.0, beamwidth=2.5)
        assert metrics.gain == 35.0
        assert metrics.beamwidth == 2.5

    def test_invalid_beamwidth_zero(self):
        """Prueba que se rechaza un ancho de haz cero."""
        with pytest.raises(
            ValueError, match="El ancho de haz debe estar entre 0 y 180 grados"
        ):
            PerformanceMetrics(gain=35.0, beamwidth=0)

    def test_invalid_beamwidth_negative(self):
        """Prueba que se rechaza un ancho de haz negativo."""
        with pytest.raises(
            ValueError, match="El ancho de haz debe estar entre 0 y 180 grados"
        ):
            PerformanceMetrics(gain=35.0, beamwidth=-1.0)

    def test_invalid_beamwidth_too_large(self):
        """Prueba que se rechaza un ancho de haz mayor a 180 grados."""
        with pytest.raises(
            ValueError, match="El ancho de haz debe estar entre 0 y 180 grados"
        ):
            PerformanceMetrics(gain=35.0, beamwidth=181.0)

    def test_negative_gain_is_allowed(self):
        """Prueba que se permite una ganancia negativa (antenas muy ineficientes)."""
        metrics = PerformanceMetrics(gain=-5.0, beamwidth=90.0)
        assert metrics.gain == -5.0


class TestOptimizationConstraints:
    """Tests para la clase OptimizationConstraints."""

    def test_valid_constraints(self):
        """Prueba la creación de restricciones válidas."""
        constraints = OptimizationConstraints(
            min_diameter=0.1,
            max_diameter=2.0,
            max_weight=1.0,
            min_f_d_ratio=0.3,
            max_f_d_ratio=0.8,
            desired_range_km=5.0,
        )
        assert constraints.min_diameter == 0.1
        assert constraints.max_diameter == 2.0

    def test_invalid_min_diameter_negative(self):
        """Prueba que se rechaza un min_diameter negativo."""
        with pytest.raises(ValueError, match="min_diameter debe ser positivo"):
            OptimizationConstraints(
                min_diameter=-0.1,
                max_diameter=2.0,
                max_weight=1.0,
                min_f_d_ratio=0.3,
                max_f_d_ratio=0.8,
                desired_range_km=5.0,
            )

    def test_invalid_max_diameter_negative(self):
        """Prueba que se rechaza un max_diameter negativo."""
        with pytest.raises(ValueError, match="max_diameter debe ser positivo"):
            OptimizationConstraints(
                min_diameter=0.1,
                max_diameter=-2.0,
                max_weight=1.0,
                min_f_d_ratio=0.3,
                max_f_d_ratio=0.8,
                desired_range_km=5.0,
            )

    def test_invalid_diameter_range(self):
        """Prueba que min_diameter debe ser menor que max_diameter."""
        with pytest.raises(
            ValueError, match="min_diameter .* debe ser menor que max_diameter"
        ):
            OptimizationConstraints(
                min_diameter=2.0,
                max_diameter=1.0,
                max_weight=1.0,
                min_f_d_ratio=0.3,
                max_f_d_ratio=0.8,
                desired_range_km=5.0,
            )

    def test_invalid_max_weight_negative(self):
        """Prueba que se rechaza un max_weight negativo."""
        with pytest.raises(ValueError, match="max_weight debe ser positivo"):
            OptimizationConstraints(
                min_diameter=0.1,
                max_diameter=2.0,
                max_weight=-1.0,
                min_f_d_ratio=0.3,
                max_f_d_ratio=0.8,
                desired_range_km=5.0,
            )

    def test_invalid_f_d_ratio_range(self):
        """Prueba que min_f_d_ratio debe ser menor que max_f_d_ratio."""
        with pytest.raises(
            ValueError, match="min_f_d_ratio .* debe ser menor que max_f_d_ratio"
        ):
            OptimizationConstraints(
                min_diameter=0.1,
                max_diameter=2.0,
                max_weight=1.0,
                min_f_d_ratio=0.8,
                max_f_d_ratio=0.3,
                desired_range_km=5.0,
            )

    def test_invalid_desired_range_negative(self):
        """Prueba que se rechaza un desired_range_km negativo."""
        with pytest.raises(ValueError, match="desired_range_km debe ser positivo"):
            OptimizationConstraints(
                min_diameter=0.1,
                max_diameter=2.0,
                max_weight=1.0,
                min_f_d_ratio=0.3,
                max_f_d_ratio=0.8,
                desired_range_km=-5.0,
            )


class TestOptimizationResult:
    """Tests para la clase OptimizationResult."""

    def test_valid_result(self):
        """Prueba la creación de un resultado válido."""
        geometry = AntennaGeometry(diameter=1.0, focal_length=0.5)
        metrics = PerformanceMetrics(gain=35.0, beamwidth=2.5)
        result = OptimizationResult(
            optimal_geometry=geometry,
            performance_metrics=metrics,
            convergence_history=[30.0, 32.0, 34.0, 35.0],
        )
        assert result.optimal_geometry == geometry
        assert result.performance_metrics == metrics
        assert len(result.convergence_history) == 4

    def test_result_with_default_convergence(self):
        """Prueba que convergence_history por defecto es una lista vacía."""
        geometry = AntennaGeometry(diameter=1.0, focal_length=0.5)
        metrics = PerformanceMetrics(gain=35.0, beamwidth=2.5)
        result = OptimizationResult(
            optimal_geometry=geometry, performance_metrics=metrics
        )
        assert result.convergence_history == []
