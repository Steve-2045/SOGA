"""
Módulo de física electromagnética para antenas parabólicas.

Implementa las ecuaciones fundamentales para el cálculo de características
de antenas parabólicas, incluyendo ganancia y ancho de haz.
"""

import numpy as np
from typing import Union

# Constantes físicas
SPEED_OF_LIGHT = 299792458.0  # Velocidad de la luz en el vacío (m/s)


def calculate_gain(
    diameter: Union[float, np.ndarray],
    frequency_ghz: Union[float, np.ndarray],
    aperture_efficiency: Union[float, np.ndarray],
) -> Union[float, np.ndarray]:
    """
    Calcula la ganancia teórica de una antena parabólica.

    Implementa la fórmula estándar: G = η_ap * (π * D / λ)²

    Esta función está vectorizada para aceptar tanto números flotantes
    como arrays de NumPy.

    Args:
        diameter: Diámetro de la antena en metros (m).
        frequency_ghz: Frecuencia de operación en gigahertz (GHz).
        aperture_efficiency: Eficiencia de apertura (η_ap), valor entre 0 y 1.

    Returns:
        La ganancia de la antena en decibelios isótropos (dBi).

    Raises:
        ValueError: Si los parámetros no son físicamente válidos.

    Examples:
        >>> calculate_gain(1.0, 10.0, 0.65)
        38.54
    """
    # Validaciones compatibles con arrays
    if np.any(np.less_equal(diameter, 0)):
        raise ValueError("El diámetro debe ser un valor positivo.")
    if np.any(np.less_equal(frequency_ghz, 0)):
        raise ValueError("La frecuencia debe ser un valor positivo.")
    if np.any(np.less_equal(aperture_efficiency, 0)):
        raise ValueError("La eficiencia de apertura debe ser mayor que 0.")
    # Según literatura (Balanis, IEEE Std 145-2013), el máximo práctico
    # de eficiencia de apertura para antenas parabólicas es ~80% (0.80)
    # debido a pérdidas inevitables (spillover, blockage, iluminación no uniforme).
    # Permitimos hasta 0.85 como margen de seguridad para casos teóricos excepcionales
    # y para evitar falsos positivos en cálculos numéricos.
    if np.any(np.greater(aperture_efficiency, 0.85)):
        raise ValueError(
            "La eficiencia de apertura debe ser menor o igual a 0.85. "
            "El máximo físicamente realista para antenas parabólicas es ~0.80 (80%). "
            f"Valor recibido: {np.max(aperture_efficiency):.3f}"
        )

    # Convertir frecuencia a Hz y calcular longitud de onda
    frequency_hz = frequency_ghz * 1e9
    wavelength = SPEED_OF_LIGHT / frequency_hz

    # Ganancia lineal: G = η_ap * (π * D / λ)²
    gain_linear = aperture_efficiency * (np.pi * diameter / wavelength) ** 2

    # Convertir a escala logarítmica (dBi)
    gain_dbi = 10 * np.log10(gain_linear)

    return gain_dbi


def calculate_beamwidth(
    diameter: Union[float, np.ndarray],
    frequency_ghz: Union[float, np.ndarray],
    k_factor: float = 65.0,
) -> Union[float, np.ndarray]:
    """
    Calcula el ancho de haz a -3dB de una antena parabólica.

    Implementa la fórmula aproximada: θ = k * λ / D
    donde k es un factor que depende de la distribución de iluminación.

    Valores típicos de k según literatura:
    - k = 58.4: Iluminación parabólica óptima (Balanis)
    - k = 65.0: Antenas típicas con iluminación estándar (IEEE Std 145-2013)
    - k = 70.0: Distribución uniforme, caso conservador (Kraus)

    Args:
        diameter: Diámetro de la antena en metros (m).
        frequency_ghz: Frecuencia de operación en gigahertz (GHz).
        k_factor: Factor de iluminación. Por defecto 65.0 (IEEE estándar).

    Returns:
        Ancho de haz a -3dB en grados (°).

    Raises:
        ValueError: Si los parámetros no son físicamente válidos.

    Examples:
        >>> calculate_beamwidth(1.0, 10.0)
        2.1
    """
    if np.any(np.less_equal(diameter, 0)):
        raise ValueError("El diámetro debe ser un valor positivo.")
    if np.any(np.less_equal(frequency_ghz, 0)):
        raise ValueError("La frecuencia debe ser un valor positivo.")
    if k_factor <= 0:
        raise ValueError("El factor k debe ser positivo.")

    # Convertir frecuencia a Hz y calcular longitud de onda
    frequency_hz = frequency_ghz * 1e9
    wavelength = SPEED_OF_LIGHT / frequency_hz

    # Ancho de haz: θ = k * λ / D
    beamwidth_deg = k_factor * wavelength / diameter

    return beamwidth_deg
