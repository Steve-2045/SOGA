"""Tests para el módulo infrastructure.config."""

import tempfile
from pathlib import Path

import pytest

from soga.infrastructure.config import (
    AppConfig,
    ConfigLoader,
    OptimizationConfig,
    PhysicsConfig,
    RegulatoryConfig,
    SimulationConfig,
    UserDefaultsConfig,
    get_config,
    reload_config,
)


@pytest.fixture
def valid_config_content():
    """Contenido válido de un archivo de configuración."""
    return """
[physics]
speed_of_light = 299792458.0

[simulation]
frequency_ghz = 2.4
aperture_efficiency = 0.6
areal_density_kg_per_m2 = 1.5
beamwidth_k_factor = 65.0
efficiency_peak = 0.70
optimal_f_d_ratio = 0.45
curvature_low_fd = 0.128
curvature_high_fd = 0.236

[optimization]
population_size = 40
max_generations = 80
seed = 1

[user_defaults]
min_diameter_m = 0.1
max_diameter_m = 2.0
max_payload_g = 1000.0
min_f_d_ratio = 0.3
max_f_d_ratio = 0.8
desired_range_km = 5.0

[regulatory]
max_eirp_dbm = 36.0

[realistic_limits]
min_diameter_m = 0.05
max_diameter_m = 3.0
min_payload_g = 10.0
max_payload_g = 5000.0
min_f_d_ratio = 0.2
max_f_d_ratio = 1.5
min_range_km = 0.1
max_range_km = 50.0
"""


@pytest.fixture
def temp_config_file(valid_config_content):
    """Crea un archivo de configuración temporal para tests."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(valid_config_content)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    temp_path.unlink()


class TestConfigLoader:
    """Tests para ConfigLoader."""

    def test_load_valid_config(self, temp_config_file):
        """Prueba cargar un archivo de configuración válido."""
        config = ConfigLoader.load(temp_config_file)

        assert isinstance(config, AppConfig)
        assert config.physics.speed_of_light == 299792458.0
        assert config.simulation.frequency_ghz == 2.4
        assert config.optimization.population_size == 40

    def test_load_nonexistent_file_raises_error(self):
        """Prueba que un archivo inexistente lanza FileNotFoundError."""
        nonexistent = Path("/tmp/nonexistent_config_12345.toml")
        with pytest.raises(FileNotFoundError, match="no encontrado"):
            ConfigLoader.load(nonexistent)

    def test_load_invalid_toml_raises_error(self):
        """Prueba que un archivo TOML inválido lanza ValueError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("invalid {{{ toml")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Error al leer"):
                ConfigLoader.load(temp_path)
        finally:
            temp_path.unlink()

    def test_load_missing_section_raises_error(self):
        """Prueba que la falta de una sección requerida lanza ValueError."""
        incomplete_config = """
[physics]
speed_of_light = 299792458.0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(incomplete_config)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Configuración inválida"):
                ConfigLoader.load(temp_path)
        finally:
            temp_path.unlink()

    def test_find_default_config(self):
        """Prueba que encuentra el archivo config.toml por defecto."""
        config_path = ConfigLoader._find_default_config()
        assert config_path.name == "config.toml"
        # Debería existir en el proyecto
        assert config_path.exists()


class TestConfigDataclasses:
    """Tests para las dataclasses de configuración."""

    def test_physics_config(self):
        """Prueba la creación de PhysicsConfig."""
        physics = PhysicsConfig(speed_of_light=299792458.0)
        assert physics.speed_of_light == 299792458.0

    def test_simulation_config(self):
        """Prueba la creación de SimulationConfig."""
        sim = SimulationConfig(
            frequency_ghz=2.4,
            aperture_efficiency=0.6,
            areal_density_kg_per_m2=1.5,
            beamwidth_k_factor=70.0,
            efficiency_peak=0.70,
            optimal_f_d_ratio=0.45,
            curvature_low_fd=0.128,
            curvature_high_fd=0.236,
        )
        assert sim.frequency_ghz == 2.4
        assert sim.aperture_efficiency == 0.6
        assert sim.efficiency_peak == 0.70

    def test_optimization_config(self):
        """Prueba la creación de OptimizationConfig."""
        opt = OptimizationConfig(population_size=40, max_generations=80, seed=1)
        assert opt.population_size == 40
        assert opt.max_generations == 80

    def test_user_defaults_config(self):
        """Prueba la creación de UserDefaultsConfig."""
        defaults = UserDefaultsConfig(
            min_diameter_m=0.1,
            max_diameter_m=2.0,
            max_payload_g=1000.0,
            min_f_d_ratio=0.3,
            max_f_d_ratio=0.8,
            desired_range_km=5.0,
        )
        assert defaults.min_diameter_m == 0.1
        assert defaults.desired_range_km == 5.0

    def test_regulatory_config(self):
        """Prueba la creación de RegulatoryConfig."""
        reg = RegulatoryConfig(max_eirp_dbm=36.0)
        assert reg.max_eirp_dbm == 36.0

    def test_app_config_complete(self, temp_config_file):
        """Prueba que AppConfig contiene todas las secciones."""
        config = ConfigLoader.load(temp_config_file)

        assert hasattr(config, "physics")
        assert hasattr(config, "simulation")
        assert hasattr(config, "optimization")
        assert hasattr(config, "user_defaults")
        assert hasattr(config, "regulatory")
        assert hasattr(config, "realistic_limits")


class TestGlobalConfigHelpers:
    """Tests para las funciones helper de configuración global."""

    def test_get_config_returns_singleton(self):
        """Prueba que get_config retorna siempre la misma instancia."""
        config1 = get_config()
        config2 = get_config()

        # Deben ser la misma instancia (singleton)
        assert config1 is config2

    def test_reload_config_updates_singleton(self, temp_config_file):
        """Prueba que reload_config actualiza la instancia global."""
        # Cargar configuración inicial
        get_config()

        # Crear nueva configuración con valor diferente
        modified_content = """
[physics]
speed_of_light = 299792458.0

[simulation]
frequency_ghz = 24.0
aperture_efficiency = 0.6
areal_density_kg_per_m2 = 1.5
beamwidth_k_factor = 65.0
efficiency_peak = 0.70
optimal_f_d_ratio = 0.45
curvature_low_fd = 0.128
curvature_high_fd = 0.236

[optimization]
population_size = 40
max_generations = 80
seed = 1

[user_defaults]
min_diameter_m = 0.1
max_diameter_m = 2.0
max_payload_g = 1000.0
min_f_d_ratio = 0.3
max_f_d_ratio = 0.8
desired_range_km = 5.0

[regulatory]
max_eirp_dbm = 36.0

[realistic_limits]
min_diameter_m = 0.05
max_diameter_m = 3.0
min_payload_g = 10.0
max_payload_g = 5000.0
min_f_d_ratio = 0.2
max_f_d_ratio = 1.5
min_range_km = 0.1
max_range_km = 50.0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(modified_content)
            new_config_path = Path(f.name)

        try:
            # Recargar con nueva configuración
            config2 = reload_config(new_config_path)

            # Debería tener el nuevo valor
            assert config2.simulation.frequency_ghz == 24.0

            # get_config() debería retornar la nueva configuración
            config3 = get_config()
            assert config3.simulation.frequency_ghz == 24.0
        finally:
            new_config_path.unlink()
            # Restaurar configuración por defecto
            reload_config()
