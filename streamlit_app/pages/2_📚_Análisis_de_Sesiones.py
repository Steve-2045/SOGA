"""
Análisis de Sesiones - SOGA Dashboard
======================================

Interactive page for loading, comparing, and analyzing multiple optimization sessions.
Provides comparative visualization and CSV export functionality.

Author: SOGA Development Team
License: MIT
"""

import io
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Ensure the backend is importable
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from soga.infrastructure.file_io import ResultsExporter

# Page configuration
st.set_page_config(
    page_title="Análisis de Sesiones - SOGA",
    page_icon="📚",
    layout="wide",
)


def initialize_session_state() -> None:
    """Initialize session state for loaded sessions."""
    if "loaded_sessions" not in st.session_state:
        st.session_state.loaded_sessions = []


def load_session_file(uploaded_file) -> Dict[str, Any]:
    """
    Load and parse a session JSON file.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        Dictionary with session data

    Raises:
        json.JSONDecodeError: If file is not valid JSON
        ValueError: If file doesn't have required structure
    """
    try:
        data = json.load(uploaded_file)

        # Validate structure
        if "params" not in data or "results" not in data:
            raise ValueError(
                "El archivo JSON no tiene la estructura correcta. "
                "Debe contener 'params' y 'results'."
            )

        return data

    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Error al parsear JSON: {e.msg}", e.doc, e.pos
        )


def create_comparison_dataframe(sessions: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Create a pandas DataFrame for session comparison.

    Args:
        sessions: List of session dictionaries

    Returns:
        DataFrame with comparison metrics
    """
    rows = []

    for session in sessions:
        params = session["data"]["params"]
        results = session["data"]["results"]

        row = {
            "Sesión": session["filename"],
            "Ganancia (dBi)": results["expected_gain_dbi"],
            "Diámetro (mm)": results["optimal_diameter_mm"],
            "Relación f/D": results["f_d_ratio"],
            "Ancho de Haz (°)": results["beamwidth_deg"],
            "Peso Máx. (g)": params["max_payload_g"],
            "Alcance (km)": params["desired_range_km"],
        }

        rows.append(row)

    return pd.DataFrame(rows)


def create_comparative_convergence_plot(sessions: List[Dict[str, Any]]) -> go.Figure:
    """
    Create an interactive Plotly chart comparing convergence histories.

    Args:
        sessions: List of session dictionaries

    Returns:
        Plotly Figure object with overlaid convergence curves
    """
    fig = go.Figure()

    # Color palette for multiple lines
    colors = [
        "#667eea",  # Primary purple
        "#48bb78",  # Green
        "#f56565",  # Red
        "#ed8936",  # Orange
        "#4299e1",  # Blue
        "#9f7aea",  # Purple
        "#ed64a6",  # Pink
        "#38b2ac",  # Teal
    ]

    for idx, session in enumerate(sessions):
        convergence = session["data"]["results"]["convergence"]
        generations = list(range(len(convergence)))
        color = colors[idx % len(colors)]

        fig.add_trace(
            go.Scatter(
                x=generations,
                y=convergence,
                mode="lines+markers",
                name=session["filename"],
                line={"color": color, "width": 2},
                marker={"size": 4, "color": color},
                hovertemplate=f"<b>{session['filename']}</b><br>"
                              "Generación: %{x}<br>"
                              "Ganancia: %{y:.2f} dBi<extra></extra>",
            )
        )

    fig.update_layout(
        title={
            "text": "Comparación de Convergencia entre Sesiones",
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
        legend={
            "bgcolor": "#1a1f2e",
            "bordercolor": "#667eea",
            "borderwidth": 1,
        },
    )

    return fig


def export_comparison_to_bytes(df: pd.DataFrame) -> bytes:
    """
    Export comparison DataFrame to CSV format in memory.

    Args:
        df: Pandas DataFrame with comparison data

    Returns:
        CSV data as bytes
    """
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding="utf-8")
    return buffer.getvalue().encode("utf-8")


def main() -> None:
    """Main page rendering function."""
    st.title("📚 Análisis de Sesiones")
    st.markdown("Compare y analice múltiples ejecuciones de optimización guardadas")

    # Initialize session state
    initialize_session_state()

    # Sidebar - File Upload
    st.sidebar.header("📂 Cargar Sesiones")
    st.sidebar.markdown("Suba uno o más archivos `.json` generados en la página de optimización.")

    uploaded_files = st.sidebar.file_uploader(
        "Seleccionar archivos de sesión",
        type=["json"],
        accept_multiple_files=True,
        key="session_uploader",
        help="Puede seleccionar múltiples archivos manteniendo Ctrl (Windows/Linux) o Cmd (Mac)",
    )

    # Process uploaded files
    if uploaded_files:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Archivos Cargados")

        for uploaded_file in uploaded_files:
            # Check if already loaded
            existing_filenames = [s["filename"] for s in st.session_state.loaded_sessions]

            if uploaded_file.name not in existing_filenames:
                try:
                    # Reset file pointer
                    uploaded_file.seek(0)

                    # Load and validate
                    session_data = load_session_file(uploaded_file)

                    # Add to session state
                    st.session_state.loaded_sessions.append(
                        {
                            "filename": uploaded_file.name,
                            "data": session_data,
                        }
                    )

                    st.sidebar.success(f"✅ {uploaded_file.name}")

                except json.JSONDecodeError as e:
                    st.sidebar.error(f"❌ {uploaded_file.name}: JSON inválido - {e.msg}")

                except ValueError as e:
                    st.sidebar.error(f"❌ {uploaded_file.name}: {e}")

                except Exception as e:
                    st.sidebar.error(f"❌ {uploaded_file.name}: Error inesperado - {e}")

        # Clear button
        if st.sidebar.button("🗑️ Limpiar Todas las Sesiones", use_container_width=True):
            st.session_state.loaded_sessions = []
            st.rerun()

    # Main panel
    if not st.session_state.loaded_sessions:
        st.info(
            "👈 Cargue archivos de sesión (.json) en la barra lateral para comenzar el análisis comparativo."
        )
        st.markdown("---")

        # Instructions
        st.markdown("### 📋 Instrucciones")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
                #### Cómo usar esta página:

                1. **Cargar Sesiones**: Use el cargador de archivos en la barra lateral para
                   seleccionar uno o más archivos `.json` de sesiones guardadas.

                2. **Seleccionar**: Una vez cargados, use el selector múltiple para elegir
                   qué sesiones desea comparar.

                3. **Analizar**: Explore las pestañas de comparativa de métricas y convergencia
                   para identificar las mejores configuraciones.

                4. **Exportar**: Descargue los datos comparativos en formato CSV para análisis
                   adicional en otras herramientas.
                """
            )

        with col2:
            st.markdown(
                """
                #### Casos de uso:

                - **Análisis de sensibilidad**: Compare cómo diferentes rangos de parámetros
                  afectan el resultado final.

                - **Validación**: Verifique la repetibilidad ejecutando la misma configuración
                  múltiples veces.

                - **Optimización de parámetros**: Identifique qué combinaciones de restricciones
                  producen el mejor desempeño.

                - **Documentación**: Exporte comparativas para reportes técnicos o presentaciones.
                """
            )

        return

    # Session selector
    st.markdown("### 🎯 Selección de Sesiones")

    session_names = [s["filename"] for s in st.session_state.loaded_sessions]

    selected_sessions = st.multiselect(
        "Seleccionar sesiones para comparar:",
        options=session_names,
        default=session_names,
        help="Puede seleccionar o deseleccionar sesiones para el análisis comparativo",
    )

    if not selected_sessions:
        st.warning("⚠️ Seleccione al menos una sesión para visualizar los datos.")
        return

    # Filter sessions based on selection
    filtered_sessions = [
        s for s in st.session_state.loaded_sessions if s["filename"] in selected_sessions
    ]

    st.markdown(f"**{len(filtered_sessions)} sesión(es) seleccionada(s)**")
    st.markdown("---")

    # Tabs for analysis
    tab1, tab2 = st.tabs(["📊 Comparativa de Métricas", "📉 Comparativa de Convergencia"])

    with tab1:
        st.markdown("#### Tabla Comparativa de Resultados")

        # Create DataFrame
        comparison_df = create_comparison_dataframe(filtered_sessions)

        # Display with highlighting
        st.dataframe(
            comparison_df.style.highlight_max(
                subset=["Ganancia (dBi)"],
                color="#48bb7844",
            ).highlight_min(
                subset=["Ancho de Haz (°)"],
                color="#4299e144",
            ),
            use_container_width=True,
            height=min(400, len(comparison_df) * 35 + 38),  # Dynamic height
        )

        # Statistics
        st.markdown("#### 📈 Estadísticas Agregadas")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Ganancia Promedio",
                f"{comparison_df['Ganancia (dBi)'].mean():.2f} dBi",
            )
            st.metric(
                "Ganancia Máxima",
                f"{comparison_df['Ganancia (dBi)'].max():.2f} dBi",
            )

        with col2:
            st.metric(
                "Diámetro Promedio",
                f"{comparison_df['Diámetro (mm)'].mean():.2f} mm",
            )
            st.metric(
                "Desviación Estándar",
                f"{comparison_df['Diámetro (mm)'].std():.2f} mm",
            )

        with col3:
            st.metric(
                "f/D Promedio",
                f"{comparison_df['Relación f/D'].mean():.3f}",
            )
            st.metric(
                "Rango f/D",
                f"{comparison_df['Relación f/D'].min():.3f} - {comparison_df['Relación f/D'].max():.3f}",
            )

        with col4:
            st.metric(
                "Ancho Haz Promedio",
                f"{comparison_df['Ancho de Haz (°)'].mean():.2f}°",
            )
            st.metric(
                "Ancho Haz Mínimo",
                f"{comparison_df['Ancho de Haz (°)'].min():.2f}°",
            )

        # Export section
        st.markdown("---")
        st.markdown("#### 💾 Exportar Datos Comparativos")

        try:
            # Prepare data for export (convert to format expected by ResultsExporter)
            export_data = []
            for session in filtered_sessions:
                results = session["data"]["results"]
                export_data.append(
                    {
                        "diameter_mm": results["optimal_diameter_mm"],
                        "focal_length_mm": results["optimal_focal_length_mm"],
                        "depth_mm": results["optimal_depth_mm"],
                        "f_d_ratio": results["f_d_ratio"],
                        "gain_dbi": results["expected_gain_dbi"],
                        "beamwidth_deg": results["beamwidth_deg"],
                    }
                )

            # Export to bytes
            csv_bytes = export_comparison_to_bytes(comparison_df)

            st.download_button(
                label="📥 Descargar Comparativa (.csv)",
                data=csv_bytes,
                file_name="soga_session_comparison.csv",
                mime="text/csv",
                use_container_width=True,
            )

        except Exception as e:
            st.error(f"Error al exportar: {e}")

    with tab2:
        st.markdown("#### Evolución Comparativa de la Optimización")

        st.markdown(
            "Este gráfico superpone las curvas de convergencia de todas las sesiones seleccionadas, "
            "permitiendo comparar la velocidad y calidad de la optimización."
        )

        # Create and display comparative plot
        convergence_fig = create_comparative_convergence_plot(filtered_sessions)
        st.plotly_chart(convergence_fig, use_container_width=True)

        # Convergence statistics
        st.markdown("#### 📊 Análisis de Convergencia")

        convergence_stats = []

        for session in filtered_sessions:
            convergence = session["data"]["results"]["convergence"]

            stats = {
                "Sesión": session["filename"],
                "Ganancia Inicial (dBi)": f"{convergence[0]:.2f}",
                "Ganancia Final (dBi)": f"{convergence[-1]:.2f}",
                "Mejora Total (dB)": f"{convergence[-1] - convergence[0]:.2f}",
                "Generaciones": len(convergence),
            }

            convergence_stats.append(stats)

        convergence_df = pd.DataFrame(convergence_stats)
        st.dataframe(convergence_df, use_container_width=True)

        # Best session identification
        st.markdown("---")

        best_session = filtered_sessions[0]
        best_gain = best_session["data"]["results"]["expected_gain_dbi"]

        for session in filtered_sessions[1:]:
            current_gain = session["data"]["results"]["expected_gain_dbi"]
            if current_gain > best_gain:
                best_gain = current_gain
                best_session = session

        st.success(
            f"🏆 **Mejor Sesión**: `{best_session['filename']}` "
            f"con ganancia de **{best_gain:.2f} dBi**"
        )


if __name__ == "__main__":
    main()
