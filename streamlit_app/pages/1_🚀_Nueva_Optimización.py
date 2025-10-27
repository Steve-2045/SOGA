"""
Nueva Optimización - SOGA Dashboard
====================================

Interactive page for configuring and executing antenna optimization simulations.
Provides real-time visualization of results with interactive Plotly charts.

Author: SOGA Development Team
License: MIT
"""

import io
import json
import sys
from pathlib import Path
from typing import Any, Dict

import plotly.graph_objects as go
import streamlit as st

# Ensure the backend is importable
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from soga.app.facade import ApplicationFacade, FacadeValidationError
from soga.infrastructure.config import get_config
from soga.infrastructure.file_io import ResultsExporter

# Page configuration
st.set_page_config(
    page_title="Nueva Optimización - SOGA",
    page_icon="🚀",
    layout="wide",
)


def load_configuration():
    """Load SOGA configuration with caching to avoid redundant reads."""
    if "config" not in st.session_state:
        st.session_state.config = get_config()
    return st.session_state.config


def create_convergence_plot(convergence_history: list[float]) -> go.Figure:
    """
    Create an interactive Plotly line chart for convergence history.

    Args:
        convergence_history: List of best gain values per generation

    Returns:
        Plotly Figure object
    """
    generations = list(range(len(convergence_history)))

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=generations,
            y=convergence_history,
            mode="lines+markers",
            name="Mejor Ganancia",
            line={"color": "#667eea", "width": 3},
            marker={"size": 6, "color": "#667eea"},
            hovertemplate="<b>Generación %{x}</b><br>Ganancia: %{y:.2f} dBi<extra></extra>",
        )
    )

    fig.update_layout(
        title={
            "text": "Convergencia del Algoritmo NSGA-II",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20, "color": "#e2e8f0"},
        },
        xaxis={
            "title": "Generación",
            "gridcolor": "#2d3748",
            "color": "#e2e8f0",
        },
        yaxis={
            "title": "Mejor Ganancia (dBi)",
            "gridcolor": "#2d3748",
            "color": "#e2e8f0",
        },
        plot_bgcolor="#1a1f2e",
        paper_bgcolor="#1a1f2e",
        font={"color": "#e2e8f0"},
        hovermode="x unified",
        showlegend=False,
    )

    return fig


def create_pareto_front_plot(pareto_front: list, optimal_point: dict) -> go.Figure:
    """
    Create an interactive Plotly scatter plot for the Pareto front.

    Args:
        pareto_front: List of ParetoPoint objects from optimization
        optimal_point: Dictionary with the selected knee point data

    Returns:
        Plotly Figure object
    """
    if not pareto_front:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No hay datos del frente de Pareto disponibles",
            plot_bgcolor="#1a1f2e",
            paper_bgcolor="#1a1f2e",
        )
        return fig

    # Extract data from pareto_front
    weights_kg = [point.weight for point in pareto_front]
    gains_dbi = [point.gain for point in pareto_front]
    diameters_m = [point.diameter for point in pareto_front]
    fd_ratios = [point.f_d_ratio for point in pareto_front]

    # Convert weights to grams for display
    weights_g = [w * 1000 for w in weights_kg]

    # Optimal point weight in grams
    optimal_weight_kg = (
        optimal_point["optimal_diameter_mm"] / 1000
    ) ** 2 * 3.14159 * 1.8 / 4  # Approximate
    optimal_weight_g = optimal_weight_kg * 1000
    optimal_gain = optimal_point["expected_gain_dbi"]

    # Create hover text with detailed information
    hover_texts = [
        f"<b>Ganancia:</b> {gain:.2f} dBi<br>"
        f"<b>Peso:</b> {weight:.1f} g<br>"
        f"<b>Diámetro:</b> {diameter*1000:.1f} mm<br>"
        f"<b>f/D:</b> {fd:.3f}"
        for gain, weight, diameter, fd in zip(gains_dbi, weights_g, diameters_m, fd_ratios)
    ]

    fig = go.Figure()

    # Add all Pareto solutions as scatter points
    fig.add_trace(
        go.Scatter(
            x=weights_g,
            y=gains_dbi,
            mode="markers",
            name="Soluciones Pareto",
            marker={
                "size": 8,
                "color": "#667eea",
                "opacity": 0.6,
                "line": {"width": 1, "color": "#4c51bf"},
            },
            hovertext=hover_texts,
            hovertemplate="%{hovertext}<extra></extra>",
        )
    )

    # Highlight the knee point (optimal solution)
    fig.add_trace(
        go.Scatter(
            x=[optimal_weight_g],
            y=[optimal_gain],
            mode="markers",
            name="Knee Point (Óptimo)",
            marker={
                "size": 16,
                "color": "#f56565",
                "symbol": "star",
                "line": {"width": 2, "color": "#c53030"},
            },
            hovertemplate=(
                f"<b>SOLUCIÓN ÓPTIMA (Knee Point)</b><br>"
                f"<b>Ganancia:</b> {optimal_gain:.2f} dBi<br>"
                f"<b>Peso:</b> {optimal_weight_g:.1f} g<br>"
                f"<b>Diámetro:</b> {optimal_point['optimal_diameter_mm']:.1f} mm<br>"
                f"<b>f/D:</b> {optimal_point['f_d_ratio']:.3f}"
                "<extra></extra>"
            ),
        )
    )

    # Update layout with professional styling
    fig.update_layout(
        title={
            "text": "Frente de Pareto: Ganancia vs Peso",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20, "color": "#e2e8f0"},
        },
        xaxis={
            "title": "Peso de la Antena (g)",
            "gridcolor": "#2d3748",
            "color": "#e2e8f0",
            "showgrid": True,
        },
        yaxis={
            "title": "Ganancia (dBi)",
            "gridcolor": "#2d3748",
            "color": "#e2e8f0",
            "showgrid": True,
        },
        plot_bgcolor="#1a1f2e",
        paper_bgcolor="#1a1f2e",
        font={"color": "#e2e8f0"},
        hovermode="closest",
        showlegend=True,
        legend={
            "x": 0.02,
            "y": 0.98,
            "bgcolor": "rgba(26, 31, 46, 0.8)",
            "bordercolor": "#667eea",
            "borderwidth": 1,
        },
        height=600,
    )

    return fig


def diagnose_infeasibility(user_parameters: dict, config) -> dict:
    """
    Diagnose why the optimization is infeasible and provide specific feedback.

    Args:
        user_parameters: Dictionary with user-provided parameters
        config: Application configuration object

    Returns:
        Dictionary with diagnosis information including:
        - main_issue: Primary problem identifier
        - conflicts: List of specific conflicts found
        - suggestions: Actionable recommendations
        - severity: How critical each issue is
    """
    diagnosis = {
        "main_issue": None,
        "conflicts": [],
        "suggestions": [],
        "severity": "unknown",
    }

    # Extract parameters
    min_d = user_parameters["min_diameter_m"]
    max_d = user_parameters["max_diameter_m"]
    max_weight_g = user_parameters["max_payload_g"]
    min_fd = user_parameters["min_f_d_ratio"]
    max_fd = user_parameters["max_f_d_ratio"]
    range_km = user_parameters["desired_range_km"]

    # Get physical constants from config
    areal_density = config.simulation.areal_density_kg_per_m2  # kg/m²
    frequency_ghz = config.simulation.frequency_ghz

    # Use numpy pi for precision
    import numpy as np
    pi = np.pi

    # Calculate minimum possible weight with minimum diameter
    min_area = pi * (min_d / 2) ** 2
    min_weight_kg = min_area * areal_density
    min_weight_g_calc = min_weight_kg * 1000

    # Calculate maximum possible weight with maximum diameter
    max_area = pi * (max_d / 2) ** 2
    max_weight_kg = max_area * areal_density
    max_weight_g_calc = max_weight_kg * 1000

    # Calculate weight for mid-range diameter
    mid_d = (min_d + max_d) / 2
    mid_area = pi * (mid_d / 2) ** 2
    mid_weight_g = mid_area * areal_density * 1000

    # --- DIAGNOSIS 1: Weight constraint absolutely impossible ---
    # The lightest possible antenna (minimum diameter) is heavier than max allowed
    if min_weight_g_calc > max_weight_g:
        diagnosis["main_issue"] = "weight_impossible"
        diagnosis["severity"] = "critical"

        # Calculate what diameter would fit the weight constraint
        feasible_d = 2 * np.sqrt(max_weight_g / 1000 / areal_density / pi)

        diagnosis["conflicts"].append(
            {
                "title": "❌ Restricción de Peso Física­mente Imposible",
                "description": (
                    f"**Problema crítico**: Incluso la antena MÁS PEQUEÑA de tu rango ({min_d:.3f} m) "
                    f"pesa aproximadamente **{min_weight_g_calc:.1f} g**, pero tu límite de peso es solo **{max_weight_g:.0f} g**.\n\n"
                    f"Para que una antena pese {max_weight_g:.0f} g, su diámetro máximo sería **{feasible_d:.3f} m**, "
                    f"que está **por debajo** de tu diámetro mínimo ({min_d:.3f} m)."
                ),
                "calculation": (
                    f"Peso_mínimo = π × (D_min/2)² × densidad_areal\n"
                    f"           = π × ({min_d:.3f}/2)² × {areal_density:.3f} kg/m²\n"
                    f"           = {min_weight_g_calc:.1f} g\n\n"
                    f"Diámetro factible para {max_weight_g:.0f} g:\n"
                    f"D_factible = 2 × √({max_weight_g:.0f}g ÷ 1000 ÷ {areal_density:.3f} ÷ π)\n"
                    f"          = {feasible_d:.3f} m"
                ),
                "type": "critical",
            }
        )

        weight_increase_needed = int(min_weight_g_calc * 1.2)
        diagnosis["suggestions"].append(
            f"✅ **SOLUCIÓN 1**: Aumentar peso máximo a **{weight_increase_needed} g** (mínimo: {int(min_weight_g_calc)} g)"
        )
        diagnosis["suggestions"].append(
            f"✅ **SOLUCIÓN 2**: Reducir diámetro mínimo a **{feasible_d:.3f} m** o menos"
        )
        diagnosis["suggestions"].append(
            f"✅ **SOLUCIÓN 3**: Ajustar ambos: Diámetro 0.05-{max_d:.2f} m + Peso {int(mid_weight_g * 1.5)} g"
        )
        return diagnosis

    # --- DIAGNOSIS 2: Weight allows only small portion of diameter range ---
    # The weight constraint cuts off too much of the specified diameter range
    feasible_max_d = 2 * np.sqrt(max_weight_g / 1000 / areal_density / pi)
    usable_range_fraction = (feasible_max_d - min_d) / (max_d - min_d) if max_d > min_d else 0

    if feasible_max_d < max_d and usable_range_fraction < 0.3:
        diagnosis["main_issue"] = "weight_cuts_diameter_range"
        diagnosis["severity"] = "high"

        diagnosis["conflicts"].append(
            {
                "title": "⚠️ Peso Máximo Incompatible con Rango de Diámetros",
                "description": (
                    f"Tu peso máximo ({max_weight_g:.0f} g) permite antenas de hasta **{feasible_max_d:.3f} m**, "
                    f"pero tu rango de diámetros va hasta **{max_d:.2f} m**.\n\n"
                    f"Esto significa que **{(1-usable_range_fraction)*100:.0f}% de tu rango de diámetros** "
                    f"es inaccesible debido a la restricción de peso. El algoritmo tiene muy poco espacio "
                    f"para optimizar (solo puede usar diámetros entre {min_d:.3f} m y {feasible_max_d:.3f} m)."
                ),
                "calculation": (
                    f"Diámetro máximo factible con {max_weight_g:.0f} g:\n"
                    f"D_max_factible = 2 × √({max_weight_g:.0f}g ÷ 1000 ÷ {areal_density:.3f} ÷ π)\n"
                    f"              = {feasible_max_d:.3f} m\n\n"
                    f"Rango solicitado: {min_d:.3f} m - {max_d:.2f} m ({max_d - min_d:.3f} m)\n"
                    f"Rango utilizable: {min_d:.3f} m - {feasible_max_d:.3f} m ({max(0, feasible_max_d - min_d):.3f} m)\n"
                    f"Porcentaje utilizable: {usable_range_fraction*100:.0f}%"
                ),
                "type": "high",
            }
        )

        needed_weight = int(max_weight_g_calc * 1.1)
        diagnosis["suggestions"].append(
            f"✅ **OPCIÓN A**: Reducir diámetro máximo a **{feasible_max_d:.2f} m** (factible con peso actual)"
        )
        diagnosis["suggestions"].append(
            f"✅ **OPCIÓN B**: Aumentar peso máximo a **{needed_weight} g** (para usar rango completo)"
        )
        diagnosis["suggestions"].append(
            f"✅ **OPCIÓN C** (balanceada): Diámetro hasta **{(feasible_max_d + max_d)/2:.2f} m** + Peso **{int((max_weight_g + needed_weight)/2)} g**"
        )

    # --- DIAGNOSIS 3: f/D range too narrow for optimization ---
    fd_range = max_fd - min_fd
    if fd_range < 0.15 and diagnosis["main_issue"] is None:
        diagnosis["main_issue"] = "fd_range_too_narrow"
        diagnosis["severity"] = "medium"

        diagnosis["conflicts"].append(
            {
                "title": "⚠️ Rango f/D Demasiado Estrecho",
                "description": (
                    f"Tu rango de relación focal f/D es **{min_fd:.2f} - {max_fd:.2f}** (amplitud: {fd_range:.2f}).\n\n"
                    f"Esto es muy restrictivo. El algoritmo NSGA-II necesita explorar diferentes geometrías "
                    f"de parábola (más profundas o más planas) para optimizar el balance ganancia/peso. "
                    f"Un rango recomendado es al menos **0.3** de amplitud (por ejemplo, 0.3-0.7)."
                ),
                "calculation": (
                    f"Rango actual f/D: {fd_range:.2f}\n"
                    f"Rango recomendado: ≥ 0.30\n"
                    f"Flexibilidad: {(fd_range/0.3)*100:.0f}% de lo recomendado"
                ),
                "type": "medium",
            }
        )

        suggested_min_fd = max(0.25, min_fd - 0.15)
        suggested_max_fd = min(1.0, max_fd + 0.15)
        diagnosis["suggestions"].append(
            f"✅ Ampliar rango f/D a **{suggested_min_fd:.2f} - {suggested_max_fd:.2f}** (más flexible)"
        )
        diagnosis["suggestions"].append(
            f"✅ O usar rango estándar: **0.35 - 0.70** (cubre geometrías típicas óptimas)"
        )

    # --- DIAGNOSIS 4: Diameter range too narrow ---
    d_range = max_d - min_d
    if d_range < 0.2 and diagnosis["main_issue"] is None:
        diagnosis["main_issue"] = "diameter_range_too_narrow"
        diagnosis["severity"] = "medium"

        diagnosis["conflicts"].append(
            {
                "title": "⚠️ Rango de Diámetro Muy Limitado",
                "description": (
                    f"Tu rango de diámetros es **{min_d:.3f} m - {max_d:.2f} m** (amplitud: {d_range:.3f} m).\n\n"
                    f"Un rango tan estrecho limita la capacidad del algoritmo de encontrar soluciones óptimas. "
                    f"Se recomienda un rango mínimo de **0.5 m** para permitir exploración efectiva del espacio de diseño."
                ),
                "calculation": (
                    f"Rango actual: {d_range:.3f} m\n"
                    f"Rango recomendado: ≥ 0.5 m\n"
                    f"Flexibilidad: {(d_range/0.5)*100:.0f}% de lo recomendado"
                ),
                "type": "medium",
            }
        )

        # Check if we can expand without violating weight
        suggested_max_d = min(3.0, min_d + 0.8)
        suggested_weight = int(pi * (suggested_max_d/2)**2 * areal_density * 1000 * 1.2)

        if suggested_max_d * 1000 * areal_density * pi / 4 <= max_weight_g / 1000:
            diagnosis["suggestions"].append(
                f"✅ Ampliar diámetro máximo a **{suggested_max_d:.2f} m** (compatible con tu peso actual)"
            )
        else:
            diagnosis["suggestions"].append(
                f"✅ Ampliar diámetro a **{max(0.1, min_d*0.7):.2f} m - {min(3.0, max_d*1.8):.2f} m** + aumentar peso a **{suggested_weight} g**"
            )

    # --- DIAGNOSIS 5: Range requirement vs antenna size mismatch ---
    # Estimate required gain for the desired range using simplified link budget
    # This is approximate but gives users actionable feedback
    if range_km > 15:
        # Rough estimate: each 10km requires ~6dBi more gain
        # Gain scales with (D*f)^2, so gain_dB ≈ 20*log10(D*f_GHz) + K
        # For 2.4GHz, a 1m dish gives ~27dBi

        # Simple model: gain needed ≈ 20 + 3*range_km (very rough)
        approx_gain_needed = 20 + 2 * range_km

        # Estimate diameter needed (rough: gain ≈ 20*log10(D*f_GHz*3.54))
        # Simplified: D_needed ≈ 10^((gain_needed - 7)/20) / f_GHz
        d_needed_for_range = 10**((approx_gain_needed - 7) / 20) / frequency_ghz

        if d_needed_for_range > max_d * 1.5 and diagnosis["main_issue"] is None:
            diagnosis["main_issue"] = "range_requires_larger_antenna"
            diagnosis["severity"] = "high"

            # What range is achievable with current max diameter?
            max_gain_achievable = 20 * np.log10(max_d * frequency_ghz * 3.54) + 7
            achievable_range = (max_gain_achievable - 20) / 2

            diagnosis["conflicts"].append(
                {
                    "title": "⚠️ Alcance Incompatible con Tamaño de Antena",
                    "description": (
                        f"Tu alcance deseado es **{range_km:.1f} km**, lo que requiere alta ganancia.\n\n"
                        f"Con tu diámetro máximo actual ({max_d:.2f} m), el alcance máximo estimado es "
                        f"aproximadamente **{achievable_range:.1f} km** en condiciones ideales.\n\n"
                        f"Para alcanzar {range_km:.1f} km confiablemente, necesitarías una antena de al menos "
                        f"**{d_needed_for_range:.2f} m** de diámetro."
                    ),
                    "calculation": (
                        f"Estimación de alcance con D={max_d:.2f}m:\n"
                        f"Ganancia máxima ≈ {max_gain_achievable:.1f} dBi\n"
                        f"Alcance estimado ≈ {achievable_range:.1f} km\n\n"
                        f"Para {range_km:.1f} km:\n"
                        f"Ganancia requerida ≈ {approx_gain_needed:.1f} dBi\n"
                        f"Diámetro necesario ≈ {d_needed_for_range:.2f} m"
                    ),
                    "type": "high",
                }
            )

            diagnosis["suggestions"].append(
                f"✅ **OPCIÓN 1**: Reducir alcance objetivo a **{achievable_range:.1f} km** (factible con D={max_d:.2f}m)"
            )
            diagnosis["suggestions"].append(
                f"✅ **OPCIÓN 2**: Aumentar diámetro máximo a **{d_needed_for_range:.1f} m** o más"
            )
            diagnosis["suggestions"].append(
                f"✅ **OPCIÓN 3**: Balance intermedio: Alcance **{(range_km + achievable_range)/2:.1f} km** + Diámetro hasta **{(max_d + d_needed_for_range)/2:.1f} m**"
            )

    # --- DIAGNOSIS 6: General over-constrained problem ---
    # Multiple moderate issues combine to make problem infeasible
    if diagnosis["main_issue"] is None:
        diagnosis["main_issue"] = "general_over_constrained"
        diagnosis["severity"] = "medium"

        # Calculate "constraint tightness" metrics
        weight_tightness = max_weight_g / max_weight_g_calc  # closer to 0 = tighter
        d_range_adequacy = d_range / 1.0  # compared to 1m ideal range
        fd_range_adequacy = fd_range / 0.4  # compared to 0.4 ideal range

        diagnosis["conflicts"].append(
            {
                "title": "⚠️ Espacio de Búsqueda Sobre-Restringido",
                "description": (
                    f"Tus restricciones son individualmente válidas, pero en conjunto crean un espacio "
                    f"de búsqueda muy limitado para el algoritmo genético NSGA-II.\n\n"
                    f"**Análisis de restricciones**:\n"
                    f"- Peso: {max_weight_g:.0f}g (holgura: {weight_tightness*100:.0f}% del máximo posible)\n"
                    f"- Rango de diámetro: {d_range:.3f}m (adecuación: {d_range_adequacy*100:.0f}% de lo ideal)\n"
                    f"- Rango f/D: {fd_range:.2f} (adecuación: {fd_range_adequacy*100:.0f}% de lo ideal)\n\n"
                    f"El algoritmo necesita más libertad en al menos 2 de estas dimensiones para encontrar "
                    f"soluciones óptimas en el frente de Pareto."
                ),
                "calculation": (
                    f"Configuración actual:\n"
                    f"  • Diámetro: {min_d:.3f} - {max_d:.2f} m\n"
                    f"  • Peso: ≤ {max_weight_g:.0f} g\n"
                    f"  • f/D: {min_fd:.2f} - {max_fd:.2f}\n"
                    f"  • Alcance: {range_km:.1f} km\n\n"
                    f"Métricas de restricción:\n"
                    f"  • Holgura de peso: {weight_tightness*100:.0f}%\n"
                    f"  • Flexibilidad diámetro: {d_range_adequacy*100:.0f}%\n"
                    f"  • Flexibilidad f/D: {fd_range_adequacy*100:.0f}%"
                ),
                "type": "medium",
            }
        )

        # Provide a relaxed configuration
        relaxed_max_d = min(3.0, max_d * 1.4)
        relaxed_weight = int(pi * (relaxed_max_d/2)**2 * areal_density * 1000 * 1.2)
        relaxed_min_fd = max(0.25, min_fd - 0.1)
        relaxed_max_fd = min(1.0, max_fd + 0.1)

        diagnosis["suggestions"].append(
            "✅ **SOLUCIÓN**: Relajar múltiples restricciones simultáneamente para dar espacio al algoritmo:"
        )
        diagnosis["suggestions"].append(
            f"   • Diámetro: **{min_d:.2f} - {relaxed_max_d:.2f} m** (más rango)"
        )
        diagnosis["suggestions"].append(
            f"   • Peso: **{relaxed_weight} g** (más holgura)"
        )
        diagnosis["suggestions"].append(
            f"   • f/D: **{relaxed_min_fd:.2f} - {relaxed_max_fd:.2f}** (más flexibilidad geométrica)"
        )
        diagnosis["suggestions"].append(
            f"   • Alcance: **{range_km * 0.8:.1f} km** (más realista) o mantener {range_km:.1f} km si aumentas el diámetro"
        )

    return diagnosis


def create_parabola_geometry_plot(
    diameter_mm: float, focal_length_mm: float, depth_mm: float
) -> go.Figure:
    """
    Create an interactive 2D plot showing the parabolic antenna geometry.

    Args:
        diameter_mm: Antenna diameter in millimeters
        focal_length_mm: Focal length in millimeters
        depth_mm: Parabola depth in millimeters

    Returns:
        Plotly Figure object with parabola cross-section
    """
    import numpy as np

    # Convert to meters for calculation
    diameter_m = diameter_mm / 1000.0
    focal_length_m = focal_length_mm / 1000.0
    depth_m = depth_mm / 1000.0

    # Calculate parabola points
    # Parabola equation: z = x^2 / (4*f)
    # where f is the focal length
    radius_m = diameter_m / 2.0
    x_points = np.linspace(-radius_m, radius_m, 200)
    z_points = (x_points**2) / (4.0 * focal_length_m)

    # Create figure
    fig = go.Figure()

    # Plot parabola surface
    fig.add_trace(
        go.Scatter(
            x=x_points * 1000,  # Convert to mm
            y=z_points * 1000,  # Convert to mm
            mode="lines",
            name="Superficie Parabólica",
            line={"color": "#667eea", "width": 4},
            fill="tozeroy",
            fillcolor="rgba(102, 126, 234, 0.2)",
            hovertemplate="x: %{x:.1f} mm<br>z: %{y:.1f} mm<extra></extra>",
        )
    )

    # Add aperture line (diameter)
    fig.add_trace(
        go.Scatter(
            x=[-radius_m * 1000, radius_m * 1000],
            y=[0, 0],
            mode="lines",
            name="Apertura",
            line={"color": "#48bb78", "width": 3, "dash": "dash"},
            hoverinfo="skip",
        )
    )

    # Add focal point
    fig.add_trace(
        go.Scatter(
            x=[0],
            y=[focal_length_m * 1000],
            mode="markers+text",
            name="Punto Focal",
            marker={"color": "#f56565", "size": 12, "symbol": "star"},
            text=["F"],
            textposition="top center",
            textfont={"size": 14, "color": "#f56565"},
            hovertemplate="Punto Focal<br>z: %{y:.1f} mm<extra></extra>",
        )
    )

    # Add depth indicator line
    fig.add_trace(
        go.Scatter(
            x=[0, 0],
            y=[0, depth_m * 1000],
            mode="lines",
            name="Profundidad",
            line={"color": "#ed8936", "width": 2, "dash": "dot"},
            hoverinfo="skip",
        )
    )

    # Add diameter indicator
    fig.add_shape(
        type="line",
        x0=-radius_m * 1000,
        y0=-depth_m * 1000 * 0.1,
        x1=radius_m * 1000,
        y1=-depth_m * 1000 * 0.1,
        line={"color": "#48bb78", "width": 2},
    )

    # Add dimension annotations
    fig.add_annotation(
        x=0,
        y=-depth_m * 1000 * 0.2,
        text=f"D = {diameter_mm:.1f} mm",
        showarrow=False,
        font={"size": 12, "color": "#48bb78"},
        bgcolor="rgba(26, 31, 46, 0.8)",
        bordercolor="#48bb78",
        borderwidth=1,
    )

    fig.add_annotation(
        x=radius_m * 1000 * 1.15,
        y=depth_m * 1000 / 2,
        text=f"h = {depth_mm:.1f} mm",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#ed8936",
        ax=60,  # Increased from 40 to move annotation box further right
        ay=0,
        font={"size": 12, "color": "#ed8936"},
        bgcolor="rgba(26, 31, 46, 0.8)",
        bordercolor="#ed8936",
        borderwidth=1,
    )

    fig.add_annotation(
        x=-radius_m * 1000 * 0.2,
        y=focal_length_m * 1000 * 1.1,
        text=f"f = {focal_length_mm:.1f} mm",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#f56565",
        ax=-30,
        ay=-30,
        font={"size": 12, "color": "#f56565"},
        bgcolor="rgba(26, 31, 46, 0.8)",
        bordercolor="#f56565",
        borderwidth=1,
    )

    # Update layout
    fig.update_layout(
        title={
            "text": "Geometría de la Antena Parabólica (Vista en Corte)",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18, "color": "#e2e8f0"},
        },
        xaxis={
            "title": "Distancia Radial (mm)",
            "gridcolor": "#2d3748",
            "color": "#e2e8f0",
            "zeroline": True,
            "zerolinecolor": "#4a5568",
            "zerolinewidth": 2,
        },
        yaxis={
            "title": "Profundidad Axial (mm)",
            "gridcolor": "#2d3748",
            "color": "#e2e8f0",
            "zeroline": True,
            "zerolinecolor": "#4a5568",
            "zerolinewidth": 2,
            "scaleanchor": "x",  # Equal aspect ratio for accurate representation
            "scaleratio": 1,
        },
        plot_bgcolor="#1a1f2e",
        paper_bgcolor="#1a1f2e",
        font={"color": "#e2e8f0"},
        hovermode="closest",
        showlegend=True,
        legend={
            "x": 0.02,
            "y": 0.98,
            "bgcolor": "rgba(26, 31, 46, 0.8)",
            "bordercolor": "#667eea",
            "borderwidth": 1,
        },
        height=500,
    )

    return fig


def export_convergence_to_bytes(convergence_history: list[float]) -> bytes:
    """
    Export convergence history to CSV format in memory.

    Args:
        convergence_history: List of best gain values per generation

    Returns:
        CSV data as bytes
    """
    buffer = io.BytesIO()
    temp_path = Path("temp_convergence.csv")

    try:
        # Write to temporary file
        ResultsExporter.export_convergence_to_csv(convergence_history, temp_path)

        # Read back as bytes
        with open(temp_path, "rb") as f:
            csv_data = f.read()

        return csv_data
    finally:
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()


def validate_user_inputs(user_parameters: dict, config) -> tuple[bool, list[str], list[str]]:
    """
    Valida los parámetros del usuario antes de ejecutar la optimización.

    Realiza validaciones de sentido común, consistencia física, y detecta
    problemas obvios que harían que la optimización falle.

    Args:
        user_parameters: Parámetros proporcionados por el usuario
        config: Configuración de la aplicación

    Returns:
        Tuple de (es_válido, lista_errores, lista_advertencias)
        - es_válido: True si pasa todas las validaciones críticas
        - lista_errores: Lista de errores críticos que bloquean la ejecución
        - lista_advertencias: Lista de advertencias que no bloquean pero sugieren problemas
    """
    errors = []
    warnings_list = []

    # Extraer parámetros
    min_d = user_parameters["min_diameter_m"]
    max_d = user_parameters["max_diameter_m"]
    max_weight_g = user_parameters["max_payload_g"]
    min_fd = user_parameters["min_f_d_ratio"]
    max_fd = user_parameters["max_f_d_ratio"]
    range_km = user_parameters["desired_range_km"]

    # --- VALIDACIÓN 1: Rangos lógicos (min <= max) ---
    if min_d >= max_d:
        errors.append(
            f"**Diámetro inválido**: El diámetro mínimo ({min_d:.3f} m) debe ser "
            f"**menor** que el máximo ({max_d:.3f} m). Por favor, ajuste los valores."
        )

    if min_fd >= max_fd:
        errors.append(
            f"**Relación f/D inválida**: El valor mínimo ({min_fd:.2f}) debe ser "
            f"**menor** que el máximo ({max_fd:.2f}). Por favor, ajuste los valores."
        )

    # --- VALIDACIÓN 2: Valores positivos ---
    if min_d <= 0 or max_d <= 0:
        errors.append(
            f"**Diámetro inválido**: Los diámetros deben ser **positivos**. "
            f"Valores actuales: mín={min_d:.3f} m, máx={max_d:.3f} m"
        )

    if max_weight_g <= 0:
        errors.append(
            f"**Peso inválido**: El peso máximo debe ser **positivo**. "
            f"Valor actual: {max_weight_g:.0f} g"
        )

    if min_fd <= 0 or max_fd <= 0:
        errors.append(
            f"**Relación f/D inválida**: Los valores f/D deben ser **positivos**. "
            f"Valores actuales: mín={min_fd:.2f}, máx={max_fd:.2f}"
        )

    # Si hay errores básicos, no continuar con validaciones físicas
    if errors:
        return False, errors, warnings_list

    # --- VALIDACIÓN 3: Peso vs Diámetro (física básica) ---
    import numpy as np
    pi = np.pi
    areal_density = config.simulation.areal_density_kg_per_m2

    # Peso mínimo posible con el diámetro mínimo
    min_area = pi * (min_d / 2) ** 2
    min_possible_weight_g = min_area * areal_density * 1000

    if min_possible_weight_g > max_weight_g:
        # ERROR CRÍTICO: Imposible físicamente
        feasible_d = 2 * np.sqrt(max_weight_g / 1000 / areal_density / pi)
        errors.append(
            f"**Restricción de peso físicamente imposible**: La antena más pequeña "
            f"que puedes crear ({min_d:.3f} m) pesaría **{min_possible_weight_g:.1f} g**, "
            f"pero tu límite de peso es solo **{max_weight_g:.0f} g**.\n\n"
            f"💡 **Solución**: Reduce el diámetro mínimo a **{feasible_d:.3f} m** o menos, "
            f"O aumenta el peso máximo a **{int(min_possible_weight_g * 1.2)} g** o más."
        )

    # Peso máximo posible con el diámetro máximo
    max_area = pi * (max_d / 2) ** 2
    max_possible_weight_g = max_area * areal_density * 1000

    # Si el peso máximo permite menos del 30% del rango de diámetros
    feasible_max_d = 2 * np.sqrt(max_weight_g / 1000 / areal_density / pi)
    if feasible_max_d < max_d:
        usable_range_fraction = (feasible_max_d - min_d) / (max_d - min_d)

        if usable_range_fraction < 0.3:
            errors.append(
                f"**Peso incompatible con rango de diámetros**: Tu peso máximo ({max_weight_g:.0f} g) "
                f"solo permite antenas de hasta **{feasible_max_d:.3f} m**, pero tu rango "
                f"va hasta **{max_d:.2f} m**. Esto significa que **{(1-usable_range_fraction)*100:.0f}%** "
                f"de tu rango de diámetros es inaccesible.\n\n"
                f"💡 **Solución**: Reduce el diámetro máximo a **{feasible_max_d:.2f} m**, "
                f"O aumenta el peso máximo a **{int(max_possible_weight_g * 1.1)} g**."
            )
        elif usable_range_fraction < 0.7:
            warnings_list.append(
                f"⚠️ **Rango de diámetros parcialmente bloqueado**: El peso máximo "
                f"limita el uso de **{(1-usable_range_fraction)*100:.0f}%** del rango "
                f"de diámetros. El algoritmo solo puede explorar hasta {feasible_max_d:.3f} m "
                f"en lugar de {max_d:.2f} m."
            )

    # --- VALIDACIÓN 4: Rangos demasiado estrechos ---
    d_range = max_d - min_d
    fd_range = max_fd - min_fd

    if d_range < 0.1:
        warnings_list.append(
            f"⚠️ **Rango de diámetro muy estrecho**: Tu rango es solo {d_range:.3f} m. "
            f"Se recomienda al menos 0.5 m para permitir una optimización efectiva. "
            f"Considera ampliar a {min_d:.2f} - {min_d + 0.8:.2f} m."
        )

    if fd_range < 0.15:
        warnings_list.append(
            f"⚠️ **Rango f/D muy limitado**: Tu rango es solo {fd_range:.2f}. "
            f"Se recomienda al menos 0.30 para explorar diferentes geometrías de parábola. "
            f"Considera usar 0.35 - 0.70 (rango estándar)."
        )

    # --- VALIDACIÓN 5: Alcance vs tamaño de antena ---
    if range_km > 15:
        # Estimación aproximada de ganancia necesaria
        approx_gain_needed = 20 + 2 * range_km
        frequency_ghz = config.simulation.frequency_ghz
        d_needed_for_range = 10**((approx_gain_needed - 7) / 20) / frequency_ghz

        if d_needed_for_range > max_d * 1.5:
            max_gain_achievable = 20 * np.log10(max_d * frequency_ghz * 3.54) + 7
            achievable_range = (max_gain_achievable - 20) / 2

            warnings_list.append(
                f"⚠️ **Alcance muy ambicioso**: Para {range_km:.1f} km se necesita "
                f"una antena de ~{d_needed_for_range:.2f} m, pero tu máximo es {max_d:.2f} m. "
                f"El alcance real estimado será ~{achievable_range:.1f} km. "
                f"Considera reducir el alcance objetivo o aumentar el diámetro máximo."
            )

    # --- VALIDACIÓN 6: Valores fuera de rangos realistas ---
    realistic_limits = config.realistic_limits

    if max_d > realistic_limits.max_diameter_m:
        warnings_list.append(
            f"⚠️ **Diámetro inusualmente grande**: {max_d:.2f} m excede el límite "
            f"realista de {realistic_limits.max_diameter_m:.2f} m. "
            f"La optimización continuará, pero verifica que sea intencional."
        )

    if min_d < realistic_limits.min_diameter_m:
        warnings_list.append(
            f"⚠️ **Diámetro muy pequeño**: {min_d:.3f} m es menor que el mínimo "
            f"práctico de {realistic_limits.min_diameter_m:.3f} m. "
            f"Antenas tan pequeñas tendrán ganancia muy baja."
        )

    # Validar que hay espacio de búsqueda viable
    is_valid = len(errors) == 0

    return is_valid, errors, warnings_list


def main() -> None:
    """Main page rendering function."""
    st.title("🚀 Nueva Optimización")
    st.markdown(
        "Configure los parámetros de diseño y ejecute la optimización multi-objetivo NSGA-II"
    )

    # Load configuration
    config = load_configuration()

    # Sidebar - Parameter Controls
    st.sidebar.header("⚙️ Parámetros de Diseño")
    st.sidebar.markdown(
        "Ajuste los controles para definir el espacio de búsqueda de la optimización."
    )

    with st.sidebar.form(key="params_form"):
        st.subheader("Restricciones Geométricas")

        # Diameter range slider
        diameter_range = st.slider(
            "Rango de Diámetro (m)",
            min_value=float(config.realistic_limits.min_diameter_m),
            max_value=float(config.realistic_limits.max_diameter_m),
            value=(
                float(config.user_defaults.min_diameter_m),
                float(config.user_defaults.max_diameter_m),
            ),
            step=0.05,
            help="Diámetro mínimo y máximo de la antena parabólica en metros",
        )

        # Quick validation feedback for diameter
        d_range = diameter_range[1] - diameter_range[0]
        if d_range < 0.1:
            st.caption("⚠️ Rango muy estrecho. Recomendado: ≥ 0.5 m")
        elif d_range >= 0.5:
            st.caption("✅ Rango adecuado para optimización")

        # f/D ratio range slider
        fd_range = st.slider(
            "Rango de Relación f/D",
            min_value=float(config.realistic_limits.min_f_d_ratio),
            max_value=float(config.realistic_limits.max_f_d_ratio),
            value=(
                float(config.user_defaults.min_f_d_ratio),
                float(config.user_defaults.max_f_d_ratio),
            ),
            step=0.05,
            help="Relación focal/diámetro: determina la profundidad de la parábola",
        )

        # Quick validation feedback for f/D
        fd_range_width = fd_range[1] - fd_range[0]
        if fd_range_width < 0.15:
            st.caption("⚠️ Rango muy limitado. Recomendado: ≥ 0.30")
        elif fd_range_width >= 0.30:
            st.caption("✅ Rango adecuado para exploración")

        st.subheader("Restricciones de Operación")

        # Max payload slider
        max_payload = st.slider(
            "Peso Máximo Soportado (g)",
            min_value=float(config.realistic_limits.min_payload_g),
            max_value=float(config.realistic_limits.max_payload_g),
            value=float(config.user_defaults.max_payload_g),
            step=50.0,
            help="Peso máximo permitido para la antena terrestre (incluyendo reflector, alimentador y estructura de soporte)",
        )

        # Quick validation: check if weight is compatible with diameter
        import numpy as np
        pi = np.pi
        areal_density = config.simulation.areal_density_kg_per_m2
        min_possible_weight_g = pi * (diameter_range[0] / 2) ** 2 * areal_density * 1000

        if min_possible_weight_g > max_payload:
            st.caption(
                f"❌ Peso muy bajo: mínimo necesario ~{int(min_possible_weight_g)} g"
            )
        else:
            feasible_max_d = 2 * np.sqrt(max_payload / 1000 / areal_density / pi)
            if feasible_max_d < diameter_range[1]:
                st.caption(
                    f"⚠️ Peso limita diámetro a ~{feasible_max_d:.2f} m"
                )
            else:
                st.caption(f"✅ Peso compatible con rango de diámetros")

        # Desired range slider
        desired_range = st.slider(
            "Alcance Deseado (km)",
            min_value=float(config.realistic_limits.min_range_km),
            max_value=float(config.realistic_limits.max_range_km),
            value=float(config.user_defaults.desired_range_km),
            step=0.5,
            help="Distancia de comunicación deseada (informativo, no restringe la optimización)",
        )

        # Quick validation: check if range is realistic for antenna size
        if desired_range > 15:
            approx_gain_needed = 20 + 2 * desired_range
            frequency_ghz = config.simulation.frequency_ghz
            d_needed = 10**((approx_gain_needed - 7) / 20) / frequency_ghz
            if d_needed > diameter_range[1] * 1.3:
                st.caption(
                    f"⚠️ Alcance ambicioso: se recomienda D ≥ {d_needed:.2f} m"
                )

        # Submit button
        submit_button = st.form_submit_button(
            "🛰️ Ejecutar Optimización", use_container_width=True, type="primary"
        )

    # Main panel - Results area
    if not submit_button and "result" not in st.session_state:
        st.info(
            "👈 Configure los parámetros en la barra lateral y presione '🛰️ Ejecutar Optimización' "
            "para comenzar la simulación."
        )
        st.markdown("---")

        # Show default parameters info
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Valores por Defecto")
            st.json(
                {
                    "Diámetro Mín. (m)": config.user_defaults.min_diameter_m,
                    "Diámetro Máx. (m)": config.user_defaults.max_diameter_m,
                    "Peso Máximo (g)": config.user_defaults.max_payload_g,
                    "f/D Mín.": config.user_defaults.min_f_d_ratio,
                    "f/D Máx.": config.user_defaults.max_f_d_ratio,
                    "Alcance Deseado (km)": config.user_defaults.desired_range_km,
                }
            )

        with col2:
            st.markdown("### Parámetros de Optimización")
            st.json(
                {
                    "Tamaño de Población": config.optimization.population_size,
                    "Generaciones Máximas": config.optimization.max_generations,
                    "Frecuencia (GHz)": config.simulation.frequency_ghz,
                    "Eficiencia de Apertura": config.simulation.aperture_efficiency,
                }
            )

    # Execute optimization if form submitted
    if submit_button:
        # Prepare user parameters dictionary
        user_parameters: Dict[str, Any] = {
            "min_diameter_m": diameter_range[0],
            "max_diameter_m": diameter_range[1],
            "max_payload_g": max_payload,
            "min_f_d_ratio": fd_range[0],
            "max_f_d_ratio": fd_range[1],
            "desired_range_km": desired_range,
        }

        # Store parameters in session state
        st.session_state.user_parameters = user_parameters

        # --- VALIDACIÓN PREVIA: Verificar parámetros antes de ejecutar ---
        is_valid, validation_errors, validation_warnings = validate_user_inputs(
            user_parameters, config
        )

        # Mostrar advertencias (no bloquean la ejecución)
        if validation_warnings:
            st.warning("### ⚠️ Advertencias de Configuración")
            for warning in validation_warnings:
                st.markdown(f"- {warning}")
            st.markdown("---")
            st.info(
                "💡 **Nota**: Estas son advertencias, no errores. La optimización "
                "puede continuar, pero los resultados podrían no ser óptimos. "
                "Considera ajustar los parámetros según las sugerencias."
            )

        # Mostrar errores críticos (bloquean la ejecución)
        if not is_valid:
            st.error("### 🚫 Errores de Validación")
            st.markdown(
                "Se encontraron errores **críticos** en tu configuración que deben "
                "corregirse antes de ejecutar la optimización:"
            )

            for idx, error in enumerate(validation_errors, 1):
                st.markdown(f"{idx}. {error}")

            st.markdown("---")
            st.info(
                "🔧 **Cómo solucionar**: Ajusta los controles en la barra lateral "
                "según las soluciones sugeridas arriba, y luego presiona '🛰️ Ejecutar Optimización' nuevamente."
            )

            # Mostrar configuración actual para referencia
            with st.expander("📋 Ver Configuración Actual (para depuración)"):
                st.json(user_parameters)

            st.stop()  # Detener ejecución aquí

        # Execute optimization
        try:
            with st.spinner(
                "⚙️ Ejecutando optimización NSGA-II... Esto puede tardar unos segundos."
            ):
                facade = ApplicationFacade()
                result = facade.run_optimization(user_parameters)

            # Store results in session state
            st.session_state.result = result

        except FacadeValidationError as e:
            st.error("### ❌ Error de Validación del Sistema")
            st.markdown(
                f"El sistema detectó un problema con los parámetros:\n\n**{e}**"
            )
            st.info(
                "💡 Este error indica un problema interno en la configuración. "
                "Por favor, verifica los valores en la barra lateral."
            )
            st.stop()

        except RuntimeError as e:
            error_message = str(e)

            # Check if it's the "no viable solution" error
            if "no encontró ninguna solución viable" in error_message.lower():
                st.error(
                    "### 🚫 La Optimización No Encontró Soluciones Viables"
                )
                st.markdown(
                    """
                    El algoritmo NSGA-II ejecutó **todas las generaciones** pero no logró
                    encontrar **ninguna configuración de antena** que satisfaga tus restricciones.

                    **¿Qué significa esto?**

                    Tus restricciones de diseño son **demasiado restrictivas** o **incompatibles entre sí**.
                    El espacio de búsqueda está sobre-restringido y el algoritmo no tiene suficiente
                    libertad para encontrar soluciones óptimas.
                    """
                )

                # Diagnose the specific problem
                diagnosis = diagnose_infeasibility(user_parameters, config)

                # Show error with severity-based styling
                severity_icons = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "unknown": "⚠️",
                }

                icon = severity_icons.get(diagnosis["severity"], "⚠️")

                st.markdown(f"---")
                st.markdown(f"## {icon} Diagnóstico del Problema")

                # Explanation box
                if diagnosis["severity"] == "critical":
                    st.warning(
                        """
                        ### 🔍 **Problema Físicamente Imposible**

                        Una o más de tus restricciones son **matemáticamente imposibles de satisfacer**.
                        No es un problema del algoritmo, sino que la física no permite que exista
                        una antena con esas características.
                        """
                    )
                else:
                    st.warning(
                        """
                        ### 🔍 **¿Por qué no se encontró solución?**

                        Las restricciones de diseño que configuraste crean un espacio de búsqueda
                        demasiado limitado. El algoritmo NSGA-II necesita más flexibilidad para
                        encontrar soluciones óptimas en el frente de Pareto.
                        """
                    )

                # Show parameters in a cleaner format
                st.markdown("#### 📋 **Tu Configuración Actual:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Diámetro (m)",
                        f"{user_parameters['min_diameter_m']:.2f} - {user_parameters['max_diameter_m']:.2f}",
                        delta=f"Δ {user_parameters['max_diameter_m'] - user_parameters['min_diameter_m']:.2f}m",
                    )
                    st.metric("Peso Máximo", f"{user_parameters['max_payload_g']:.0f} g")
                with col2:
                    st.metric(
                        "Relación f/D",
                        f"{user_parameters['min_f_d_ratio']:.2f} - {user_parameters['max_f_d_ratio']:.2f}",
                        delta=f"Δ {user_parameters['max_f_d_ratio'] - user_parameters['min_f_d_ratio']:.2f}",
                    )
                    st.metric("Alcance Deseado", f"{user_parameters['desired_range_km']:.1f} km")
                with col3:
                    # Show constraint tightness
                    import numpy as np
                    pi = np.pi
                    areal_density = config.simulation.areal_density_kg_per_m2
                    max_possible_weight = (
                        pi
                        * (user_parameters["max_diameter_m"] / 2) ** 2
                        * areal_density
                        * 1000
                    )
                    weight_utilization = (
                        user_parameters["max_payload_g"] / max_possible_weight * 100
                    )

                    st.metric(
                        "Holgura de Peso",
                        f"{weight_utilization:.0f}%",
                        delta="del máximo posible" if weight_utilization < 100 else "Excede límite",
                        delta_color="normal" if weight_utilization < 100 else "inverse",
                    )

                st.markdown("---")

                # Show specific conflicts with better formatting
                st.markdown("### 🔍 **Diagnóstico Detallado**")
                for idx, conflict in enumerate(diagnosis["conflicts"], 1):
                    # Use different expander colors based on type
                    is_expanded = idx == 1  # Expand first conflict by default

                    with st.expander(f"{conflict['title']}", expanded=is_expanded):
                        st.markdown(conflict["description"])

                        if "calculation" in conflict:
                            st.markdown("**📐 Cálculos:**")
                            st.code(conflict["calculation"], language="text")

                st.markdown("---")

                # Show specific suggestions with better formatting
                if diagnosis["suggestions"]:
                    st.markdown("### ✅ **Cómo Solucionar Este Problema**")

                    st.info(
                        "A continuación se presentan soluciones específicas basadas en tu configuración actual. "
                        "**Ajusta los controles de la barra lateral** con los valores recomendados:"
                    )

                    for idx, suggestion in enumerate(diagnosis["suggestions"], 1):
                        st.markdown(f"{suggestion}")

                st.markdown("---")

                # General advice based on severity
                if diagnosis["severity"] == "critical":
                    st.error(
                        """
                        🚨 **Acción Requerida**: Debes ajustar tus restricciones antes de continuar.
                        El problema actual **no tiene solución matemática** con la configuración actual.
                        """
                    )
                else:
                    st.info(
                        """
                        💡 **Consejo General**: Si es tu primera vez usando SOGA, comienza con esta
                        configuración probada y luego ajusta gradualmente:

                        - **Diámetro**: 0.15 m - 1.5 m (rango amplio y realista)
                        - **Peso máximo**: 1500 g (balance entre portabilidad y rendimiento)
                        - **f/D**: 0.35 - 0.70 (rango estándar para parábolas)
                        - **Alcance**: 8 km (objetivo moderado)
                        """
                    )

            else:
                # Other runtime errors
                st.error(f"❌ **Error durante la Optimización**: {error_message}")

            st.stop()

        except Exception as e:
            st.error(f"❌ **Error Inesperado**: {type(e).__name__}: {e}")
            st.stop()

    # Display results if they exist
    if "result" in st.session_state:
        result = st.session_state.result

        st.success("✅ ¡Optimización completada con éxito!")

        # KPI Metrics Section
        st.markdown("### 📊 Métricas Clave de Rendimiento")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Ganancia Óptima",
                f"{result['expected_gain_dbi']:.2f} dBi",
                help="Ganancia de la antena en dirección del lóbulo principal",
            )

        with col2:
            st.metric(
                "Diámetro Óptimo",
                f"{result['optimal_diameter_mm']:.2f} mm",
                help="Diámetro de la apertura parabólica",
            )

        with col3:
            st.metric(
                "Relación f/D",
                f"{result['f_d_ratio']:.3f}",
                help="Relación focal/diámetro que determina la profundidad",
            )

        with col4:
            st.metric(
                "Ancho de Haz",
                f"{result['beamwidth_deg']:.2f}°",
                help="Ancho de haz a -3dB (HPBW - Half Power Beamwidth)",
            )

        st.markdown("---")

        # Tabs for detailed results
        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📉 Gráfico de Convergencia",
                "📊 Frente de Pareto",
                "📐 Geometría Detallada",
                "💾 Guardar y Exportar",
            ]
        )

        with tab1:
            st.markdown("#### Evolución del Algoritmo NSGA-II")
            st.markdown(
                "Este gráfico muestra cómo la mejor ganancia encontrada mejora a través de las generaciones "
                "del algoritmo evolutivo."
            )

            # Create and display convergence plot
            convergence_fig = create_convergence_plot(result["convergence"])
            st.plotly_chart(convergence_fig, use_container_width=True)

            # Statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Ganancia Inicial", f"{result['convergence'][0]:.2f} dBi")
            with col2:
                st.metric("Ganancia Final", f"{result['convergence'][-1]:.2f} dBi")
            with col3:
                improvement = result["convergence"][-1] - result["convergence"][0]
                st.metric("Mejora Total", f"{improvement:.2f} dB")

        with tab2:
            st.markdown("#### Frente de Pareto: Trade-offs entre Ganancia y Peso")
            st.markdown(
                """
                El **frente de Pareto** muestra todas las soluciones óptimas encontradas por NSGA-II.
                Cada punto representa una configuración de antena donde no es posible mejorar un objetivo
                (ganancia o peso) sin empeorar el otro.

                - **Puntos azules**: Todas las soluciones del frente de Pareto
                - **Estrella roja**: Knee point (solución con mejor balance seleccionada automáticamente)
                """
            )

            # Check if pareto_front data is available
            if "pareto_front" in result and result["pareto_front"]:
                # Create and display Pareto front plot
                pareto_fig = create_pareto_front_plot(
                    result["pareto_front"],
                    result
                )
                st.plotly_chart(pareto_fig, use_container_width=True)

                # Statistics about the Pareto front
                st.markdown("---")
                st.markdown("##### 📈 Estadísticas del Frente de Pareto")

                col1, col2, col3, col4 = st.columns(4)

                pareto_gains = [p.gain for p in result["pareto_front"]]
                pareto_weights = [p.weight * 1000 for p in result["pareto_front"]]  # Convert to grams

                with col1:
                    st.metric(
                        "Soluciones Encontradas",
                        f"{len(result['pareto_front'])}",
                        help="Número total de soluciones óptimas en el frente de Pareto"
                    )

                with col2:
                    st.metric(
                        "Rango de Ganancia",
                        f"{min(pareto_gains):.1f} - {max(pareto_gains):.1f} dBi",
                        help="Rango de ganancias disponibles en las soluciones óptimas"
                    )

                with col3:
                    st.metric(
                        "Rango de Peso",
                        f"{min(pareto_weights):.0f} - {max(pareto_weights):.0f} g",
                        help="Rango de pesos disponibles en las soluciones óptimas"
                    )

                with col4:
                    # Calculate trade-off ratio
                    gain_range = max(pareto_gains) - min(pareto_gains)
                    weight_range = max(pareto_weights) - min(pareto_weights)
                    if weight_range > 0:
                        tradeoff = gain_range / weight_range
                        st.metric(
                            "Trade-off",
                            f"{tradeoff:.3f} dBi/g",
                            help="Ganancia adicional por gramo de peso añadido"
                        )

                st.markdown("---")
                st.info(
                    """
                    **💡 Interpretación del Frente de Pareto:**

                    - **Zona izquierda** (bajo peso): Antenas más ligeras con menor ganancia
                    - **Zona derecha** (alto peso): Antenas más pesadas con mayor ganancia
                    - **Knee point** (estrella roja): Mejor compromiso entre ganancia y peso

                    El algoritmo NSGA-II ha encontrado todas estas configuraciones óptimas.
                    Dependiendo de tus prioridades específicas, podrías elegir cualquier punto del frente.
                    """
                )
            else:
                st.warning("No hay datos del frente de Pareto disponibles para esta optimización.")

        with tab3:
            st.markdown("#### Especificaciones Geométricas Completas")

            # Parabola geometry visualization
            st.markdown("##### 📐 Visualización de la Geometría")
            st.markdown(
                "Este diagrama muestra el perfil de corte de la antena parabólica con sus dimensiones clave:"
            )

            parabola_fig = create_parabola_geometry_plot(
                result["optimal_diameter_mm"],
                result["optimal_focal_length_mm"],
                result["optimal_depth_mm"],
            )
            st.plotly_chart(parabola_fig, use_container_width=True)

            st.markdown("---")

            # Geometry table
            st.markdown("##### 📏 Tabla de Dimensiones")
            geometry_data = {
                "Parámetro": [
                    "Diámetro de Apertura",
                    "Distancia Focal",
                    "Profundidad de la Parábola",
                    "Relación f/D",
                ],
                "Valor": [
                    f"{result['optimal_diameter_mm']:.2f} mm",
                    f"{result['optimal_focal_length_mm']:.2f} mm",
                    f"{result['optimal_depth_mm']:.2f} mm",
                    f"{result['f_d_ratio']:.3f}",
                ],
                "Descripción": [
                    "Diámetro de la superficie reflectora",
                    "Distancia del vértice al punto focal",
                    "Profundidad máxima de la superficie cóncava",
                    "Relación adimensional que define la curvatura",
                ],
            }

            st.table(geometry_data)

            # Performance metrics table
            st.markdown("#### Métricas de Rendimiento RF")

            performance_data = {
                "Métrica": [
                    "Ganancia Directiva",
                    "Ancho de Haz (HPBW)",
                    "Frecuencia de Operación",
                    "Eficiencia de Apertura",
                ],
                "Valor": [
                    f"{result['expected_gain_dbi']:.2f} dBi",
                    f"{result['beamwidth_deg']:.2f}°",
                    f"{config.simulation.frequency_ghz:.1f} GHz",
                    f"{config.simulation.aperture_efficiency * 100:.0f}%",
                ],
            }

            st.table(performance_data)

            # JSON export option
            with st.expander("🔍 Ver Datos Completos (JSON)"):
                st.json(result)

        with tab4:
            st.markdown("#### Opciones de Guardado y Exportación")

            # Session save section
            st.markdown("##### 💾 Guardar Sesión Completa")
            st.markdown(
                "Guarde los parámetros de entrada y resultados en formato JSON para análisis posterior."
            )

            # Prepare session data for JSON serialization
            # Convert ParetoPoint objects to dictionaries
            result_copy = dict(st.session_state.result)
            if "pareto_front" in result_copy and result_copy["pareto_front"]:
                result_copy["pareto_front"] = [
                    {
                        "diameter": p.diameter,
                        "f_d_ratio": p.f_d_ratio,
                        "gain": p.gain,
                        "weight": p.weight,
                    }
                    for p in result_copy["pareto_front"]
                ]

            session_data = {
                "params": st.session_state.user_parameters,
                "results": result_copy,
            }

            session_json = json.dumps(session_data, indent=2, ensure_ascii=False)

            st.download_button(
                label="📥 Descargar Sesión (.json)",
                data=session_json,
                file_name="soga_session.json",
                mime="application/json",
                use_container_width=True,
            )

            st.markdown("---")

            # Convergence export section
            st.markdown("##### 📊 Exportar Historial de Convergencia")
            st.markdown(
                "Exporte el historial de convergencia en formato CSV para análisis en Excel, Python, etc."
            )

            try:
                convergence_csv = export_convergence_to_bytes(result["convergence"])

                st.download_button(
                    label="📥 Descargar Convergencia (.csv)",
                    data=convergence_csv,
                    file_name="soga_convergence.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            except Exception as e:
                st.error(f"Error al exportar convergencia: {e}")

            st.markdown("---")

            # Instructions
            st.info(
                """
                **Cómo usar los archivos guardados:**

                - **Archivo JSON**: Puede cargarse en la página "📚 Análisis de Sesiones" para
                  comparar múltiples ejecuciones.

                - **Archivo CSV**: Puede abrirse en Excel, Google Sheets, o procesarse con
                  pandas/matplotlib para análisis personalizado.
                """
            )


if __name__ == "__main__":
    main()
