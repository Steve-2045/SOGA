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
        "Get Help": "https://github.com/tu-repo/soga",
        "Report a bug": "https://github.com/tu-repo/soga/issues",
        "About": "SOGA: Software de Optimización Geométrica de Antenas para UAVs",
    },
)


def main() -> None:
    """Main home page rendering function."""
    # Title and header
    st.title("📡 SOGA: Software de Optimización Geométrica de Antenas")
    st.markdown("### Dashboard Interactivo para Optimización de Antenas Parabólicas en UAVs")

    st.markdown("---")

    # Introduction section
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            """
            ## Bienvenido al Dashboard de SOGA

            **SOGA** es una herramienta avanzada de optimización multi-objetivo que diseña antenas
            parabólicas de alto rendimiento para aplicaciones de Vehículos Aéreos No Tripulados (UAVs).

            ### Características Principales

            - **Optimización Multi-Objetivo NSGA-II**: Algoritmo genético de última generación para
              balancear ganancia, peso y geometría.

            - **Fundamentos Científicos**: Basado en las ecuaciones de Balanis y Kraus para diseño
              de antenas parabólicas de alta precisión.

            - **Validación Física**: Todas las configuraciones se validan contra límites realistas
              de fabricación y operación en drones.

            - **Análisis de Convergencia**: Visualización completa del proceso de optimización
              generación por generación.

            ### Navegación

            Utilice la **barra lateral izquierda** para navegar entre las páginas del dashboard:

            - 🚀 **Nueva Optimización**: Configure y ejecute simulaciones de optimización
            - 📚 **Análisis de Sesiones**: Compare y analice múltiples resultados guardados
            - ℹ️ **Acerca del Proyecto**: Documentación técnica y fundamentos científicos

            ---

            ### Inicio Rápido

            1. Vaya a la página **🚀 Nueva Optimización**
            2. Configure los parámetros de diseño usando los controles deslizantes
            3. Presione **Ejecutar Optimización** y espere los resultados
            4. Analice los gráficos interactivos y métricas de rendimiento
            5. Descargue la sesión o exporte los datos para análisis posterior
            """
        )

    with col2:
        st.markdown("### Imagen del Proyecto")

        # Try to display the audit image if it exists
        audit_image_path = project_root / "scripts" / "audit" / "auditoria_eficiencia_vs_fd.png"

        if audit_image_path.exists():
            st.image(
                str(audit_image_path),
                caption="Eficiencia de apertura vs. Relación f/D",
                use_container_width=True,
            )
        else:
            st.info("Imagen de proyecto no disponible")

        st.markdown("---")

        # Quick stats
        st.markdown("### Especificaciones Técnicas")
        st.metric("Frecuencia de Operación", "2.4 GHz", help="Banda ISM estándar")
        st.metric("Rango de Diámetros", "5 cm - 3 m", help="Límites de fabricación")
        st.metric("Algoritmo", "NSGA-II", help="Non-dominated Sorting Genetic Algorithm II")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #667eea;'>
            <p>SOGA Dashboard v1.0 | Desarrollado con Streamlit y optimización evolutiva NSGA-II</p>
            <p>📧 Contacto: soporte@soga.dev | 📄 Documentación completa en la página "Acerca del Proyecto"</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
