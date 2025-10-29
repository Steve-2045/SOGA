#!/usr/bin/env python3
"""
Ejemplo básico de uso del backend SOGA.

Este script demuestra cómo usar ApplicationFacade para optimizar
una antena parabólica con parámetros simples.
"""

from soga.app.facade import ApplicationFacade


def main():
    print("=" * 60)
    print("SOGA - Software de Optimización Geométrica de Antenas")
    print("Ejemplo: Optimización Básica")
    print("=" * 60)
    print()

    # Crear instancia de la fachada
    facade = ApplicationFacade()

    # Definir parámetros de optimización
    # Estos son parámetros de alto nivel comprensibles para el usuario
    params = {
        "min_diameter_m": 0.2,  # Diámetro mínimo: 20 cm
        "max_diameter_m": 1.5,  # Diámetro máximo: 1.5 m
        "max_payload_g": 800.0,  # Peso máximo: 800 gramos
        "min_f_d_ratio": 0.35,  # Relación focal mínima
        "max_f_d_ratio": 0.65,  # Relación focal máxima
        "desired_range_km": 5.0,  # Alcance deseado: 5 km
    }

    print("Parámetros de entrada:")
    print(
        f"  - Diámetro: {params['min_diameter_m']:.2f} - {params['max_diameter_m']:.2f} m"
    )
    print(f"  - Peso máximo: {params['max_payload_g']:.0f} g")
    print(
        f"  - Relación f/D: {params['min_f_d_ratio']:.2f} - {params['max_f_d_ratio']:.2f}"
    )
    print(f"  - Alcance deseado: {params['desired_range_km']:.1f} km")
    print()

    print("Ejecutando optimización...")
    print("(Esto puede tomar 10-20 segundos)")
    print()

    # Ejecutar optimización
    result = facade.run_optimization(params)

    # Mostrar resultados
    print("=" * 60)
    print("RESULTADOS DE LA OPTIMIZACIÓN")
    print("=" * 60)
    print()

    print("Geometría Óptima:")
    print(
        f"  - Diámetro: {result['optimal_diameter_mm']:.2f} mm ({result['optimal_diameter_mm']/10:.1f} cm)"
    )
    print(
        f"  - Distancia focal: {result['optimal_focal_length_mm']:.2f} mm ({result['optimal_focal_length_mm']/10:.1f} cm)"
    )
    print(
        f"  - Profundidad: {result['optimal_depth_mm']:.2f} mm ({result['optimal_depth_mm']/10:.1f} cm)"
    )
    print(f"  - Relación f/D: {result['f_d_ratio']:.3f}")
    print()

    print("Métricas de Rendimiento:")
    print(f"  - Ganancia esperada: {result['expected_gain_dbi']:.2f} dBi")
    print(f"  - Ancho de haz: {result['beamwidth_deg']:.2f}°")
    print()

    print("Convergencia del Algoritmo:")
    print(f"  - Generaciones ejecutadas: {len(result['convergence'])}")
    if result["convergence"]:
        print(f"  - Ganancia inicial: {result['convergence'][0]:.2f} dBi")
        print(f"  - Ganancia final: {result['convergence'][-1]:.2f} dBi")
        print(
            f"  - Mejora: {result['convergence'][-1] - result['convergence'][0]:.2f} dB"
        )
    print()

    # Cálculo estimado de peso (asumiendo densidad de config.toml)
    import math
    from soga.infrastructure.config import get_config

    config = get_config()
    diameter_m = result["optimal_diameter_mm"] / 1000.0
    area_m2 = math.pi * (diameter_m / 2) ** 2
    estimated_weight_kg = area_m2 * config.simulation.reflector_areal_density_kg_per_m2
    estimated_weight_g = estimated_weight_kg * 1000

    print("Estimaciones Adicionales:")
    print(f"  - Área del reflector: {area_m2:.4f} m²")
    print(f"  - Peso estimado: {estimated_weight_g:.1f} g")
    print(
        f"  - Cumple restricción de peso: {'✓ SÍ' if estimated_weight_g <= params['max_payload_g'] else '✗ NO'}"
    )
    print()

    print("=" * 60)
    print("¡Optimización completada exitosamente!")
    print("=" * 60)


if __name__ == "__main__":
    main()
