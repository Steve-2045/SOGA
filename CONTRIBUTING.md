# Contributing to SOGA

Thank you for your interest in contributing to SOGA (Software de Optimización Geométrica de Antenas)!

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/Proyecto_Dron.git`
3. Create a branch: `git checkout -b feature/your-feature-name`

## Development Setup

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements.txt
```

## Code Standards

### Style Guidelines

We follow PEP 8 and use automated tools to maintain code quality:

- **Black**: Code formatter (line length: 100)
- **Ruff**: Fast linter for Python

### Running Code Quality Checks

```bash
# Format code with black
black src/ tests/ examples/

# Lint with ruff
ruff check src/ tests/ examples/

# Fix auto-fixable issues
ruff check --fix src/ tests/ examples/
```

### Code Structure

SOGA follows a layered architecture:

```
src/soga/
├── core/            # Domain logic (physics, models, optimization)
├── app/             # Application layer (facade)
└── infrastructure/  # Infrastructure (config, file I/O)
```

**Key Principles:**

- Domain logic should not depend on infrastructure
- Use dependency injection
- Write pure functions when possible
- Document all public APIs with docstrings

### Documentation Standards

- Use Google-style docstrings
- Include type hints for all function signatures
- Add examples in docstrings for complex functions
- Keep comments concise and meaningful

Example:

```python
def calculate_gain(diameter_m: float, wavelength_m: float, efficiency: float) -> float:
    """
    Calculate antenna gain using the aperture formula.

    Args:
        diameter_m: Antenna diameter in meters
        wavelength_m: Wavelength in meters
        efficiency: Aperture efficiency (0-1)

    Returns:
        Antenna gain in dBi

    Examples:
        >>> calculate_gain(0.5, 0.125, 0.7)
        18.95
    """
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src/soga --cov-report=term-missing

# Run specific test file
pytest tests/core/test_physics.py -v

# Run specific test
pytest tests/core/test_physics.py::test_calculate_gain -v
```

### Test Standards

- Aim for >90% code coverage
- Write unit tests for all new functions
- Include edge cases and error conditions
- Use descriptive test names: `test_<function>_<scenario>_<expected_result>`

Example:

```python
def test_calculate_gain_with_zero_diameter_raises_error():
    """Test that zero diameter raises ValueError."""
    with pytest.raises(ValueError, match="diameter must be positive"):
        calculate_gain(diameter_m=0.0, wavelength_m=0.125, efficiency=0.7)
```

## Submitting Changes

### Pull Request Process

1. **Update tests**: Ensure all tests pass and add new tests for your changes
2. **Update documentation**: Update docstrings, README, or relevant docs
3. **Run quality checks**: Format code with black and run ruff
4. **Commit message**: Use clear, descriptive commit messages
5. **Create PR**: Submit a pull request with a detailed description

### Commit Message Format

```
<type>: <short summary>

<detailed description>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**

```
feat: add support for elliptical reflector geometries

Implemented elliptical reflector model in core/models.py.
Added physics calculations for elliptical apertures.
Includes comprehensive test coverage.

Closes #42
```

### Pull Request Checklist

- [ ] Tests pass: `pytest tests/ -v`
- [ ] Coverage maintained: `pytest --cov=src/soga`
- [ ] Code formatted: `black src/ tests/`
- [ ] No linting errors: `ruff check src/ tests/`
- [ ] Documentation updated
- [ ] Commit messages follow format
- [ ] Branch is up-to-date with main

## Reporting Issues

### Bug Reports

Include:

1. **Description**: Clear description of the bug
2. **Steps to reproduce**: Minimal code example
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: Python version, OS, SOGA version

**Template:**

```markdown
**Bug Description**
Brief description of the issue

**To Reproduce**
\`\`\`python
# Minimal code to reproduce
\`\`\`

**Expected Behavior**
What you expected to happen

**Actual Behavior**
What actually happened

**Environment**
- Python version: 3.11.5
- OS: Ubuntu 22.04
- SOGA version: 0.0.1
```

### Feature Requests

Include:

1. **Use case**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Alternatives**: Other approaches considered

## Code of Conduct

- Be respectful and constructive
- Focus on technical merit
- Welcome newcomers
- Help others learn

## Questions?

- Open an issue for questions
- Tag with `question` label
- Check existing issues first

---

Thank you for contributing to SOGA!
