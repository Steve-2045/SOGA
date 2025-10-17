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


def diagnose_infeasibility(user_parameters: dict, config) -> dict:
    """
    Diagnose why the optimization is infeasible and provide specific feedback.

    Args:
        user_parameters: Dictionary with user-provided parameters
        config: Application configuration object

    Returns:
        Dictionary with diagnosis information
    """
    diagnosis = {
        "main_issue": None,
        "conflicts": [],
        "suggestions": [],
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

    # Calculate minimum possible weight with minimum diameter
    min_area = 3.14159 * (min_d / 2) ** 2
    min_weight_kg = min_area * areal_density
    min_weight_g = min_weight_kg * 1000

    # Calculate maximum possible weight with maximum diameter
    max_area = 3.14159 * (max_d / 2) ** 2
    max_weight_kg = max_area * areal_density
    max_weight_g_calc = max_weight_kg * 1000

    # Diagnosis 1: Weight constraint too restrictive
    if min_weight_g > max_weight_g:
        diagnosis["main_issue"] = "weight_too_low"
        diagnosis["conflicts"].append({
            "title": "Peso Máximo Insuficiente",
            "description": f"Incluso la antena más pequeña ({min_d:.2f}m) pesa ~{min_weight_g:.0f}g, "
                          f"pero tu límite es {max_weight_g:.0f}g.",
            "calculation": f"Peso mínimo = π×({min_d:.2f}/2)² × {areal_density} kg/m² = {min_weight_g:.0f}g",
        })
        diagnosis["suggestions"].append(
            f"Aumentar peso máximo a **{int(min_weight_g * 1.3):.0f}g** o más"
        )

    # Diagnosis 2: Diameter range too large for weight constraint
    elif max_weight_g < max_weight_g_calc * 0.5:
        diagnosis["main_issue"] = "diameter_range_too_large"
        # Calculate feasible max diameter for the weight constraint
        feasible_max_d = 2 * ((max_weight_g / 1000 / areal_density / 3.14159) ** 0.5)
        diagnosis["conflicts"].append({
            "title": "Rango de Diámetro Demasiado Amplio para el Peso Permitido",
            "description": f"Con {max_weight_g:.0f}g, el diámetro máximo factible es ~{feasible_max_d:.2f}m, "
                          f"pero tu rango llega hasta {max_d:.2f}m.",
            "calculation": f"D_max_factible = 2×√({max_weight_g/1000:.3f}kg ÷ {areal_density} ÷ π) = {feasible_max_d:.2f}m",
        })
        diagnosis["suggestions"].append(
            f"Reducir diámetro máximo a **{feasible_max_d:.2f}m** o menos"
        )
        diagnosis["suggestions"].append(
            f"O aumentar peso máximo a **{int(max_weight_g_calc):.0f}g**"
        )

    # Diagnosis 3: f/D range too narrow
    fd_range = max_fd - min_fd
    if fd_range < 0.2:
        diagnosis["main_issue"] = "fd_range_too_narrow"
        diagnosis["conflicts"].append({
            "title": "Rango f/D Muy Estrecho",
            "description": f"El rango f/D ({min_fd:.2f} - {max_fd:.2f}) es muy restrictivo. "
                          f"Esto limita severamente las opciones geométricas.",
            "calculation": f"Rango actual: {fd_range:.2f} (se recomienda ≥ 0.3)",
        })
        diagnosis["suggestions"].append(
            f"Ampliar rango f/D a **{max(0.25, min_fd - 0.1):.2f} - {min(1.2, max_fd + 0.1):.2f}**"
        )

    # Diagnosis 4: Diameter range too narrow
    d_range = max_d - min_d
    if d_range < 0.3:
        diagnosis["main_issue"] = "diameter_range_too_narrow"
        diagnosis["conflicts"].append({
            "title": "Rango de Diámetro Muy Estrecho",
            "description": f"El rango de diámetro ({min_d:.2f}m - {max_d:.2f}m) es muy pequeño. "
                          f"El algoritmo necesita más flexibilidad.",
            "calculation": f"Rango actual: {d_range:.2f}m (se recomienda ≥ 0.5m)",
        })
        diagnosis["suggestions"].append(
            f"Ampliar rango de diámetro a **{max(0.05, min_d * 0.5):.2f}m - {min(3.0, max_d * 1.5):.2f}m**"
        )

    # Diagnosis 5: Extreme range requirement
    if range_km > 20 and max_d < 1.5:
        diagnosis["main_issue"] = "range_vs_size"
        diagnosis["conflicts"].append({
            "title": "Alcance Muy Alto para Tamaño de Antena Limitado",
            "description": f"Para {range_km:.1f} km se necesita alta ganancia, lo que requiere antenas grandes (>1.5m), "
                          f"pero tu diámetro máximo es {max_d:.2f}m.",
            "calculation": f"Alcance alto → Ganancia alta → Diámetro grande (tu max: {max_d:.2f}m)",
        })
        diagnosis["suggestions"].append(
            f"Reducir alcance deseado a **{range_km * 0.4:.1f} km** para antenas de ~{max_d:.2f}m"
        )
        diagnosis["suggestions"].append(
            f"O aumentar diámetro máximo a **2.0m** o más"
        )

    # Diagnosis 6: Multiple moderate conflicts (general incompatibility)
    if diagnosis["main_issue"] is None and len(diagnosis["conflicts"]) == 0:
        diagnosis["main_issue"] = "general_incompatibility"
        diagnosis["conflicts"].append({
            "title": "Combinación General de Restricciones Incompatible",
            "description": "Las restricciones son individualmente válidas, pero su combinación no permite "
                          "ninguna solución viable. El espacio de búsqueda está sobre-restringido.",
            "calculation": f"Parámetros: D={min_d:.2f}-{max_d:.2f}m, Peso≤{max_weight_g:.0f}g, "
                          f"f/D={min_fd:.2f}-{max_fd:.2f}, Alcance={range_km:.1f}km",
        })
        diagnosis["suggestions"].append(
            "Relajar **múltiples restricciones simultáneamente**"
        )
        diagnosis["suggestions"].append(
            f"Ejemplo: Peso→**{int(max_weight_g * 2):.0f}g**, f/D→**0.3-0.8**, D→**{min_d * 0.7:.2f}-{max_d * 1.3:.2f}m**"
        )

    return diagnosis


def create_parabola_geometry_plot(diameter_mm: float, focal_length_mm: float, depth_mm: float) -> go.Figure:
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


def main() -> None:
    """Main page rendering function."""
    st.title("🚀 Nueva Optimización")
    st.markdown("Configure los parámetros de diseño y ejecute la optimización multi-objetivo NSGA-II")

    # Load configuration
    config = load_configuration()

    # Sidebar - Parameter Controls
    st.sidebar.header("⚙️ Parámetros de Diseño")
    st.sidebar.markdown("Ajuste los controles para definir el espacio de búsqueda de la optimización.")

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

        st.subheader("Restricciones de Operación")

        # Max payload slider
        max_payload = st.slider(
            "Peso Máximo Soportado (g)",
            min_value=float(config.realistic_limits.min_payload_g),
            max_value=float(config.realistic_limits.max_payload_g),
            value=float(config.user_defaults.max_payload_g),
            step=50.0,
            help="Peso máximo que el UAV puede transportar (incluyendo antena y estructura)",
        )

        # Desired range slider
        desired_range = st.slider(
            "Alcance Deseado (km)",
            min_value=float(config.realistic_limits.min_range_km),
            max_value=float(config.realistic_limits.max_range_km),
            value=float(config.user_defaults.desired_range_km),
            step=0.5,
            help="Distancia de comunicación deseada (informativo, no restringe la optimización)",
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

        # Execute optimization
        try:
            with st.spinner("⚙️ Ejecutando optimización NSGA-II... Esto puede tardar unos segundos."):
                facade = ApplicationFacade()
                result = facade.run_optimization(user_parameters)

            # Store results in session state
            st.session_state.result = result

        except FacadeValidationError as e:
            st.error(f"❌ **Error de Validación**: {e}")
            st.stop()

        except RuntimeError as e:
            error_message = str(e)

            # Check if it's the "no viable solution" error
            if "no encontró ninguna solución viable" in error_message.lower():
                st.error("❌ **Error de Optimización**: La optimización no encontró ninguna solución viable.")

                st.warning(
                    """
                    ### 🔍 **¿Por qué sucede esto?**

                    Las restricciones de diseño que configuraste son **físicamente incompatibles**.
                    El algoritmo NSGA-II intentó encontrar una antena que cumpla TODAS las restricciones
                    simultáneamente, pero no existe ninguna geometría que lo logre.
                    """
                )

                # Diagnose the specific problem
                diagnosis = diagnose_infeasibility(user_parameters, config)

                # Show parameters
                st.markdown("#### 📋 **Parámetros Configurados:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Diámetro", f"{user_parameters['min_diameter_m']:.2f}m - {user_parameters['max_diameter_m']:.2f}m")
                    st.metric("Peso Máximo", f"{user_parameters['max_payload_g']:.0f}g")
                with col2:
                    st.metric("f/D Ratio", f"{user_parameters['min_f_d_ratio']:.2f} - {user_parameters['max_f_d_ratio']:.2f}")
                    st.metric("Alcance Deseado", f"{user_parameters['desired_range_km']:.1f} km")

                st.markdown("---")

                # Show specific conflicts found
                with st.expander("🔴 **Diagnóstico del Problema**", expanded=True):
                    for conflict in diagnosis["conflicts"]:
                        st.markdown(f"### {conflict['title']}")
                        st.markdown(conflict['description'])
                        if 'calculation' in conflict:
                            st.code(conflict['calculation'], language="text")
                        st.markdown("---")

                # Show specific suggestions
                if diagnosis["suggestions"]:
                    st.markdown("### ✅ **Soluciones Específicas para tu Caso:**")
                    for idx, suggestion in enumerate(diagnosis["suggestions"], 1):
                        st.markdown(f"{idx}. {suggestion}")

                # General advice
                st.info(
                    """
                    💡 **Consejo**: Empieza con restricciones más flexibles y luego ajústalas
                    gradualmente hasta encontrar el balance óptimo para tu aplicación.

                    **Configuración recomendada para comenzar:**
                    - Diámetro: 0.1m - 2.0m (amplio)
                    - Peso máximo: 2000g (realista)
                    - f/D: 0.3 - 0.8 (flexible)
                    - Alcance: 5 km (moderado)
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
        tab1, tab2, tab3 = st.tabs(["📉 Gráfico de Convergencia", "📐 Geometría Detallada", "💾 Guardar y Exportar"])

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

        with tab3:
            st.markdown("#### Opciones de Guardado y Exportación")

            # Session save section
            st.markdown("##### 💾 Guardar Sesión Completa")
            st.markdown("Guarde los parámetros de entrada y resultados en formato JSON para análisis posterior.")

            session_data = {
                "params": st.session_state.user_parameters,
                "results": st.session_state.result,
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
            st.markdown("Exporte el historial de convergencia en formato CSV para análisis en Excel, Python, etc.")

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
