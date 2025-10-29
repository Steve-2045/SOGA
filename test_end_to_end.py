#!/usr/bin/env python3
"""
Script de prueba end-to-end para SOGA.
Verifica que todo el pipeline de optimización funciona correctamente.
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from soga.app.facade import ApplicationFacade
from soga.infrastructure.config import get_config

def test_optimization_pipeline():
    """Prueba el pipeline completo de optimización."""

    print("=" * 70)
    print("PRUEBA END-TO-END: Pipeline de Optimización SOGA")
    print("=" * 70)

    # 1. Cargar configuración
    print("\n[1/4] Cargando configuración...")
    try:
        config = get_config()
        print(f"✅ Configuración cargada: frequency={config.simulation.frequency_ghz} GHz")
        print(f"✅ Densidad reflector: {config.simulation.reflector_areal_density_kg_per_m2} kg/m²")
    except Exception as e:
        print(f"❌ Error al cargar configuración: {e}")
        return False

    # 2. Crear facade
    print("\n[2/4] Inicializando ApplicationFacade...")
    try:
        facade = ApplicationFacade()
        print("✅ Facade creado exitosamente")
    except Exception as e:
        print(f"❌ Error al crear facade: {e}")
        return False

    # 3. Definir parámetros de prueba
    print("\n[3/4] Definiendo parámetros de optimización...")
    user_params = {
        "min_diameter_m": 0.5,
        "max_diameter_m": 1.5,
        "max_payload_g": 1000.0,
        "min_f_d_ratio": 0.35,
        "max_f_d_ratio": 0.65,
        "desired_range_km": 5.0,
    }
    print(f"✅ Parámetros definidos:")
    for key, value in user_params.items():
        print(f"   - {key}: {value}")

    # 4-5. Ejecutar optimización (incluye validación interna)
    print("\n[4/4] Ejecutando optimización NSGA-II...")
    print("   (Esto incluye validación de parámetros y optimización)")
    print("   (Puede tomar 10-30 segundos...)")

    try:
        result = facade.run_optimization(user_params)

        print("\n✅ OPTIMIZACIÓN COMPLETADA EXITOSAMENTE")
        print("\n" + "=" * 70)
        print("RESULTADOS DE LA OPTIMIZACIÓN")
        print("=" * 70)

        # Mostrar geometría óptima
        print("\n📐 Geometría Óptima:")
        print(f"   - Diámetro: {result['optimal_diameter_mm']:.2f} mm ({result['optimal_diameter_mm']/1000:.3f} m)")
        print(f"   - Distancia focal: {result['optimal_focal_length_mm']:.2f} mm ({result['optimal_focal_length_mm']/1000:.3f} m)")
        print(f"   - Relación f/D: {result['f_d_ratio']:.3f}")
        print(f"   - Profundidad: {result['optimal_depth_mm']:.2f} mm ({result['optimal_depth_mm']/1000:.4f} m)")

        # Mostrar métricas de rendimiento
        print("\n📊 Métricas de Rendimiento:")
        print(f"   - Ganancia: {result['expected_gain_dbi']:.2f} dBi")
        print(f"   - Ancho de haz: {result['beamwidth_deg']:.2f}°")

        # Mostrar información del frente de Pareto
        print("\n🎯 Frente de Pareto:")
        print(f"   - Soluciones encontradas: {len(result['pareto_front'])}")

        # Mostrar convergencia
        print("\n📈 Convergencia:")
        print(f"   - Generaciones ejecutadas: {len(result['convergence'])}")
        print(f"   - Mejor ganancia inicial: {result['convergence'][0]:.2f} dBi")
        print(f"   - Mejor ganancia final: {result['convergence'][-1]:.2f} dBi")
        print(f"   - Mejora total: {result['convergence'][-1] - result['convergence'][0]:.2f} dB")

        print("\n" + "=" * 70)
        print("✅ PRUEBA END-TO-END COMPLETADA EXITOSAMENTE")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n❌ Error durante la optimización: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_optimization_pipeline()
    sys.exit(0 if success else 1)
