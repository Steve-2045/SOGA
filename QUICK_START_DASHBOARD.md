# SOGA Dashboard - Quick Start Guide

This guide will help you get the SOGA interactive dashboard running in less than 5 minutes.

## Prerequisites

- Python 3.11 or higher
- SOGA backend installed (if not, see [Installation](#backend-installation))

## Step 1: Install Dashboard Dependencies

From the SOGA project root:

```bash
cd /home/tybur/Documents/SOGA
pip install streamlit plotly pandas
```

Or use the requirements file:

```bash
pip install -r streamlit_app/requirements.txt
```

## Step 2: Launch the Dashboard

### Option A: Using the Launcher Script (Easiest)

```bash
python run_dashboard.py
```

### Option B: Using Streamlit Directly

```bash
export PYTHONPATH=$PWD:$PYTHONPATH
streamlit run streamlit_app/SOGA_Dashboard.py
```

### Option C: Using Bash Script

Create and run `run_dashboard.sh`:

```bash
#!/bin/bash
cd /home/tybur/Documents/SOGA
export PYTHONPATH=$PWD:$PYTHONPATH
streamlit run streamlit_app/SOGA_Dashboard.py
```

Make it executable and run:

```bash
chmod +x run_dashboard.sh
./run_dashboard.sh
```

## Step 3: Access the Dashboard

Once Streamlit starts, you'll see output like:

```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.X:8501
```

Open your web browser and navigate to: **http://localhost:8501**

## Using the Dashboard

### First-Time Users: Run Your First Optimization

1. **Navigate to "🚀 Nueva Optimización"** (use the sidebar on the left)

2. **Configure Parameters** (or use defaults):
   - Rango de Diámetro: 0.1m - 2.0m
   - Rango de Relación f/D: 0.3 - 0.8
   - Peso Máximo: 1000g
   - Alcance Deseado: 5 km

3. **Click "🛰️ Ejecutar Optimización"**

4. **Wait 5-30 seconds** for the optimization to complete

5. **View Results**:
   - KPI metrics at the top
   - Convergence plot in the first tab
   - Detailed geometry in the second tab
   - Download options in the third tab

6. **Save Your Session** (optional):
   - Go to the "💾 Guardar y Exportar" tab
   - Click "Descargar Sesión (.json)"
   - Save the file for later comparison

### Comparing Multiple Runs

1. **Run multiple optimizations** with different parameters and save each as JSON

2. **Navigate to "📚 Análisis de Sesiones"**

3. **Upload your saved JSON files** using the sidebar file uploader

4. **Select sessions to compare** from the multiselect dropdown

5. **Analyze**:
   - View comparative metrics table
   - Explore overlaid convergence plots
   - Export comparison data to CSV

### Learning More

Navigate to **"ℹ️ Acerca del Proyecto"** to:
- Read the project description
- Understand the system architecture
- Learn about the scientific fundamentals
- View the complete README

## Troubleshooting

### "ModuleNotFoundError: No module named 'soga'"

**Solution**: Install the SOGA backend:

```bash
cd /home/tybur/Documents/SOGA
pip install -e .
```

Or set PYTHONPATH:

```bash
export PYTHONPATH=/home/tybur/Documents/SOGA:$PYTHONPATH
```

### "ModuleNotFoundError: No module named 'streamlit'"

**Solution**: Install Streamlit:

```bash
pip install streamlit plotly pandas
```

### Port 8501 Already in Use

**Solution**: Use a different port:

```bash
streamlit run streamlit_app/SOGA_Dashboard.py --server.port=8502
```

Then access at: http://localhost:8502

### Optimization is Very Slow

**Solution**: Reduce optimization parameters in `config.toml`:

```toml
[optimization]
population_size = 20    # Reduced from 40
max_generations = 40    # Reduced from 80
```

### Theme Not Applying

**Solution**: Clear cache and restart:

```bash
streamlit cache clear
# Then restart the dashboard
```

## Backend Installation

If you haven't installed the SOGA backend yet:

```bash
# Clone the repository (if not already done)
cd /home/tybur/Documents/SOGA

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate on Windows

# Install in development mode
pip install -e .

# Verify installation
python -m pytest tests/ -q
```

## Next Steps

After successfully running the dashboard:

1. **Experiment** with different parameter ranges to understand sensitivity
2. **Save multiple sessions** and compare them
3. **Export data** to CSV for analysis in other tools (Excel, Python, MATLAB)
4. **Read the documentation** in the "Acerca del Proyecto" page
5. **Explore the code** in `streamlit_app/` to customize or extend

## Getting Help

- **Dashboard Documentation**: See [streamlit_app/README.md](streamlit_app/README.md)
- **SOGA Documentation**: See [docs/](docs/) directory
- **GitHub Issues**: Report bugs or request features
- **Example Scripts**: Check [examples/](examples/) directory

## Performance Tips

- **First run**: The first optimization may take longer (~30 seconds) due to JIT compilation
- **Subsequent runs**: Should complete in 5-15 seconds
- **Large optimizations**: Increase `population_size` and `max_generations` in `config.toml`
- **Quick tests**: Decrease these values for faster iteration during experimentation

## Configuration Files

Key configuration files:

- **Backend Config**: `config.toml` - SOGA optimization parameters
- **UI Theme**: `streamlit_app/.streamlit/config.toml` - Dashboard appearance
- **Dependencies**: `streamlit_app/requirements.txt` - Dashboard dependencies

## Example Session Workflow

Complete workflow example:

```bash
# 1. Start dashboard
python run_dashboard.py

# 2. In browser (http://localhost:8501):
#    - Go to "Nueva Optimización"
#    - Set: Diameter 0.5-1.5m, Payload 800g
#    - Click "Ejecutar Optimización"
#    - Download as "design_800g.json"

# 3. Change payload to 1200g, run again
#    - Download as "design_1200g.json"

# 4. Go to "Análisis de Sesiones"
#    - Upload both JSON files
#    - Compare results
#    - Export comparison CSV

# 5. Analyze CSV externally:
import pandas as pd
df = pd.read_csv("soga_session_comparison.csv")
print(df)
```

---

**You're ready to optimize antennas! 🚀**

For questions or issues, consult the full documentation or open a GitHub issue.
