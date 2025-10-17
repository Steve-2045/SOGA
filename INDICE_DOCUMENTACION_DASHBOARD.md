# 📚 Índice de Documentación - Dashboard SOGA

Esta guía te ayudará a encontrar rápidamente la documentación que necesitas.

---

## 🚀 Inicio Rápido

### ¿Primera vez usando el dashboard?
👉 Lee: [QUICK_START_DASHBOARD.md](QUICK_START_DASHBOARD.md)
- Instalación en 3 pasos
- Primer uso del dashboard
- Ejemplo completo de workflow

### ¿Ya instalaste y quieres empezar?
👉 Lee: [DASHBOARD_INSTALADO.md](DASHBOARD_INSTALADO.md)
- Cómo ejecutar el dashboard
- Estructura de páginas
- Flujo de trabajo típico
- Solución de problemas

### ¿Quieres un resumen ejecutivo?
👉 Lee: [RESUMEN_DASHBOARD.md](RESUMEN_DASHBOARD.md)
- Visión general del dashboard
- Características principales
- Estado de implementación
- Casos de uso

---

## 📖 Documentación Técnica

### Dashboard (Interfaz Web)
📄 [streamlit_app/README.md](streamlit_app/README.md)
- Arquitectura del dashboard
- Descripción de cada página
- Customización del tema
- Desarrollo y extensión
- API de componentes

### Proyecto SOGA (Backend)
📄 [README.md](README.md)
- Descripción del proyecto completo
- Instalación del backend
- Uso programático
- Arquitectura del sistema
- Configuración

### Arquitectura del Sistema
📄 [docs/soga-architecture-guide.md](docs/soga-architecture-guide.md)
- Clean Architecture
- Capas y responsabilidades
- Diagramas de componentes
- Patrones de diseño

---

## 🎯 Por Caso de Uso

### "Quiero ejecutar mi primera optimización"
1. Lee: [QUICK_START_DASHBOARD.md](QUICK_START_DASHBOARD.md) - Sección "Paso 3"
2. Ejecuta: `./run_dashboard.sh`
3. Sigue las instrucciones en pantalla

### "Quiero comparar múltiples diseños"
1. Lee: [DASHBOARD_INSTALADO.md](DASHBOARD_INSTALADO.md) - Sección "Flujo de Trabajo"
2. Usa: Página "📚 Análisis de Sesiones"
3. Ver: [streamlit_app/README.md](streamlit_app/README.md) - Sección "Comparación"

### "Quiero entender cómo funciona el algoritmo"
1. Lee: [RESUMEN_DASHBOARD.md](RESUMEN_DASHBOARD.md) - Sección "Integración con Backend"
2. Visita: Dashboard → Página "ℹ️ Acerca del Proyecto" → Tab "Fundamentos Científicos"
3. Lee: [docs/REPORTE_AUDITORIA_FINAL.md](docs/REPORTE_AUDITORIA_FINAL.md)

### "Quiero personalizar el dashboard"
1. Lee: [streamlit_app/README.md](streamlit_app/README.md) - Sección "Theme Customization"
2. Edita: `streamlit_app/.streamlit/config.toml`
3. Ver: [streamlit_app/README.md](streamlit_app/README.md) - Sección "Development"

### "Tengo un problema/error"
1. Lee: [DASHBOARD_INSTALADO.md](DASHBOARD_INSTALADO.md) - Sección "Solución de Problemas"
2. Lee: [QUICK_START_DASHBOARD.md](QUICK_START_DASHBOARD.md) - Sección "Troubleshooting"
3. Revisa: Los logs en la terminal

---

## 📁 Documentación por Archivo

### Archivos de Inicio Rápido

| Archivo | Propósito | Cuándo leerlo |
|---------|-----------|---------------|
| [RESUMEN_DASHBOARD.md](RESUMEN_DASHBOARD.md) | Resumen ejecutivo | Visión general del proyecto |
| [QUICK_START_DASHBOARD.md](QUICK_START_DASHBOARD.md) | Guía de inicio rápido | Primera instalación |
| [DASHBOARD_INSTALADO.md](DASHBOARD_INSTALADO.md) | Manual de usuario | Uso diario del dashboard |
| Este archivo | Índice de documentación | Navegación de docs |

### Archivos Técnicos

| Archivo | Propósito | Cuándo leerlo |
|---------|-----------|---------------|
| [streamlit_app/README.md](streamlit_app/README.md) | Documentación del dashboard | Desarrollo o customización |
| [README.md](README.md) | Documentación de SOGA | Entender el backend |
| [streamlit_app/requirements.txt](streamlit_app/requirements.txt) | Dependencias | Instalación manual |

### Scripts de Ejecución

| Archivo | Tipo | Uso |
|---------|------|-----|
| [run_dashboard.sh](run_dashboard.sh) | Bash | `./run_dashboard.sh` (recomendado) |
| [run_dashboard.py](run_dashboard.py) | Python | `python run_dashboard.py` |

---

## 🔍 Documentación del Backend SOGA

### Esencial

| Archivo | Contenido |
|---------|-----------|
| [README.md](README.md) | README principal del proyecto |
| [config.toml](config.toml) | Configuración de parámetros |

### Detallada

| Archivo | Contenido |
|---------|-----------|
| [docs/soga-architecture-guide.md](docs/soga-architecture-guide.md) | Guía de arquitectura |
| [docs/REPORTE_AUDITORIA_FINAL.md](docs/REPORTE_AUDITORIA_FINAL.md) | Auditoría completa del sistema |

---

## 🎨 Archivos de Configuración

### Dashboard

| Archivo | Propósito |
|---------|-----------|
| [streamlit_app/.streamlit/config.toml](streamlit_app/.streamlit/config.toml) | Tema y configuración de Streamlit |
| [streamlit_app/requirements.txt](streamlit_app/requirements.txt) | Dependencias del dashboard |

### Backend

| Archivo | Propósito |
|---------|-----------|
| [config.toml](config.toml) | Parámetros de optimización |
| [pyproject.toml](pyproject.toml) | Configuración del proyecto Python |

---

## 🗺️ Mapa de Navegación Rápida

```
┌─────────────────────────────────────────────┐
│         ¿Qué necesitas hacer?               │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
    ¿Instalar?              ¿Usar?
        │                       │
        ↓                       ↓
QUICK_START_DASHBOARD    DASHBOARD_INSTALADO
        │                       │
        │                       ↓
        │               ¿Necesitas ayuda?
        │                       │
        ↓                       ↓
 ¿Entender                 Troubleshooting
  el código?                (en ambos docs)
        │
        ↓
streamlit_app/README
        +
docs/soga-architecture-guide
```

---

## 📝 Orden de Lectura Recomendado

### Para Usuarios (Uso del Dashboard)

1. **[RESUMEN_DASHBOARD.md](RESUMEN_DASHBOARD.md)** (5 min)
   - Visión general del proyecto

2. **[QUICK_START_DASHBOARD.md](QUICK_START_DASHBOARD.md)** (10 min)
   - Instalación y primer uso

3. **[DASHBOARD_INSTALADO.md](DASHBOARD_INSTALADO.md)** (15 min)
   - Uso completo y casos de uso

4. **Dashboard → "ℹ️ Acerca del Proyecto"** (en la app)
   - Fundamentos científicos

### Para Desarrolladores (Modificar/Extender)

1. **[README.md](README.md)** (15 min)
   - Contexto del proyecto SOGA

2. **[docs/soga-architecture-guide.md](docs/soga-architecture-guide.md)** (30 min)
   - Arquitectura del backend

3. **[streamlit_app/README.md](streamlit_app/README.md)** (20 min)
   - Arquitectura del dashboard

4. **Código fuente** (en `streamlit_app/`)
   - Implementación detallada

---

## 🔧 Recursos Adicionales

### Ejemplos de Código
📁 `examples/`
- Ejemplos de uso programático del backend

### Tests
📁 `tests/`
- Tests unitarios y de integración
- Ejemplos de validación

### Scripts de Auditoría
📁 `scripts/audit/`
- Scripts de validación científica
- Gráficos de análisis

---

## 🆘 ¿Necesitas Ayuda?

### Problema con Instalación
👉 [QUICK_START_DASHBOARD.md](QUICK_START_DASHBOARD.md) - Sección "Troubleshooting"

### Problema con Ejecución
👉 [DASHBOARD_INSTALADO.md](DASHBOARD_INSTALADO.md) - Sección "Solución de Problemas"

### Pregunta sobre Funcionalidad
👉 [streamlit_app/README.md](streamlit_app/README.md) - Sección correspondiente

### Pregunta sobre el Backend
👉 [README.md](README.md) o [docs/soga-architecture-guide.md](docs/soga-architecture-guide.md)

---

## 📊 Matriz de Documentación

| Necesito... | Archivo | Sección |
|-------------|---------|---------|
| Instalar | QUICK_START_DASHBOARD.md | Paso 1 |
| Ejecutar | DASHBOARD_INSTALADO.md | "Cómo Ejecutar" |
| Entender arquitectura | streamlit_app/README.md | "Structure" |
| Customizar tema | streamlit_app/README.md | "Theme Customization" |
| Comparar sesiones | DASHBOARD_INSTALADO.md | "Flujo de Trabajo" |
| Solucionar error | QUICK_START o INSTALADO | "Troubleshooting" |
| Ver ejemplos | examples/ | - |
| Entender ciencia | Dashboard en navegador | Página "Acerca" |

---

## 🎯 Resumen Ultra-Rápido

**Para empezar ahora mismo:**

```bash
# 1. Ir al proyecto
cd /home/tybur/Documents/SOGA

# 2. Ejecutar dashboard
./run_dashboard.sh

# 3. Abrir navegador
# http://localhost:8501

# 4. ¡Optimizar!
```

**Si tienes problemas:**
Lee [QUICK_START_DASHBOARD.md](QUICK_START_DASHBOARD.md)

**Si quieres aprender más:**
Lee [DASHBOARD_INSTALADO.md](DASHBOARD_INSTALADO.md)

---

## 📞 Contacto y Soporte

- **Documentación local**: Ver carpeta `docs/`
- **Ejemplos**: Ver carpeta `examples/`
- **Issues**: GitHub (si aplica)

---

**Última actualización:** 2025-10-16
**Versión del Dashboard:** 1.0
**Estado:** ✅ Completamente funcional
