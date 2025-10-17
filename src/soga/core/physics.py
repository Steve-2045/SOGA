"""
Módulo de física electromagnética para antenas parabólicas.

Implementa las ecuaciones fundamentales para el cálculo de características
de antenas parabólicas, incluyendo ganancia, ancho de haz y link budget.

Referencias:
- Balanis, "Antenna Theory: Analysis and Design", 4th Edition
- IEEE Std 145-2013: "IEEE Standard for Definitions of Terms for Antennas"
- Friis, H.T. (1946): "A Note on a Simple Transmission Formula"
- ITU-R P.525: "Calculation of free-space attenuation"
- Rappaport, "Wireless Communications: Principles and Practice", 2nd Edition
"""

import numpy as np
from typing import Union, Tuple
from dataclasses import dataclass

# Constantes físicas
SPEED_OF_LIGHT = 299792458.0  # Velocidad de la luz en el vacío (m/s)
BOLTZMANN_CONSTANT = 1.380649e-23  # Constante de Boltzmann (J/K)


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


@dataclass
class LinkBudgetResult:
    """
    Resultado del cálculo de link budget.

    Atributos:
        tx_power_dbm: Potencia de transmisión en dBm
        tx_antenna_gain_dbi: Ganancia de antena TX en dBi
        rx_antenna_gain_dbi: Ganancia de antena RX en dBi
        free_space_loss_db: Pérdida en espacio libre en dB
        implementation_loss_db: Pérdidas de implementación en dB
        rx_power_dbm: Potencia recibida en dBm
        rx_sensitivity_dbm: Sensibilidad del receptor en dBm
        required_snr_db: SNR requerido en dB
        fade_margin_db: Margen de desvanecimiento en dB
        link_margin_db: Margen total del link en dB
        is_viable: True si el link es viable (margen >= mínimo)
    """
    tx_power_dbm: float
    tx_antenna_gain_dbi: float
    rx_antenna_gain_dbi: float
    free_space_loss_db: float
    implementation_loss_db: float
    rx_power_dbm: float
    rx_sensitivity_dbm: float
    required_snr_db: float
    fade_margin_db: float
    link_margin_db: float
    is_viable: bool


def calculate_free_space_path_loss(
    distance_km: float,
    frequency_ghz: float
) -> float:
    """
    Calcula la pérdida de propagación en espacio libre usando la ecuación de Friis.

    Implementa la fórmula estándar ITU-R P.525:
    FSPL(dB) = 20·log₁₀(d) + 20·log₁₀(f) + 92.45

    donde:
    - d: distancia en kilómetros
    - f: frecuencia en GHz

    Esta ecuación es válida para:
    - Propagación en línea de visión (LOS - Line of Sight)
    - Espacio libre sin obstáculos
    - Distancias en la región de campo lejano (d >> 2D²/λ)

    Args:
        distance_km: Distancia entre transmisor y receptor en kilómetros (km)
        frequency_ghz: Frecuencia de operación en gigahertz (GHz)

    Returns:
        Pérdida de propagación en espacio libre en decibelios (dB)

    Raises:
        ValueError: Si los parámetros no son físicamente válidos

    References:
        - ITU-R P.525-4: "Calculation of free-space attenuation"
        - Friis, H.T. (1946): "A Note on a Simple Transmission Formula"
          Proc. IRE, Vol. 34, pp. 254-256
        - Rappaport, T.S.: "Wireless Communications", 2nd Ed., Eq. 3.1

    Examples:
        >>> calculate_free_space_path_loss(1.0, 2.4)
        80.05  # Pérdida para 1 km a 2.4 GHz
        >>> calculate_free_space_path_loss(10.0, 2.4)
        100.05  # Pérdida para 10 km a 2.4 GHz
    """
    if distance_km <= 0:
        raise ValueError(
            f"La distancia debe ser positiva. Valor recibido: {distance_km} km"
        )
    if frequency_ghz <= 0:
        raise ValueError(
            f"La frecuencia debe ser positiva. Valor recibido: {frequency_ghz} GHz"
        )

    # Fórmula de Friis para pérdida en espacio libre (ITU-R P.525)
    # FSPL(dB) = 20·log₁₀(d_km) + 20·log₁₀(f_GHz) + 92.45
    fspl_db = 20.0 * np.log10(distance_km) + 20.0 * np.log10(frequency_ghz) + 92.45

    return fspl_db


def calculate_link_budget(
    distance_km: float,
    frequency_ghz: float,
    tx_antenna_diameter_m: float,
    rx_antenna_diameter_m: float,
    tx_antenna_efficiency: float,
    rx_antenna_efficiency: float,
    tx_power_dbm: float,
    rx_sensitivity_dbm: float,
    required_snr_db: float,
    fade_margin_db: float,
    implementation_loss_db: float,
    min_link_margin_db: float = 6.0,
) -> LinkBudgetResult:
    """
    Calcula el link budget completo para un enlace de comunicación RF.

    Implementa la ecuación fundamental de link budget:
    P_rx = P_tx + G_tx + G_rx - L_fs - L_impl

    Y valida que se cumplan los requerimientos:
    Link Margin = P_rx - (RX_sens + SNR_req + Fade_margin)

    El link es viable si: Link Margin >= min_link_margin_db

    Args:
        distance_km: Distancia del enlace en kilómetros
        frequency_ghz: Frecuencia de operación en GHz
        tx_antenna_diameter_m: Diámetro de antena transmisora en metros
        rx_antenna_diameter_m: Diámetro de antena receptora en metros
        tx_antenna_efficiency: Eficiencia de apertura TX (0-1)
        rx_antenna_efficiency: Eficiencia de apertura RX (0-1)
        tx_power_dbm: Potencia de transmisión en dBm
        rx_sensitivity_dbm: Sensibilidad del receptor en dBm
        required_snr_db: SNR mínimo requerido en dB
        fade_margin_db: Margen para desvanecimiento en dB
        implementation_loss_db: Pérdidas de implementación en dB
        min_link_margin_db: Margen mínimo aceptable para validación (default: 6 dB)

    Returns:
        LinkBudgetResult con todos los parámetros del link budget calculados

    Raises:
        ValueError: Si algún parámetro no es físicamente válido

    References:
        - Rappaport, "Wireless Communications", 2nd Ed., Ch. 3
        - ITU-R P.341: "The concept of transmission loss for radio links"
        - IEEE Std 145-2013: Antenna terminology

    Examples:
        >>> result = calculate_link_budget(
        ...     distance_km=5.0,
        ...     frequency_ghz=2.4,
        ...     tx_antenna_diameter_m=1.0,
        ...     rx_antenna_diameter_m=1.0,
        ...     tx_antenna_efficiency=0.6,
        ...     rx_antenna_efficiency=0.6,
        ...     tx_power_dbm=20.0,
        ...     rx_sensitivity_dbm=-95.0,
        ...     required_snr_db=10.0,
        ...     fade_margin_db=10.0,
        ...     implementation_loss_db=3.0
        ... )
        >>> print(f"Link viable: {result.is_viable}, Margin: {result.link_margin_db:.1f} dB")
    """
    # Validación de parámetros
    if distance_km <= 0:
        raise ValueError(f"La distancia debe ser positiva: {distance_km} km")
    if frequency_ghz <= 0:
        raise ValueError(f"La frecuencia debe ser positiva: {frequency_ghz} GHz")
    if tx_antenna_diameter_m <= 0:
        raise ValueError(f"El diámetro TX debe ser positivo: {tx_antenna_diameter_m} m")
    if rx_antenna_diameter_m <= 0:
        raise ValueError(f"El diámetro RX debe ser positivo: {rx_antenna_diameter_m} m")
    if not (0 < tx_antenna_efficiency <= 1.0):
        raise ValueError(f"La eficiencia TX debe estar en (0,1]: {tx_antenna_efficiency}")
    if not (0 < rx_antenna_efficiency <= 1.0):
        raise ValueError(f"La eficiencia RX debe estar en (0,1]: {rx_antenna_efficiency}")
    if tx_power_dbm < -100 or tx_power_dbm > 60:
        raise ValueError(f"Potencia TX fuera de rango realista [-100, 60] dBm: {tx_power_dbm}")
    if rx_sensitivity_dbm > -20 or rx_sensitivity_dbm < -150:
        raise ValueError(f"Sensibilidad RX fuera de rango realista [-150, -20] dBm: {rx_sensitivity_dbm}")
    if required_snr_db < 0 or required_snr_db > 30:
        raise ValueError(f"SNR requerido fuera de rango realista [0, 30] dB: {required_snr_db}")
    if fade_margin_db < 0 or fade_margin_db > 40:
        raise ValueError(f"Margen de fade fuera de rango realista [0, 40] dB: {fade_margin_db}")
    if implementation_loss_db < 0 or implementation_loss_db > 20:
        raise ValueError(f"Pérdidas de implementación fuera de rango [0, 20] dB: {implementation_loss_db}")

    # Paso 1: Calcular ganancias de antenas (usando función existente)
    tx_gain_dbi = calculate_gain(tx_antenna_diameter_m, frequency_ghz, tx_antenna_efficiency)
    rx_gain_dbi = calculate_gain(rx_antenna_diameter_m, frequency_ghz, rx_antenna_efficiency)

    # Paso 2: Calcular pérdida en espacio libre
    fspl_db = calculate_free_space_path_loss(distance_km, frequency_ghz)

    # Paso 3: Calcular potencia recibida (ecuación de Friis)
    # P_rx = P_tx + G_tx + G_rx - FSPL - L_impl
    rx_power_dbm = (
        tx_power_dbm
        + tx_gain_dbi
        + rx_gain_dbi
        - fspl_db
        - implementation_loss_db
    )

    # Paso 4: Calcular margen del link
    # Link Margin = P_rx - (RX_sensitivity + SNR_required + Fade_margin)
    # Si Link Margin > 0, el link es viable
    # Si Link Margin >= min_link_margin_db, el link es robusto/confiable
    link_margin_db = rx_power_dbm - (rx_sensitivity_dbm + required_snr_db + fade_margin_db)

    # Paso 5: Determinar viabilidad
    is_viable = link_margin_db >= min_link_margin_db

    # Retornar resultado completo
    return LinkBudgetResult(
        tx_power_dbm=tx_power_dbm,
        tx_antenna_gain_dbi=float(tx_gain_dbi),
        rx_antenna_gain_dbi=float(rx_gain_dbi),
        free_space_loss_db=float(fspl_db),
        implementation_loss_db=implementation_loss_db,
        rx_power_dbm=float(rx_power_dbm),
        rx_sensitivity_dbm=rx_sensitivity_dbm,
        required_snr_db=required_snr_db,
        fade_margin_db=fade_margin_db,
        link_margin_db=float(link_margin_db),
        is_viable=is_viable,
    )


def validate_range_feasibility(
    min_antenna_diameter_m: float,
    max_antenna_diameter_m: float,
    desired_range_km: float,
    frequency_ghz: float,
    antenna_efficiency: float,
    tx_power_dbm: float,
    rx_sensitivity_dbm: float,
    required_snr_db: float,
    fade_margin_db: float,
    implementation_loss_db: float,
    min_link_margin_db: float = 6.0,
) -> Tuple[bool, str, LinkBudgetResult]:
    """
    Valida si el alcance deseado es físicamente alcanzable con los parámetros dados.

    Calcula el link budget usando la antena MÁS GRANDE posible (max_diameter)
    para verificar el mejor caso. Si incluso con la antena más grande no se
    alcanza el rango deseado, entonces las restricciones son incompatibles.

    Args:
        min_antenna_diameter_m: Diámetro mínimo de antena en metros
        max_antenna_diameter_m: Diámetro máximo de antena en metros
        desired_range_km: Alcance deseado en kilómetros
        frequency_ghz: Frecuencia de operación en GHz
        antenna_efficiency: Eficiencia de apertura (0-1)
        tx_power_dbm: Potencia de transmisión en dBm
        rx_sensitivity_dbm: Sensibilidad del receptor en dBm
        required_snr_db: SNR mínimo requerido en dB
        fade_margin_db: Margen para desvanecimiento en dB
        implementation_loss_db: Pérdidas de implementación en dB
        min_link_margin_db: Margen mínimo aceptable (default: 6 dB)

    Returns:
        Tupla de (is_feasible, message, link_budget_result):
        - is_feasible: True si el alcance es alcanzable
        - message: Mensaje explicativo (vacío si es viable, diagnóstico si no)
        - link_budget_result: Resultado completo del link budget

    Examples:
        >>> feasible, msg, result = validate_range_feasibility(
        ...     min_antenna_diameter_m=0.1,
        ...     max_antenna_diameter_m=2.0,
        ...     desired_range_km=50.0,  # Muy lejos
        ...     frequency_ghz=2.4,
        ...     antenna_efficiency=0.6,
        ...     tx_power_dbm=20.0,
        ...     rx_sensitivity_dbm=-95.0,
        ...     required_snr_db=10.0,
        ...     fade_margin_db=10.0,
        ...     implementation_loss_db=3.0
        ... )
        >>> print(f"Factible: {feasible}")
        >>> if not feasible:
        ...     print(msg)
    """
    # Calcular link budget con la antena MÁS GRANDE (mejor caso)
    # Asumimos que TX y RX usan la misma antena optimizada
    best_case_result = calculate_link_budget(
        distance_km=desired_range_km,
        frequency_ghz=frequency_ghz,
        tx_antenna_diameter_m=max_antenna_diameter_m,
        rx_antenna_diameter_m=max_antenna_diameter_m,
        tx_antenna_efficiency=antenna_efficiency,
        rx_antenna_efficiency=antenna_efficiency,
        tx_power_dbm=tx_power_dbm,
        rx_sensitivity_dbm=rx_sensitivity_dbm,
        required_snr_db=required_snr_db,
        fade_margin_db=fade_margin_db,
        implementation_loss_db=implementation_loss_db,
        min_link_margin_db=min_link_margin_db,
    )

    if best_case_result.is_viable:
        # El link es viable incluso en el mejor caso
        return True, "", best_case_result

    # El link NO es viable. Generar mensaje diagnóstico detallado
    shortage_db = min_link_margin_db - best_case_result.link_margin_db

    # Calcular cuánto más de ganancia se necesitaría
    # (aproximadamente equivalente a cuánto más grande debería ser la antena)
    additional_gain_needed_db = shortage_db

    # Estimar el tamaño de antena necesario
    # Ganancia escala con (D/λ)², entonces en dB: G_dB ∝ 20·log₁₀(D)
    # Para ganar X dB más: D_new = D_old · 10^(X/20)
    gain_ratio = 10.0 ** (additional_gain_needed_db / 20.0)
    required_diameter_m = max_antenna_diameter_m * gain_ratio

    # Calcular el rango máximo alcanzable con la antena actual
    # FSPL = 20·log₁₀(d) + 20·log₁₀(f) + 92.45
    # Si reducimos FSPL en shortage_db, podemos calcular el nuevo rango:
    # 20·log₁₀(d_max) = FSPL_current - shortage_db - 20·log₁₀(f) - 92.45
    current_fspl = best_case_result.free_space_loss_db
    achievable_fspl = current_fspl - shortage_db
    # FSPL = 20·log₁₀(d) + 20·log₁₀(f) + 92.45
    # => log₁₀(d) = (FSPL - 20·log₁₀(f) - 92.45) / 20
    log10_d_max = (achievable_fspl - 20.0 * np.log10(frequency_ghz) - 92.45) / 20.0
    achievable_range_km = 10.0 ** log10_d_max

    # Mensaje diagnóstico
    message = (
        f"El alcance de {desired_range_km:.1f} km NO es alcanzable con los parámetros dados.\n\n"
        f"**Análisis del Link Budget (Mejor Caso):**\n"
        f"- Antena máxima: {max_antenna_diameter_m:.2f} m\n"
        f"- Ganancia TX: {best_case_result.tx_antenna_gain_dbi:.1f} dBi\n"
        f"- Ganancia RX: {best_case_result.rx_antenna_gain_dbi:.1f} dBi\n"
        f"- Pérdida espacio libre: {best_case_result.free_space_loss_db:.1f} dB\n"
        f"- Potencia recibida: {best_case_result.rx_power_dbm:.1f} dBm\n"
        f"- Margen del link: {best_case_result.link_margin_db:.1f} dB "
        f"(requiere ≥ {min_link_margin_db:.1f} dB)\n"
        f"- **Déficit: {shortage_db:.1f} dB**\n\n"
        f"**Soluciones posibles:**\n"
        f"1. Reducir alcance a **{achievable_range_km:.2f} km** o menos\n"
        f"2. Usar antenas de al menos **{required_diameter_m:.2f} m** de diámetro\n"
        f"3. Aumentar potencia TX en **{shortage_db:.1f} dB** (actualmente {tx_power_dbm:.0f} dBm)\n"
        f"4. Usar receptor más sensible (actual: {rx_sensitivity_dbm:.0f} dBm, "
        f"necesario: {rx_sensitivity_dbm - shortage_db:.0f} dBm)\n"
        f"5. Reducir márgenes de seguridad (fade: {fade_margin_db:.0f} dB, "
        f"SNR: {required_snr_db:.0f} dB)"
    )

    return False, message, best_case_result
