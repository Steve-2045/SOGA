# Compromisos Desfavorables en el Diseño de Antenas Parabólicas

## Contexto: Agricultura de Precisión

Este documento analiza los trade-offs en el diseño de **antenas parabólicas terrestres** para comunicación con drones en agricultura de precisión. Las antenas se instalan en ubicaciones fijas o semi-portátiles en tierra para establecer enlaces de largo alcance con UAVs.

## Resumen Ejecutivo

El sistema SOGA visualiza el **frente de Pareto**, que muestra explícitamente todos los **trade-offs** (compromisos desfavorables) entre los diferentes objetivos de optimización: ganancia, peso, geometría y alcance.

---

## 1. Compromiso Principal: Ganancia vs Peso

### Descripción del Conflicto

Este es el trade-off más fundamental en el diseño de antenas parabólicas terrestres para comunicación con UAVs:

- **Mayor ganancia** → Requiere **mayor diámetro** → **Mayor peso**
- **Menor peso** → Requiere **menor diámetro** → **Menor ganancia**

### Visualización en el Frente de Pareto

El gráfico muestra claramente esta relación:

```
Ganancia (dBi)
    ↑
 25 |                                        • ← Antena grande/pesada
    |                                    •  •
 20 |                              •  •  •
    |                         •  •  •
 15 |                    •  •  ★  ← Knee point (óptimo)
    |               •  •  •
 10 |          •  •  •
    |     •  •  ← Antena pequeña/ligera
  5 |  •
    └─────────────────────────────────────────→ Peso (g)
        100    300    500    700    900
```

### Ejemplo Cuantitativo (Datos Reales)

De una optimización típica (min_D=0.2m, max_D=1.0m, max_peso=800g):

| Solución | Diámetro | Peso | Ganancia | Descripción |
|----------|----------|------|----------|-------------|
| 1 (Ligera) | 200 mm | 57 g | 12.5 dBi | Muy ligera pero poca ganancia |
| 2 (Balanceada) | 440 mm | 274 g | 19.3 dBi | **Knee point** - mejor compromiso |
| 3 (Pesada) | 752 mm | 800 g | 24.0 dBi | Máxima ganancia pero muy pesada |

**Trade-off cuantificado**: ~0.015 dBi/g
- Por cada gramo adicional, se gana aproximadamente 0.015 dBi
- Para ganar 1 dBi adicional, se necesitan ~67 gramos más

---

## 2. Compromiso Secundario: Eficiencia de Apertura vs Geometría (f/D)

### Descripción del Conflicto

La relación focal f/D afecta la eficiencia de apertura de manera asimétrica:

- **f/D bajo (< 0.45)**: Parábola profunda
  - Problema: **Blockage** (bloqueo por el feed)
  - Pérdida de eficiencia: **Moderada** (~2-3%)

- **f/D alto (> 0.45)**: Parábola plana
  - Problema: **Spillover** (energía derramada fuera del borde)
  - Pérdida de eficiencia: **Severa** (~5-8%)

### Modelo Matemático del Trade-off

```
η(f/D) = η_peak - κ(f/D) × (f/D - 0.45)²

donde:
  κ(f/D) = { 0.128  si f/D < 0.45  (blockage)
           { 0.236  si f/D ≥ 0.45  (spillover)
```

**Ratio de asimetría**: 0.236/0.128 = **1.84×**
- El spillover degrada la eficiencia 1.84 veces más rápido que el blockage

### Ejemplo Cuantitativo

| f/D | Eficiencia | Pérdida vs Óptimo | Tipo de Pérdida |
|-----|------------|-------------------|-----------------|
| 0.20 | 69.2% | -0.8% | Blockage moderado |
| 0.45 | **70.0%** | **0%** (óptimo) | - |
| 0.70 | 68.5% | -1.5% | Spillover moderado |
| 1.00 | 62.9% | -7.1% | Spillover severo |

---

## 3. Trade-off Implícito: Diámetro vs Profundidad

### Descripción del Conflicto

Aunque no es un objetivo de optimización explícito, existe un compromiso geométrico:

**Profundidad = D² / (16 × f)**

Para una f/D fija:
- **Mayor diámetro** → **Mayor profundidad** → Más difícil de fabricar/transportar
- **Menor diámetro** → **Menor profundidad** → Más fácil pero menor ganancia

### Ejemplo con f/D = 0.45 Constante

| Diámetro | Focal | Profundidad | Dificultad Fabricación |
|----------|-------|-------------|------------------------|
| 200 mm | 90 mm | 28 mm | Muy fácil |
| 500 mm | 225 mm | 69 mm | Moderada |
| 1000 mm | 450 mm | 139 mm | Difícil (parábola muy honda) |

---

## 4. Trade-off de Peso vs Resistencia Estructural

### Descripción del Conflicto

El modelo actual usa densidad areal constante (1.8 kg/m²), pero en la práctica:

- **Antenas grandes** (>500mm) requieren **refuerzos estructurales**
  - Peso real > peso calculado
  - Densidad areal efectiva aumenta con el diámetro

- **Antenas pequeñas** (<300mm) pueden usar **materiales más ligeros**
  - Peso real ≈ peso calculado
  - Mayor margen de carga útil disponible

### Impacto en Diseño de Estación Terrestre

Para una estación terrestre con límite de 800g (portabilidad manual):

| Antena | Peso Calculado | Peso Real Estimado | % del Límite |
|--------|----------------|-------------------|--------------|
| 200 mm | 57 g | ~60 g | 7.5% |
| 500 mm | 354 g | ~400 g | 50% |
| 750 mm | 797 g | **>900 g** | **>100% ⚠️** |

---

## 5. Compromiso Operacional: Ancho de Haz vs Ganancia

### Descripción del Conflicto

Relación inversa fundamental de antenas:

**HPBW ≈ 70λ / D**

- **Mayor ganancia** (D grande) → **Ancho de haz estrecho** → Difícil apuntamiento
- **Menor ganancia** (D pequeña) → **Ancho de haz amplio** → Fácil apuntamiento

### Ejemplo Cuantitativo (2.4 GHz)

| Diámetro | Ganancia | HPBW | Precisión Requerida |
|----------|----------|------|---------------------|
| 200 mm | 12.5 dBi | 36.2° | Baja (tolera ±18°) |
| 500 mm | 20.8 dBi | 14.5° | Media (tolera ±7°) |
| 1000 mm | 26.8 dBi | 7.2° | Alta (tolera ±3.6°) |

**Implicaciones**:
- Antenas grandes requieren sistemas de tracking más precisos
- Antenas pequeñas son más tolerantes a vibraciones ambientales (viento, etc.)

---

## 6. Visualización Integrada en SOGA

### Cómo Interpretar el Frente de Pareto

El nuevo tab **"📊 Frente de Pareto"** muestra:

1. **Puntos azules**: Todas las configuraciones óptimas (no-dominadas)
   - No se puede mejorar un objetivo sin empeorar el otro

2. **Estrella roja**: Knee point (solución recomendada)
   - Mejor balance automáticamente calculado
   - Punto de máxima curvatura del frente

3. **Métricas mostradas**:
   - Número de soluciones encontradas (~40 típicamente)
   - Rango de ganancia (ej: 12.5 - 24.0 dBi)
   - Rango de peso (ej: 57 - 800 g)
   - **Trade-off ratio** (dBi/g)

### Uso Práctico

1. **Si priorizas peso ligero**: Selecciona soluciones en zona izquierda del frente
2. **Si priorizas ganancia**: Selecciona soluciones en zona derecha del frente
3. **Si buscas balance**: Usa el knee point (recomendado)

---

## 7. Recomendaciones de Diseño

### Escenarios Típicos

#### Estación Portátil Ligera (Prioridad: Portabilidad)
- **Objetivo**: Máxima movilidad para instalación rápida en campo
- **Solución**: Zona izquierda del frente (peso < 200g)
- **Trade-off aceptado**: Ganancia reducida (12-16 dBi)
- **Beneficio**: Fácil transporte, instalación rápida sin herramientas

#### Estación Fija de Alto Rendimiento (Prioridad: Ganancia)
- **Objetivo**: Maximizar alcance de comunicación con UAVs
- **Solución**: Zona derecha del frente (peso > 500g)
- **Trade-off aceptado**: Mayor peso y complejidad de instalación
- **Beneficio**: Alcance de comunicación >10 km

#### Estación Semi-Portátil (Prioridad: Balance)
- **Objetivo**: Equilibrar portabilidad y rendimiento
- **Solución**: **Knee point** (peso ~300-400g)
- **Trade-off aceptado**: No óptimo en ningún extremo
- **Beneficio**: Versatilidad operacional, buena relación peso/ganancia

---

## Conclusión

El frente de Pareto visualiza explícitamente que **no existe una solución universalmente óptima**. Cada aplicación requiere priorizar diferentes objetivos según sus requisitos operacionales.

La herramienta SOGA permite explorar todas las opciones y tomar decisiones informadas basadas en trade-offs cuantificados.
