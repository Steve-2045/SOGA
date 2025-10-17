import pytest
import numpy as np
from soga.core.physics import calculate_gain, calculate_beamwidth, SPEED_OF_LIGHT


class TestCalculateGain:
    """Tests para la función calculate_gain."""

    @pytest.mark.parametrize(
        "diameter, frequency_ghz, aperture_efficiency, expected_gain_dbi",
        [
            # Valores de referencia calculados con una calculadora online (Pasternack).
            (0.6, 12, 0.55, 34.96),
            (1.2, 4, 0.6, 31.82),
            # Valores de referencia validados con calculadora estándar (Pasternack).
            (1.0, 10, 0.65, 38.54),
            (0.3, 24, 0.5, 34.54),
        ],
    )
    def test_valid_inputs(
        self, diameter, frequency_ghz, aperture_efficiency, expected_gain_dbi
    ):
        """Prueba la función calculate_gain con una variedad de entradas válidas."""
        calculated_gain = calculate_gain(diameter, frequency_ghz, aperture_efficiency)
        # Se comprueba con una tolerancia de 0.1 dB como sugiere la guía.
        assert np.isclose(calculated_gain, expected_gain_dbi, atol=0.1)

    def test_invalid_efficiency_zero(self):
        """Prueba que calculate_gain lanza un ValueError para eficiencia cero."""
        with pytest.raises(
            ValueError,
            match=r"La eficiencia de apertura debe ser mayor que 0\.",
        ):
            calculate_gain(diameter=0.6, frequency_ghz=12, aperture_efficiency=0)

    def test_invalid_efficiency_too_high(self):
        """Prueba que calculate_gain lanza un ValueError para eficiencia > 0.85."""
        with pytest.raises(
            ValueError,
            match=r"La eficiencia de apertura debe ser menor o igual a 0\.85",
        ):
            calculate_gain(diameter=0.6, frequency_ghz=12, aperture_efficiency=0.90)

    def test_invalid_efficiency_negative(self):
        """Prueba que calculate_gain lanza un ValueError para eficiencia negativa."""
        with pytest.raises(
            ValueError,
            match=r"La eficiencia de apertura debe ser mayor que 0\.",
        ):
            calculate_gain(diameter=0.6, frequency_ghz=12, aperture_efficiency=-0.5)

    def test_invalid_diameter_zero(self):
        """Prueba que calculate_gain lanza un ValueError para diámetro cero."""
        with pytest.raises(ValueError, match="El diámetro debe ser un valor positivo."):
            calculate_gain(diameter=0, frequency_ghz=12, aperture_efficiency=0.55)

    def test_invalid_diameter_negative(self):
        """Prueba que calculate_gain lanza un ValueError para diámetro negativo."""
        with pytest.raises(ValueError, match="El diámetro debe ser un valor positivo."):
            calculate_gain(diameter=-0.6, frequency_ghz=12, aperture_efficiency=0.55)

    def test_invalid_frequency_zero(self):
        """Prueba que calculate_gain lanza un ValueError para frecuencia cero."""
        with pytest.raises(
            ValueError, match="La frecuencia debe ser un valor positivo."
        ):
            calculate_gain(diameter=0.6, frequency_ghz=0, aperture_efficiency=0.55)

    def test_invalid_frequency_negative(self):
        """Prueba que calculate_gain lanza un ValueError para frecuencia negativa."""
        with pytest.raises(
            ValueError, match="La frecuencia debe ser un valor positivo."
        ):
            calculate_gain(diameter=0.6, frequency_ghz=-10, aperture_efficiency=0.55)

    def test_vectorized_operation(self):
        """Prueba que la función funciona con arrays de NumPy."""
        diameters = np.array([0.5, 1.0, 1.5])
        gains = calculate_gain(diameters, 10.0, 0.6)
        assert isinstance(gains, np.ndarray)
        assert len(gains) == 3
        assert np.all(gains > 0)


class TestCalculateBeamwidth:
    """Tests para la función calculate_beamwidth."""

    def test_valid_inputs(self):
        """Prueba el cálculo del ancho de haz con entradas válidas."""
        beamwidth = calculate_beamwidth(diameter=1.0, frequency_ghz=2.4)
        # Para D=1m, f=2.4GHz: λ ≈ 0.12491m, beamwidth ≈ 65*0.12491/1 = 8.12°
        assert beamwidth == pytest.approx(8.12, abs=0.1)

    def test_custom_k_factor(self):
        """Prueba con un factor k personalizado."""
        beamwidth = calculate_beamwidth(diameter=1.0, frequency_ghz=2.4, k_factor=80.0)
        # Para D=1m, f=2.4GHz, k=80: λ ≈ 0.12491m, beamwidth ≈ 80*0.12491/1 = 9.99°
        assert beamwidth == pytest.approx(9.99, abs=0.1)

    def test_invalid_diameter_zero(self):
        """Prueba que se rechaza un diámetro cero."""
        with pytest.raises(ValueError, match="El diámetro debe ser un valor positivo."):
            calculate_beamwidth(diameter=0, frequency_ghz=2.4)

    def test_invalid_frequency_negative(self):
        """Prueba que se rechaza una frecuencia negativa."""
        with pytest.raises(
            ValueError, match="La frecuencia debe ser un valor positivo."
        ):
            calculate_beamwidth(diameter=1.0, frequency_ghz=-2.4)

    def test_invalid_k_factor(self):
        """Prueba que se rechaza un factor k no positivo."""
        with pytest.raises(ValueError, match="El factor k debe ser positivo."):
            calculate_beamwidth(diameter=1.0, frequency_ghz=2.4, k_factor=-70.0)

    def test_vectorized_operation(self):
        """Prueba que la función funciona con arrays de NumPy."""
        diameters = np.array([0.5, 1.0, 1.5])
        beamwidths = calculate_beamwidth(diameters, 2.4)
        assert isinstance(beamwidths, np.ndarray)
        assert len(beamwidths) == 3
        # El ancho de haz es inversamente proporcional al diámetro
        assert beamwidths[0] > beamwidths[1] > beamwidths[2]


class TestConstants:
    """Tests para las constantes físicas."""

    def test_speed_of_light(self):
        """Verifica que la velocidad de la luz sea correcta."""
        assert SPEED_OF_LIGHT == 299792458.0
