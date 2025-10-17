# SOGA UI Components Guide

Quick reference guide for using the custom UI components in the SOGA dashboard.

## 📦 Import Components

```python
import sys
from pathlib import Path

# Add utils to path (for pages)
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import components
from utils.ui_components import (
    load_custom_css,
    gradient_header,
    info_card,
    metric_card,
    divider_with_text,
    badge,
    progress_bar_with_text,
    styled_plotly_chart,
    create_pareto_front_chart,
    create_convergence_chart,
    create_plotly_theme
)
```

## 🎨 Components

### 1. Load Custom CSS

**Always call this first on each page!**

```python
load_custom_css()
```

This loads the custom styling from `styles/custom.css`.

---

### 2. Gradient Header

Create headers with gradient text effects.

```python
gradient_header(
    text="My Page Title",
    level=1,          # H1-H6 (1-6)
    icon="🚀"         # Optional emoji
)
```

**Example Output:**
```
🚀 My Page Title  (with gradient effect)
```

**Use Cases:**
- Page titles (level=1)
- Section headers (level=2-3)
- Subsections (level=4-6)

---

### 3. Info Card

Create styled informational cards with color themes.

```python
info_card(
    title="Card Title",
    content="Your markdown content here...",
    icon="ℹ️",
    color="primary"   # primary, success, warning, info
)
```

**Available Colors:**
- `primary`: Purple gradient (default)
- `success`: Cyan gradient
- `warning`: Pink/yellow gradient
- `info`: Blue gradient

**Example:**
```python
info_card(
    title="Welcome",
    content="""
This is a **welcome message** with:
- Bullet points
- *Italic text*
- **Bold text**
    """,
    icon="👋",
    color="primary"
)
```

---

### 4. Divider with Text

Create styled section dividers.

```python
divider_with_text("SECTION NAME")
```

**Example Output:**
```
─────────── SECTION NAME ───────────
(with gradient lines)
```

**Best Practices:**
- Use UPPERCASE text
- Short labels (1-3 words)
- Between major sections

---

### 5. Metric Card

Create custom metric displays with gradients.

```python
metric_card(
    label="Metric Name",
    value="42.5",
    delta="+5.2",     # Optional
    icon="📊",
    help_text="Explanation"  # Optional
)
```

**Note:** For standard metrics, you can also use Streamlit's `st.metric()` which is automatically styled by the custom CSS.

---

### 6. Badge

Create small colored badges.

```python
badge(
    text="New Feature",
    color="success"   # primary, success, warning, info
)
```

**Use Cases:**
- Status indicators
- Tags and labels
- Version numbers

---

### 7. Progress Bar

Custom progress bars with gradient fills.

```python
progress_bar_with_text(
    progress=0.75,        # 0.0 to 1.0
    text="Processing..."  # Optional
)
```

**Example:**
```python
progress_bar_with_text(0.65, "Optimization: 65%")
```

---

### 8. Styled Plotly Chart

Apply custom dark theme to any Plotly chart.

```python
import plotly.graph_objects as go

fig = go.Figure(data=[
    go.Scatter(x=[1, 2, 3], y=[4, 5, 6])
])

styled_plotly_chart(fig)
```

**Features:**
- Automatic dark theme
- Custom color palette
- Enhanced hover tooltips
- Professional export options

---

### 9. Convergence Chart

Specialized chart for optimization convergence.

```python
history = [20.5, 23.1, 24.8, 25.2, 25.3]  # Gain values per generation

fig = create_convergence_chart(
    history=history,
    title="Optimization Progress"
)

styled_plotly_chart(fig)
```

**Features:**
- Gradient colors
- Area fill under curve
- Generation labels
- Custom hover template

---

### 10. Pareto Front Chart

Specialized chart for Pareto front visualization.

```python
data = {
    'weight': [0.5, 0.8, 1.2, 1.5],
    'gain': [20, 23, 25, 26]
}

fig = create_pareto_front_chart(
    data=data,
    title="Trade-off Space"
)

styled_plotly_chart(fig)
```

**Features:**
- Color-coded by gain
- Interactive hover
- Custom markers
- Professional styling

---

### 11. Create Plotly Theme

Get the theme configuration for manual application.

```python
theme = create_plotly_theme()

fig.update_layout(**theme)
```

**Use this when you need more control over the chart styling.**

---

## 📋 Complete Page Template

```python
"""
My Page
Description of the page.
"""

import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.ui_components import (
    load_custom_css,
    gradient_header,
    info_card,
    divider_with_text
)

# Load custom CSS
load_custom_css()

# Page header
gradient_header("My Page Title", level=1, icon="🎯")
st.markdown("Subtitle or description")

# First section
divider_with_text("GETTING STARTED")

info_card(
    title="Introduction",
    content="Welcome to this page...",
    icon="👋",
    color="primary"
)

# Main content
st.markdown("### Section Content")
# ... your content here ...

# Another section
divider_with_text("DETAILS")

col1, col2 = st.columns(2)

with col1:
    info_card(
        title="Feature 1",
        content="Description...",
        icon="✨",
        color="success"
    )

with col2:
    info_card(
        title="Feature 2",
        content="Description...",
        icon="🚀",
        color="info"
    )

# Metrics
st.markdown("### Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Label", "Value")

with col2:
    st.metric("Label", "Value")

with col3:
    st.metric("Label", "Value")
```

---

## 🎨 Color Palette Reference

### CSS Variables

Available in `custom.css`:

```css
--primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
--success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)
--warning-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%)
--info-gradient: linear-gradient(135deg, #4299e1 0%, #667eea 100%)

--bg-primary: #0f1419
--bg-secondary: #1a1f2e
--bg-tertiary: #242b3d

--text-primary: #e2e8f0
--text-secondary: #a0aec0
--text-tertiary: #718096

--border-color: #2d3748
--border-accent: #4a5568
```

### Color Usage

| Context | Variable | Use For |
|---------|----------|---------|
| Primary actions | `primary` | Main buttons, headers |
| Success states | `success` | Confirmations, positive feedback |
| Warnings | `warning` | Alerts, important notices |
| Information | `info` | Help text, tips |

---

## 💡 Best Practices

### Layout

```python
# ✅ Good: Clear hierarchy
gradient_header("Main Title", level=1, icon="🚀")
divider_with_text("SECTION")
st.markdown("### Subsection")

# ❌ Avoid: Skipping levels
gradient_header("Title", level=1)
st.markdown("##### Small header")  # Too small
```

### Cards

```python
# ✅ Good: Cards for grouped content
col1, col2 = st.columns(2)
with col1:
    info_card("Feature A", "Description...", icon="✨", color="success")
with col2:
    info_card("Feature B", "Description...", icon="🚀", color="info")

# ❌ Avoid: Too many cards in a row
col1, col2, col3, col4, col5 = st.columns(5)  # Too crowded
```

### Dividers

```python
# ✅ Good: Between major sections
divider_with_text("CONFIGURATION")
# ... configuration content ...
divider_with_text("RESULTS")
# ... results content ...

# ❌ Avoid: Too frequent
divider_with_text("PART 1")
st.write("One line")
divider_with_text("PART 2")  # Too soon
```

### Charts

```python
# ✅ Good: Use styled_plotly_chart
fig = go.Figure(...)
styled_plotly_chart(fig)

# ❌ Avoid: Plain st.plotly_chart (misses theme)
st.plotly_chart(fig)  # Won't have custom styling
```

---

## 🔍 Troubleshooting

### CSS Not Loading

```python
# Make sure this is called!
load_custom_css()
```

### Components Not Found

```python
# Check import path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Colors Not Showing

```python
# Use exact color names
color="primary"  # ✅ Correct
color="Primary"  # ❌ Won't work (case sensitive)
```

---

## 📚 Examples by Use Case

### Dashboard Home Page

```python
gradient_header("Dashboard", level=1, icon="📊")
divider_with_text("OVERVIEW")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Users", "1,234")
with col2:
    st.metric("Sessions", "5,678")
with col3:
    st.metric("Uptime", "99.9%")
```

### Configuration Page

```python
gradient_header("Configuration", level=1, icon="⚙️")
divider_with_text("SETTINGS")

with st.form("config_form"):
    st.slider("Parameter", 0, 100, 50)
    st.number_input("Value", value=10)
    st.form_submit_button("Save")
```

### Results Page

```python
gradient_header("Results", level=1, icon="📊")

info_card(
    title="Analysis Complete",
    content="Found optimal solution.",
    icon="✅",
    color="success"
)

divider_with_text("VISUALIZATION")

fig = create_convergence_chart(history, "Progress")
styled_plotly_chart(fig)
```

### About Page

```python
gradient_header("About", level=1, icon="ℹ️")
divider_with_text("INFORMATION")

col1, col2 = st.columns(2)
with col1:
    info_card("Feature 1", "Description", icon="✨", color="primary")
with col2:
    info_card("Feature 2", "Description", icon="🚀", color="success")
```

---

## 🎓 Additional Resources

- **Full Documentation**: See `docs/UI_ENHANCEMENTS.md`
- **CSS Reference**: `streamlit_app/styles/custom.css`
- **Component Source**: `streamlit_app/utils/ui_components.py`
- **Live Examples**: All page files in `streamlit_app/pages/`

---

**Last Updated**: October 15, 2025
**Version**: 1.0.0
