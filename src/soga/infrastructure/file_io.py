"""
Módulo de entrada/salida de archivos.

Proporciona funcionalidades para:
- Guardar y cargar sesiones de trabajo en formato JSON
- Exportar resultados en formatos 2D (JSON, CSV)
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from soga.core.models import AntennaGeometry, OptimizationResult, PerformanceMetrics


class SessionManager:
    """
    Gestiona la persistencia de sesiones de trabajo.

    Una sesión incluye los parámetros de entrada del usuario y los resultados
    de la optimización. Sigue el principio KISS: formato JSON simple.
    """

    @staticmethod
    def save_session(
        filepath: Path,
        user_parameters: Dict[str, Any],
        optimization_result: OptimizationResult,
    ) -> None:
        """
        Guarda una sesión de trabajo en formato JSON.

        Args:
            filepath: Ruta donde guardar la sesión (extensión .json recomendada).
            user_parameters: Parámetros de entrada del usuario.
            optimization_result: Resultado de la optimización.

        Raises:
            IOError: Si no se puede escribir el archivo.
            ValueError: Si los datos no son serializables.

        Examples:
            >>> result = OptimizationResult(...)
            >>> SessionManager.save_session(
            ...     Path("my_session.json"),
            ...     {"max_diameter_m": 1.5},
            ...     result
            ... )
        """
        # Construir el diccionario de sesión
        session_data = {
            "user_parameters": user_parameters,
            "results": {
                "geometry": {
                    "diameter": optimization_result.optimal_geometry.diameter,
                    "focal_length": optimization_result.optimal_geometry.focal_length,
                    "depth": optimization_result.optimal_geometry.depth,
                    "f_d_ratio": optimization_result.optimal_geometry.f_d_ratio,
                },
                "performance": {
                    "gain": optimization_result.performance_metrics.gain,
                    "beamwidth": optimization_result.performance_metrics.beamwidth,
                },
                "convergence_history": optimization_result.convergence_history,
            },
        }

        # Guardar como JSON
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        except (IOError, TypeError) as e:
            raise IOError(f"Error al guardar la sesión en {filepath}: {e}") from e

    @staticmethod
    def load_session(filepath: Path) -> Dict[str, Any]:
        """
        Carga una sesión de trabajo desde un archivo JSON.

        Args:
            filepath: Ruta al archivo de sesión.

        Returns:
            Diccionario con la sesión cargada. Estructura:
                {
                    "user_parameters": {...},
                    "results": {
                        "geometry": {...},
                        "performance": {...},
                        "convergence_history": [...]
                    }
                }

        Raises:
            FileNotFoundError: Si el archivo no existe.
            ValueError: Si el archivo JSON es inválido.

        Examples:
            >>> session = SessionManager.load_session(Path("my_session.json"))
            >>> print(session["results"]["geometry"]["diameter"])
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Archivo de sesión no encontrado: {filepath}")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                session_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Archivo JSON inválido en {filepath}: {e}") from e
        except IOError as e:
            raise IOError(f"Error al leer el archivo {filepath}: {e}") from e

        # Validar estructura básica
        if "user_parameters" not in session_data or "results" not in session_data:
            raise ValueError(
                f"Estructura de sesión inválida en {filepath}: "
                "falta 'user_parameters' o 'results'"
            )

        return session_data

    @staticmethod
    def reconstruct_result(session_data: Dict[str, Any]) -> OptimizationResult:
        """
        Reconstruye un OptimizationResult desde los datos de sesión.

        Args:
            session_data: Datos de sesión cargados con load_session().

        Returns:
            OptimizationResult reconstruido.

        Raises:
            ValueError: Si los datos son inválidos o incompletos.

        Examples:
            >>> session = SessionManager.load_session(Path("session.json"))
            >>> result = SessionManager.reconstruct_result(session)
        """
        try:
            results = session_data["results"]

            geometry = AntennaGeometry(
                diameter=results["geometry"]["diameter"],
                focal_length=results["geometry"]["focal_length"],
            )

            performance = PerformanceMetrics(
                gain=results["performance"]["gain"],
                beamwidth=results["performance"]["beamwidth"],
            )

            convergence = results.get("convergence_history", [])

            return OptimizationResult(
                optimal_geometry=geometry,
                performance_metrics=performance,
                convergence_history=convergence,
            )
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Error al reconstruir el resultado: {e}") from e


class ResultsExporter:
    """
    Exporta resultados de optimización a formatos estándar 2D.

    Soporta exportación a CSV para análisis y reportes.
    """

    @staticmethod
    def export_to_csv(
        results: List[Dict[str, Any]],
        filepath: Path,
    ) -> None:
        """
        Exporta múltiples resultados de optimización a formato CSV.

        Args:
            results: Lista de diccionarios con resultados. Cada diccionario debe
                    contener las claves: diameter_mm, focal_length_mm, depth_mm,
                    f_d_ratio, gain_dbi, beamwidth_deg.
            filepath: Ruta donde guardar el archivo CSV.

        Raises:
            IOError: Si no se puede escribir el archivo.
            ValueError: Si los datos son inválidos.

        Examples:
            >>> results = [
            ...     {
            ...         "diameter_mm": 500.0,
            ...         "focal_length_mm": 225.0,
            ...         "depth_mm": 69.44,
            ...         "f_d_ratio": 0.45,
            ...         "gain_dbi": 28.5,
            ...         "beamwidth_deg": 4.2
            ...     }
            ... ]
            >>> ResultsExporter.export_to_csv(results, Path("results.csv"))
        """
        if not results:
            raise ValueError("La lista de resultados está vacía")

        # Definir columnas esperadas
        fieldnames = [
            "diameter_mm",
            "focal_length_mm",
            "depth_mm",
            "f_d_ratio",
            "gain_dbi",
            "beamwidth_deg",
        ]

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for result in results:
                    # Validar que todas las claves requeridas existen
                    missing_keys = set(fieldnames) - set(result.keys())
                    if missing_keys:
                        raise ValueError(
                            f"Faltan claves requeridas en resultado: {missing_keys}"
                        )

                    # Escribir fila con solo las columnas requeridas
                    row = {key: result[key] for key in fieldnames}
                    writer.writerow(row)

        except (IOError, OSError) as e:
            raise IOError(f"Error al guardar el archivo CSV en {filepath}: {e}") from e

    @staticmethod
    def export_convergence_to_csv(
        convergence_history: List[float],
        filepath: Path,
    ) -> None:
        """
        Exporta el historial de convergencia a formato CSV.

        Args:
            convergence_history: Lista con los valores de convergencia por generación.
            filepath: Ruta donde guardar el archivo CSV.

        Raises:
            IOError: Si no se puede escribir el archivo.
            ValueError: Si el historial está vacío.

        Examples:
            >>> history = [25.5, 26.1, 26.8, 27.2, 27.5]
            >>> ResultsExporter.export_convergence_to_csv(
            ...     history,
            ...     Path("convergence.csv")
            ... )
        """
        if not convergence_history:
            raise ValueError("El historial de convergencia está vacío")

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["generation", "best_gain_dbi"])

                for generation, gain in enumerate(convergence_history):
                    writer.writerow([generation, gain])

        except (IOError, OSError) as e:
            raise IOError(
                f"Error al guardar el historial de convergencia en {filepath}: {e}"
            ) from e
