# SOGA Dashboard - Streamlit Application

Professional interactive dashboard for the Software de Optimización Geométrica de Antenas (SOGA).

## Overview

This multi-page Streamlit application provides a complete user interface for:

- Configuring and running antenna optimization simulations
- Visualizing optimization results with interactive Plotly charts
- Comparing multiple optimization sessions
- Exporting data for further analysis
- Accessing project documentation and scientific background

## Features

- **Professional Dark Theme**: Custom dark color scheme optimized for data visualization
- **Interactive Visualizations**: Plotly charts with hover information and zoom capabilities
- **Multi-Page Architecture**: Organized navigation with dedicated pages for different tasks
- **Session Management**: Save and load optimization sessions in JSON format
- **Data Export**: Export convergence history and comparison data to CSV
- **Responsive Design**: Wide layout optimized for large displays

## Installation

### 1. Install Dashboard Dependencies

From the project root:

```bash
pip install -r streamlit_app/requirements.txt
```

Or install individually:

```bash
pip install streamlit>=1.28.0 plotly>=5.18.0 pandas>=2.1.0
```

### 2. Verify SOGA Backend Installation

Ensure the SOGA backend is installed:

```bash
pip install -e .
```

## Running the Dashboard

### Method 1: From Project Root (Recommended)

```bash
cd /home/tybur/Documents/SOGA
export PYTHONPATH=$PWD:$PYTHONPATH
streamlit run streamlit_app/SOGA_Dashboard.py
```

### Method 2: Using a Launch Script

Create a file `run_dashboard.sh`:

```bash
#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH=$PWD:$PYTHONPATH
streamlit run streamlit_app/SOGA_Dashboard.py
```

Then run:

```bash
chmod +x run_dashboard.sh
./run_dashboard.sh
```

### Method 3: Python Script

Create a file `run_dashboard.py`:

```python
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Run Streamlit
import streamlit.web.cli as stcli

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        str(project_root / "streamlit_app" / "SOGA_Dashboard.py"),
        "--server.port=8501",
        "--server.address=localhost",
    ]
    sys.exit(stcli.main())
```

Then run:

```bash
python run_dashboard.py
```

## Application Structure

```
streamlit_app/
├── .streamlit/
│   └── config.toml              # Streamlit theme configuration
├── pages/
│   ├── 1_🚀_Nueva_Optimización.py    # Main optimization page
│   ├── 2_📚_Análisis_de_Sesiones.py  # Session comparison page
│   └── 3_ℹ️_Acerca_del_Proyecto.py   # Documentation page
├── SOGA_Dashboard.py            # Main entry point (Home page)
├── requirements.txt             # Dashboard dependencies
└── README.md                    # This file
```

## Pages Description

### Home Page (SOGA_Dashboard.py)

The landing page that provides:
- Project overview and introduction
- Quick start instructions
- Navigation guidance
- Key project statistics

### 🚀 Nueva Optimización

The main optimization page where users can:
- Configure optimization parameters using interactive sliders
- Execute NSGA-II optimization
- View real-time optimization results
- Explore convergence plots and performance metrics
- Save sessions and export data

**Key Features:**
- Form-based parameter input with validation
- Real-time feedback with spinners and status messages
- Tabbed results view (Convergence, Geometry, Export)
- KPI metrics display
- JSON session download
- CSV convergence export

### 📚 Análisis de Sesiones

Session comparison and analysis page where users can:
- Upload multiple JSON session files
- Select sessions for comparison
- View comparative metrics table
- Analyze overlaid convergence plots
- Export comparison data to CSV

**Key Features:**
- Multi-file upload
- Interactive session selection
- Statistical aggregation
- Best session identification
- Comparative visualization

### ℹ️ Acerca del Proyecto

Documentation and information page with:
- Project description and context
- System architecture overview
- Scientific fundamentals and equations
- Complete README content

**Key Features:**
- Tabbed organization
- Architecture diagrams
- Mathematical equations (LaTeX rendering)
- Expandable sections for detailed information

## Theme Customization

The dashboard uses a custom dark theme defined in [.streamlit/config.toml](.streamlit/config.toml):

```toml
[theme]
base = "dark"
primaryColor = "#667eea"              # Purple/blue for primary actions
backgroundColor = "#0f1419"            # Deep dark background
secondaryBackgroundColor = "#1a1f2e"   # Lighter for panels
textColor = "#e2e8f0"                  # Light gray for readability
font = "sans serif"
```

To modify the theme, edit this file and restart the Streamlit server.

## Usage Workflow

### Typical Workflow

1. **Navigate to Nueva Optimización**
   - Adjust parameter sliders to define design constraints
   - Click "Ejecutar Optimización"
   - Wait for NSGA-II to complete (~5-30 seconds)

2. **Analyze Results**
   - Review KPI metrics (gain, diameter, f/D ratio, beamwidth)
   - Explore convergence plot to verify optimization quality
   - Check detailed geometry specifications

3. **Save Session**
   - Download session JSON for later comparison
   - Export convergence CSV for external analysis

4. **Compare Sessions** (Optional)
   - Navigate to Análisis de Sesiones
   - Upload multiple session JSON files
   - Select sessions to compare
   - Analyze comparative metrics and convergence

5. **Learn More** (Optional)
   - Visit Acerca del Proyecto
   - Review scientific fundamentals
   - Understand system architecture

### Example: Sensitivity Analysis

To perform a sensitivity analysis:

1. Run optimization with baseline parameters → Save as `baseline.json`
2. Vary max payload from 500g to 1500g in 250g increments
3. Save each run as `payload_500g.json`, `payload_750g.json`, etc.
4. Upload all sessions to Análisis de Sesiones
5. Compare how payload constraint affects optimal gain and geometry

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'soga'`:

```bash
# Make sure you're in the project root
cd /home/tybur/Documents/SOGA

# Set PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH

# Install SOGA in development mode
pip install -e .
```

### Port Already in Use

If port 8501 is already in use:

```bash
streamlit run streamlit_app/SOGA_Dashboard.py --server.port=8502
```

### Configuration Not Loading

If the theme doesn't apply:

1. Check that `.streamlit/config.toml` exists
2. Clear Streamlit cache:
   ```bash
   streamlit cache clear
   ```
3. Restart the Streamlit server

### Slow Optimization

If optimization is taking too long (>1 minute):

1. Check `config.toml` parameters:
   - Reduce `population_size` (e.g., from 40 to 20)
   - Reduce `max_generations` (e.g., from 80 to 40)

2. Ensure you're not running in debug mode

## Development

### Adding a New Page

1. Create a new file in `pages/` with naming format:
   ```
   N_emoji_PageName.py
   ```
   Where N is the page number (determines order in sidebar)

2. Follow the existing page template:
   ```python
   import sys
   from pathlib import Path
   import streamlit as st

   # Setup path
   project_root = Path(__file__).parent.parent.parent
   sys.path.insert(0, str(project_root))

   # Page config
   st.set_page_config(
       page_title="Page Title - SOGA",
       page_icon="📊",
       layout="wide",
   )

   def main():
       st.title("Page Title")
       # Your content here

   if __name__ == "__main__":
       main()
   ```

3. Restart Streamlit to see the new page

### Modifying Visualizations

All Plotly charts use a consistent theme matching the Streamlit dark theme.

Template for new charts:

```python
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Scatter(...))

fig.update_layout(
    title={
        "text": "Chart Title",
        "x": 0.5,
        "xanchor": "center",
        "font": {"size": 20, "color": "#e2e8f0"},
    },
    xaxis={"title": "X Axis", "gridcolor": "#2d3748", "color": "#e2e8f0"},
    yaxis={"title": "Y Axis", "gridcolor": "#2d3748", "color": "#e2e8f0"},
    plot_bgcolor="#1a1f2e",
    paper_bgcolor="#1a1f2e",
    font={"color": "#e2e8f0"},
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)
```

## Performance Considerations

- **Session State**: Results are stored in `st.session_state` to avoid re-computation
- **Configuration Caching**: Config is loaded once and cached
- **File Processing**: Large files are processed in-memory without temporary files where possible

## Security Notes

- The dashboard runs locally by default
- No external API calls or data transmission
- Session files are stored locally
- Safe to use with sensitive antenna designs

## Future Enhancements

Potential improvements for future versions:

- [ ] Real-time optimization visualization (generation-by-generation)
- [ ] 3D antenna geometry rendering
- [ ] Radiation pattern visualization
- [ ] Multi-objective Pareto front exploration
- [ ] Automated report generation (PDF)
- [ ] Integration with CAD export (STL, STEP)
- [ ] Cloud deployment option
- [ ] User authentication for shared deployments

## Support

For issues, questions, or contributions:

- **GitHub**: https://github.com/tu-repo/soga
- **Documentation**: See `docs/` directory in project root
- **Email**: soporte@soga.dev

## License

This dashboard is part of the SOGA project and follows the same license (MIT).

---

**Built with Streamlit, Plotly, and Python**
