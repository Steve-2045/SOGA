"""Tests para el módulo infrastructure.file_io."""

import csv
import json
import tempfile
from pathlib import Path

import pytest

from soga.core.models import AntennaGeometry, OptimizationResult, PerformanceMetrics
from soga.infrastructure.file_io import SessionManager, ResultsExporter


@pytest.fixture
def sample_geometry():
    """Geometría de ejemplo para tests."""
    return AntennaGeometry(diameter=1.0, focal_length=0.5)


@pytest.fixture
def sample_result(sample_geometry):
    """Resultado de optimización de ejemplo para tests."""
    metrics = PerformanceMetrics(gain=35.0, beamwidth=2.5)
    return OptimizationResult(
        optimal_geometry=sample_geometry,
        performance_metrics=metrics,
        convergence_history=[30.0, 32.0, 34.0, 35.0],
    )


@pytest.fixture
def sample_user_params():
    """Parámetros de usuario de ejemplo."""
    return {
        "min_diameter_m": 0.2,
        "max_diameter_m": 1.5,
        "max_payload_g": 800,
        "desired_range_km": 8.0,
    }


class TestSessionManager:
    """Tests para SessionManager."""

    def test_save_session_creates_file(self, sample_user_params, sample_result):
        """Prueba que save_session crea un archivo JSON válido."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            SessionManager.save_session(temp_path, sample_user_params, sample_result)

            # Verificar que el archivo existe
            assert temp_path.exists()

            # Verificar que es JSON válido
            with open(temp_path, "r") as f:
                data = json.load(f)
                assert "user_parameters" in data
                assert "results" in data
        finally:
            temp_path.unlink()

    def test_save_session_preserves_data(self, sample_user_params, sample_result):
        """Prueba que save_session preserva correctamente todos los datos."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            SessionManager.save_session(temp_path, sample_user_params, sample_result)

            with open(temp_path, "r") as f:
                data = json.load(f)

            # Verificar parámetros de usuario
            assert data["user_parameters"] == sample_user_params

            # Verificar geometría
            assert data["results"]["geometry"]["diameter"] == 1.0
            assert data["results"]["geometry"]["focal_length"] == 0.5
            assert data["results"]["geometry"]["f_d_ratio"] == pytest.approx(0.5)

            # Verificar métricas
            assert data["results"]["performance"]["gain"] == 35.0
            assert data["results"]["performance"]["beamwidth"] == 2.5

            # Verificar historial
            assert data["results"]["convergence_history"] == [30.0, 32.0, 34.0, 35.0]
        finally:
            temp_path.unlink()

    def test_load_session_reads_file(self, sample_user_params, sample_result):
        """Prueba que load_session lee correctamente un archivo."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Guardar primero
            SessionManager.save_session(temp_path, sample_user_params, sample_result)

            # Luego cargar
            loaded_data = SessionManager.load_session(temp_path)

            assert "user_parameters" in loaded_data
            assert "results" in loaded_data
            assert loaded_data["user_parameters"] == sample_user_params
        finally:
            temp_path.unlink()

    def test_load_session_nonexistent_raises_error(self):
        """Prueba que cargar un archivo inexistente lanza FileNotFoundError."""
        nonexistent = Path("/tmp/nonexistent_session_12345.json")
        with pytest.raises(FileNotFoundError, match="no encontrado"):
            SessionManager.load_session(nonexistent)

    def test_load_session_invalid_json_raises_error(self):
        """Prueba que un archivo JSON inválido lanza ValueError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="JSON inválido"):
                SessionManager.load_session(temp_path)
        finally:
            temp_path.unlink()

    def test_load_session_invalid_structure_raises_error(self):
        """Prueba que una estructura inválida lanza ValueError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"wrong_key": "value"}, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Estructura de sesión inválida"):
                SessionManager.load_session(temp_path)
        finally:
            temp_path.unlink()

    def test_reconstruct_result_recreates_object(
        self, sample_user_params, sample_result
    ):
        """Prueba que reconstruct_result recrea correctamente el objeto."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Guardar y cargar
            SessionManager.save_session(temp_path, sample_user_params, sample_result)
            session_data = SessionManager.load_session(temp_path)

            # Reconstruir
            reconstructed = SessionManager.reconstruct_result(session_data)

            # Verificar que es del tipo correcto
            assert isinstance(reconstructed, OptimizationResult)
            assert isinstance(reconstructed.optimal_geometry, AntennaGeometry)
            assert isinstance(reconstructed.performance_metrics, PerformanceMetrics)

            # Verificar valores
            assert reconstructed.optimal_geometry.diameter == 1.0
            assert reconstructed.performance_metrics.gain == 35.0
            assert reconstructed.convergence_history == [30.0, 32.0, 34.0, 35.0]
        finally:
            temp_path.unlink()

    def test_reconstruct_result_invalid_data_raises_error(self):
        """Prueba que datos inválidos lanzan ValueError."""
        invalid_data = {"results": {"wrong": "structure"}}

        with pytest.raises(ValueError, match="Error al reconstruir"):
            SessionManager.reconstruct_result(invalid_data)


class TestResultsExporter:
    """Tests para ResultsExporter."""

    def test_export_to_csv_creates_file(self):
        """Prueba que export_to_csv crea un archivo CSV."""
        results = [
            {
                "diameter_mm": 500.0,
                "focal_length_mm": 225.0,
                "depth_mm": 69.44,
                "f_d_ratio": 0.45,
                "gain_dbi": 28.5,
                "beamwidth_deg": 4.2,
            }
        ]

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = Path(f.name)

        try:
            ResultsExporter.export_to_csv(results, temp_path)

            # Verificar que el archivo existe
            assert temp_path.exists()

            # Verificar contenido
            with open(temp_path, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 1
                assert float(rows[0]["diameter_mm"]) == 500.0
        finally:
            temp_path.unlink()

    def test_export_to_csv_multiple_results(self):
        """Prueba exportación de múltiples resultados."""
        results = [
            {
                "diameter_mm": 500.0,
                "focal_length_mm": 225.0,
                "depth_mm": 69.44,
                "f_d_ratio": 0.45,
                "gain_dbi": 28.5,
                "beamwidth_deg": 4.2,
            },
            {
                "diameter_mm": 800.0,
                "focal_length_mm": 360.0,
                "depth_mm": 111.11,
                "f_d_ratio": 0.45,
                "gain_dbi": 32.1,
                "beamwidth_deg": 2.6,
            },
        ]

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = Path(f.name)

        try:
            ResultsExporter.export_to_csv(results, temp_path)

            with open(temp_path, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 2
        finally:
            temp_path.unlink()

    def test_export_to_csv_empty_list_raises_error(self):
        """Prueba que una lista vacía lanza ValueError."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="vacía"):
                ResultsExporter.export_to_csv([], temp_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_export_to_csv_missing_keys_raises_error(self):
        """Prueba que faltan claves lanza ValueError."""
        results = [
            {
                "diameter_mm": 500.0,
                # Faltan otras claves requeridas
            }
        ]

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Faltan claves"):
                ResultsExporter.export_to_csv(results, temp_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_export_convergence_to_csv_creates_file(self):
        """Prueba que export_convergence_to_csv crea un archivo."""
        history = [25.5, 26.1, 26.8, 27.2, 27.5]

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = Path(f.name)

        try:
            ResultsExporter.export_convergence_to_csv(history, temp_path)

            # Verificar que el archivo existe
            assert temp_path.exists()

            # Verificar contenido
            with open(temp_path, "r") as f:
                reader = csv.reader(f)
                rows = list(reader)
                assert len(rows) == 6  # header + 5 data rows
                assert rows[0] == ["generation", "best_gain_dbi"]
                assert float(rows[1][1]) == 25.5
        finally:
            temp_path.unlink()

    def test_export_convergence_empty_raises_error(self):
        """Prueba que un historial vacío lanza ValueError."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="vacío"):
                ResultsExporter.export_convergence_to_csv([], temp_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()
