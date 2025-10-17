# ✅ Dashboard SOGA Instalado Exitosamente

El dashboard interactivo de SOGA ha sido instalado y configurado correctamente.

## 📦 Dependencias Instaladas

Las siguientes dependencias han sido instaladas en tu entorno virtual `./venv`:

- ✅ **Streamlit 1.50.0** - Framework de dashboard
- ✅ **Plotly 6.3.1** - Gráficos interactivos
- ✅ **Pandas 2.3.3** - Manipulación de datos

## 🚀 Cómo Ejecutar el Dashboard

Tienes **3 opciones** para ejecutar el dashboard:

### Opción 1: Script Bash (Recomendado) ⭐

```bash
./run_dashboard.sh
```

Este script:
- Detecta automáticamente el entorno virtual
- Configura el PYTHONPATH correctamente
- Muestra mensajes informativos
- Es la forma más simple de ejecutar

### Opción 2: Script Python

```bash
./venv/bin/python run_dashboard.py
```

O simplemente:

```bash
python run_dashboard.py
```

### Opción 3: Streamlit Directo

```bash
export PYTHONPATH=$PWD:$PYTHONPATH
./venv/bin/streamlit run streamlit_app/SOGA_Dashboard.py
```

## 🌐 Acceso al Dashboard

Una vez ejecutado cualquiera de los comandos anteriores, abre tu navegador en:

```
http://localhost:8501
```

## 📚 Estructura del Dashboard

El dashboard tiene **4 páginas principales**:

### 🏠 Página Principal (Home)
- Introducción al proyecto SOGA
- Guía de navegación
- Estadísticas del proyecto

### 🚀 Nueva Optimización
- Configurar parámetros de diseño con sliders interactivos
- Ejecutar optimización NSGA-II
- Visualizar resultados en tiempo real
- **Gráfico 2D de geometría parabólica** con dimensiones anotadas
- Descargar sesiones y exportar datos

### 📚 Análisis de Sesiones
- Cargar múltiples archivos de sesión (.json)
- Comparar resultados entre ejecuciones
- Gráficos comparativos de convergencia
- Exportar comparativas a CSV

### ℹ️ Acerca del Proyecto
- Descripción general del proyecto
- Arquitectura del sistema
- Fundamentos científicos (ecuaciones de Balanis, Kraus, IEEE)
- README completo

## 🎨 Características del Dashboard

### Tema Profesional Oscuro
- Fondo oscuro para reducir fatiga visual
- Colores morados/azules profesionales
- Optimizado para visualización de datos científicos

### Visualizaciones Interactivas
- Gráficos Plotly con zoom y pan
- Información al pasar el ratón
- Diseño responsivo

### Gestión de Sesiones
- Guardar configuraciones y resultados en JSON
- Cargar y comparar múltiples sesiones
- Exportar datos a CSV para análisis externo

## 📝 Flujo de Trabajo Típico

1. **Ejecutar el dashboard**
   ```bash
   ./run_dashboard.sh
   ```

2. **Ir a "🚀 Nueva Optimización"**
   - Ajustar parámetros (diámetro, f/D, peso, alcance)
   - Hacer clic en "Ejecutar Optimización"
   - Esperar 5-30 segundos

3. **Analizar resultados**
   - Ver métricas clave (ganancia, diámetro, f/D, beamwidth)
   - Explorar gráfico de convergencia
   - **Visualizar geometría parabólica en 2D** con dimensiones anotadas
   - Revisar geometría detallada en tablas

4. **Guardar sesión**
   - Ir a pestaña "Guardar y Exportar"
   - Descargar archivo JSON
   - Descargar CSV de convergencia (opcional)

5. **Comparar sesiones** (opcional)
   - Ir a "📚 Análisis de Sesiones"
   - Cargar múltiples archivos JSON
   - Comparar métricas y convergencia

## 🛠️ Configuración

### Tema del Dashboard
El tema se configura en:
```
streamlit_app/.streamlit/config.toml
```

### Parámetros de Optimización
Los parámetros del backend se configuran en:
```
config.toml
```

## 📖 Documentación Completa

- **Dashboard**: [streamlit_app/README.md](streamlit_app/README.md)
- **Inicio Rápido**: [QUICK_START_DASHBOARD.md](QUICK_START_DASHBOARD.md)
- **Proyecto SOGA**: [README.md](README.md)

## 🔧 Solución de Problemas

### El dashboard no inicia

**Verifica que Streamlit esté instalado:**
```bash
./venv/bin/pip list | grep streamlit
```

**Si no está instalado:**
```bash
./venv/bin/pip install -r streamlit_app/requirements.txt
```

### Error "ModuleNotFoundError: No module named 'soga'"

**Verifica que el backend esté instalado:**
```bash
./venv/bin/pip install -e .
```

### Puerto 8501 ya en uso

**Usa un puerto diferente:**
```bash
./venv/bin/streamlit run streamlit_app/SOGA_Dashboard.py --server.port=8502
```

Luego accede en: http://localhost:8502

### La optimización es muy lenta

**Edita `config.toml` para reducir parámetros:**
```toml
[optimization]
population_size = 20    # Reducido de 40
max_generations = 40    # Reducido de 80
```

## 📊 Ejemplo de Uso

### Análisis de Sensibilidad al Peso

```bash
# 1. Ejecutar dashboard
./run_dashboard.sh

# 2. En el navegador:
#    - Ir a "Nueva Optimización"
#    - Configurar: Peso = 500g → Ejecutar → Guardar como "peso_500g.json"
#    - Configurar: Peso = 1000g → Ejecutar → Guardar como "peso_1000g.json"
#    - Configurar: Peso = 1500g → Ejecutar → Guardar como "peso_1500g.json"

# 3. Ir a "Análisis de Sesiones"
#    - Cargar los 3 archivos JSON
#    - Comparar cómo el peso afecta la ganancia óptima
#    - Exportar comparativa a CSV
```

## 🎯 Próximos Pasos

1. **Experimenta con diferentes parámetros** para entender la sensibilidad del diseño
2. **Guarda múltiples sesiones** para comparación
3. **Exporta datos** para análisis en Excel, Python o MATLAB
4. **Lee la documentación científica** en "Acerca del Proyecto"
5. **Personaliza el tema** editando `.streamlit/config.toml`

## 📞 Soporte

- **Documentación**: Ver carpeta `docs/`
- **Ejemplos**: Ver carpeta `examples/`
- **GitHub**: Reportar issues o sugerencias

---

## ✨ Resumen de Archivos Creados

```
streamlit_app/
├── .streamlit/config.toml           # Configuración de tema
├── pages/
│   ├── 1_🚀_Nueva_Optimización.py   # Página de optimización
│   ├── 2_📚_Análisis_de_Sesiones.py # Página de comparación
│   └── 3_ℹ️_Acerca_del_Proyecto.py  # Página de documentación
├── SOGA_Dashboard.py                # Página principal (Home)
├── README.md                        # Documentación del dashboard
└── requirements.txt                 # Dependencias

run_dashboard.py                     # Launcher Python
run_dashboard.sh                     # Launcher Bash
QUICK_START_DASHBOARD.md             # Guía rápida
DASHBOARD_INSTALADO.md               # Este archivo
```

---

**¡Todo listo para optimizar antenas! 🎉**

El dashboard está completamente funcional y listo para usar.
