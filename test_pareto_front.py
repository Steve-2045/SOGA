#!/usr/bin/env python3
"""
Script de prueba rápida para verificar la funcionalidad del frente de Pareto.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from soga.app.facade import ApplicationFacade

def test_pareto_front():
    """Test que el frente de Pareto se genera correctamente."""
    print("=" * 70)
    print("TEST: Verificación del Frente de Pareto")
    print("=" * 70)

    # Parámetros de prueba
    test_params = {
        "min_diameter_m": 0.2,
        "max_diameter_m": 1.0,
        "max_payload_g": 800,
        "min_f_d_ratio": 0.35,
        "max_f_d_ratio": 0.65,
        "desired_range_km": 5.0,
    }

    print("\n1. Parámetros de entrada:")
    for key, value in test_params.items():
        print(f"   {key}: {value}")

    print("\n2. Ejecutando optimización...")
    facade = ApplicationFacade()

    try:
        result = facade.run_optimization(test_params)

        print("\n3. ✅ Optimización exitosa!")
        print(f"\n4. Resultados del knee point:")
        print(f"   - Ganancia: {result['expected_gain_dbi']:.2f} dBi")
        print(f"   - Diámetro: {result['optimal_diameter_mm']:.2f} mm")
        print(f"   - f/D: {result['f_d_ratio']:.3f}")

        # Verificar frente de Pareto
        if "pareto_front" in result and result["pareto_front"]:
            pareto = result["pareto_front"]
            print(f"\n5. ✅ Frente de Pareto generado correctamente!")
            print(f"   - Número de soluciones: {len(pareto)}")
            print(f"   - Rango de ganancia: {min(p.gain for p in pareto):.2f} - {max(p.gain for p in pareto):.2f} dBi")
            print(f"   - Rango de peso: {min(p.weight*1000 for p in pareto):.1f} - {max(p.weight*1000 for p in pareto):.1f} g")

            # Mostrar primeras 5 soluciones
            print(f"\n6. Primeras 5 soluciones del frente de Pareto:")
            for i, point in enumerate(pareto[:5]):
                print(f"   {i+1}. D={point.diameter*1000:.1f}mm, f/D={point.f_d_ratio:.3f}, "
                      f"Ganancia={point.gain:.2f}dBi, Peso={point.weight*1000:.1f}g")

            print("\n" + "=" * 70)
            print("✅ PRUEBA EXITOSA: El frente de Pareto está funcionando correctamente")
            print("=" * 70)
            return True
        else:
            print("\n❌ ERROR: El frente de Pareto no está en los resultados")
            return False

    except Exception as e:
        print(f"\n❌ ERROR durante la optimización: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pareto_front()
    sys.exit(0 if success else 1)
