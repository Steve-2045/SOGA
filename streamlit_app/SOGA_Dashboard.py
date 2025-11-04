"""
SOGA Dashboard - Main Entry Point
==================================

Professional interactive dashboard for the Software de Optimización Geométrica de Antenas (SOGA).
This is the home page of the multi-page Streamlit application.

Author: SOGA Development Team
License: MIT
"""

import sys
from pathlib import Path

import streamlit as st

# Ensure the backend is importable
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="SOGA Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/Steve-2045/SOGA",
        "Report a bug": "https://github.com/Steve-2045/SOGA/issues",
        "About": "SOGA: Optimización de Antenas para Drones en Agricultura de Precisión",
    },
)


def main() -> None:
    """Main home page rendering function."""
    # Title and header
    st.title("📡 SOGA: Software de Optimización Geométrica de Antenas")
    st.markdown(
        "### Antenas Parabólicas para Comunicación con Drones en Agricultura de Precisión"
    )

    st.markdown("---")

    # Introduction section
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            """
            ## Bienvenido

            Herramienta avanzada de optimización multi-objetivo para diseño de antenas parabólicas
            direccionales de 2.4 GHz para comunicación terrestre con drones en agricultura de precisión.

            ### Características Principales

            - **Optimización Multi-Objetivo NSGA-II**: Algoritmo genético de última generación para
              balancear ganancia, peso y geometría.

            - **Fundamentos Científicos**: Basado en las ecuaciones de Balanis y Kraus para diseño
              de antenas parabólicas de alta precisión.

            - **Validación Física**: Todas las configuraciones se validan contra límites realistas
              de fabricación y operación práctica.

            - **Análisis de Convergencia**: Visualización completa del proceso de optimización
              generación por generación.

            ### Navegación

            Utilice la **barra lateral** para acceder a las diferentes páginas:

            - 🚀 **Nueva Optimización**: Configure y ejecute simulaciones de optimización
            - 📚 **Análisis de Sesiones**: Compare y analice múltiples resultados guardados
            - ℹ️ **Acerca del Proyecto**: Documentación técnica y fundamentos científicos

            ---

            ### Inicio Rápido

            1. Vaya a **🚀 Nueva Optimización**
            2. Configure los parámetros de diseño
            3. Ejecute la optimización
            4. Analice los resultados y métricas de rendimiento
            5. Descargue o exporte los datos
            """
        )

    with col2:
        # Quick stats
        st.markdown("### Especificaciones Técnicas")
        st.metric("Frecuencia de Operación", "2.4 GHz", help="Banda ISM estándar")
        st.metric("Rango de Diámetros", "5 cm - 3 m", help="Límites de fabricación")
        st.metric(
            "Algoritmo", "NSGA-II", help="Non-dominated Sorting Genetic Algorithm II"
        )

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #667eea;'>
            <p>SOGA v1.0 | Desarrollado con Streamlit y optimización evolutiva NSGA-II</p>
            <p>Para más información, consulta la documentación completa en la carpeta <code>docs/</code></p>
            <p>GitHub: <a href="https://github.com/Steve-2045/SOGA" target="_blank">https://github.com/Steve-2045/SOGA</a></p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
