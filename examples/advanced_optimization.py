#!/usr/bin/env python3
"""
Ejemplo avanzado de uso del backend SOGA.

Este script demuestra cómo usar OptimizationEngine directamente
para tener control completo sobre el proceso de optimización.
"""

from soga.core.optimization import OptimizationEngine
from soga.core.models import OptimizationConstraints
import matplotlib.pyplot as plt


def main():
    print("=" * 60)
    print("SOGA - Ejemplo Avanzado: Optimización con Control Total")
    print("=" * 60)
    print()

    # Crear motor con parámetros personalizados
    print("Configurando motor de optimización...")
    engine = OptimizationEngine(
        population_size=50,      # Población más grande para mejor exploración
        max_generations=100,     # Más generaciones para mejor convergencia
        seed=42                  # Semilla personalizada para reproducibilidad
    )
    print(f"  - Población: {engine.population_size} individuos")
    print(f"  - Generaciones: {engine.max_generations}")
    print(f"  - Semilla: {engine.seed}")
    print()

    # Definir restricciones de bajo nivel
    print("Definiendo restricciones del problema...")
    constraints = OptimizationConstraints(
        min_diameter=0.1,        # 10 cm
        max_diameter=2.0,        # 2 m
        max_weight=1.0,          # 1 kg
        min_f_d_ratio=0.3,       # Parábola profunda
        max_f_d_ratio=0.8,       # Parábola plana
        desired_range_km=10.0    # 10 km (informativo)
    )
    print(f"  - Diámetro: {constraints.min_diameter}-{constraints.max_diameter} m")
    print(f"  - Peso máximo: {constraints.max_weight} kg")
    print(f"  - f/D ratio: {constraints.min_f_d_ratio}-{constraints.max_f_d_ratio}")
    print()

    # Ejecutar optimización
    print("Ejecutando optimización avanzada...")
    print("(Esto puede tomar 30-60 segundos)")
    print()
    
    result = engine.run(constraints)

    # Mostrar resultados detallados
    print("=" * 60)
    print("RESULTADOS DETALLADOS")
    print("=" * 60)
    print()

    print("Geometría Óptima:")
    print(f"  - Diámetro: {result.optimal_geometry.diameter:.4f} m = {result.optimal_geometry.diameter*1000:.2f} mm")
    print(f"  - Distancia focal: {result.optimal_geometry.focal_length:.4f} m = {result.optimal_geometry.focal_length*1000:.2f} mm")
    print(f"  - Profundidad: {result.optimal_geometry.depth:.4f} m = {result.optimal_geometry.depth*1000:.2f} mm")
    print(f"  - Relación f/D: {result.optimal_geometry.f_d_ratio:.4f}")
    print()

    print("Métricas de Rendimiento:")
    print(f"  - Ganancia: {result.performance_metrics.gain:.3f} dBi")
    print(f"  - Ancho de haz (-3dB): {result.performance_metrics.beamwidth:.3f}°")
    print()

    # Calcular peso
    import math
    from soga.infrastructure.config import get_config
    
    config = get_config()
    area = math.pi * (result.optimal_geometry.diameter / 2) ** 2
    weight_kg = area * config.simulation.areal_density_kg_per_m2
    
    print("Estimaciones Físicas:")
    print(f"  - Área efectiva: {area:.6f} m²")
    print(f"  - Peso estimado: {weight_kg:.4f} kg = {weight_kg*1000:.1f} g")
    print(f"  - Cumple restricción: {'✓' if weight_kg <= constraints.max_weight else '✗'}")
    print()

    # Análisis de convergencia
    print("Análisis de Convergencia:")
    print(f"  - Generaciones ejecutadas: {len(result.convergence_history)}")
    if len(result.convergence_history) > 0:
        print(f"  - Ganancia inicial: {result.convergence_history[0]:.3f} dBi")
        print(f"  - Ganancia final: {result.convergence_history[-1]:.3f} dBi")
        improvement = result.convergence_history[-1] - result.convergence_history[0]
        print(f"  - Mejora total: {improvement:.3f} dB ({improvement/result.convergence_history[0]*100:.1f}%)")
        
        # Detectar estancamiento
        last_20_pct = max(1, len(result.convergence_history) // 5)
        recent_improvement = result.convergence_history[-1] - result.convergence_history[-last_20_pct]
        print(f"  - Mejora últimas {last_20_pct} generaciones: {recent_improvement:.4f} dB")
        
        if abs(recent_improvement) < 0.01:
            print("  - Estado: CONVERGIDO (mejora < 0.01 dB)")
        else:
            print("  - Estado: MEJORANDO (puede beneficiarse de más generaciones)")
    print()

    # Visualizar convergencia
    print("Generando gráfico de convergencia...")
    plot_convergence(result.convergence_history)
    print("  - Gráfico guardado como 'convergence.png'")
    print()

    print("=" * 60)
    print("¡Optimización avanzada completada!")
    print("=" * 60)


def plot_convergence(history):
    """Genera un gráfico de la convergencia del algoritmo."""
    if not history:
        print("No hay datos de convergencia para graficar")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(history, linewidth=2, color='#2E86AB')
    plt.xlabel('Generación', fontsize=12)
    plt.ylabel('Mejor Ganancia (dBi)', fontsize=12)
    plt.title('Convergencia del Algoritmo NSGA-II', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('convergence.png', dpi=150, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    main()
