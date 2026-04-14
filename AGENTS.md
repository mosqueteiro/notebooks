# Agent Guidelines

## Overview

This is a Python project using:
- **Python 3.14+** (see `.python-version`)
- **uv** for package management
- **marimo** for notebook development
- **Nix** flake for reproducible devshell (see `flake.nix`)

## Development Environment

### Setup
```bash
# Option 1: Use Nix devshell (recommended)
nix develop

# Option 2: Use uv venv
uv sync
source .venv/bin/activate
```

### Running the Project
```bash
python main.py
marimo run main.py   # if using marimo
marimo edit          # open notebook editor
```

## Build/Lint/Test Commands

**Note**: No formal test suite or linting tools currently configured. Add to `pyproject.toml` as needed.

### If you add testing with pytest:
```bash
uv add --dev pytest
pytest                      # run all tests
pytest tests/               # run specific directory
pytest tests/test_file.py   # run single test file
pytest -k "test_name"       # run tests matching pattern
pytest --cov=src            # with coverage
```

### If you add linting with ruff:
```bash
uv add --dev ruff
ruff check .                # lint all files
ruff check path/to/file.py   # lint single file
ruff format .               # format code
```

### If you add type checking with mypy:
```bash
uv add --dev mypy
mypy .                      # type check
mypy path/to/file.py        # type check single file
```

## Code Style Guidelines

### General Principles
- Keep code simple and readable
- Write for humans first, machines second
- Be consistent with existing style in the file
- Use descriptive names over clever one-liners

### Imports
```python
# Standard library first
import os
import sys
from pathlib import Path

# Third-party
import marimo as mo

# Local project (if applicable)
# from . import module
```

### Formatting
- Use **4 spaces** for indentation (no tabs)
- Maximum line length: **100 characters**
- Use blank lines to separate logical sections
- No trailing whitespace

### Types
- Use type hints for function arguments and return values
- Prefer explicit types over `Any`
```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

### Naming Conventions
- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- Descriptive names: `calculate_total` not `calc`

### Error Handling
- Use exceptions for unexpected errors
- Catch specific exceptions, not bare `except:`
- Include context in error messages
```python
try:
    result = load_data(path)
except FileNotFoundError as e:
    raise ValueError(f"Data file not found: {path}") from e
```

### Docstrings
- Use Google or NumPy style for multi-line docs
- Keep brief: summarize "what" not "how"
```python
def process(data: list[int]) -> int:
    """Sum all values in the list.
    
    Args:
        data: List of integers to sum.
    
    Returns:
        Sum of all values.
    """
    return sum(data)
```

## Marimo Notebooks

- Notebook files use `.py` extension with marimo framework
- Edit with `marimo edit`
- Run with `marimo run <filename>`

## Project Structure

```
notebooks/
├── AGENTS.md           # This file
├── flake.nix           # Nix devshell definition
├── pyproject.toml     # Project config
├── uv.lock            # Locked dependencies
├── main.py            # Entry point
└── .venv/             # Virtual environment (gitignored)
```

## Dependencies

Add dependencies via:
```bash
uv add <package>          # runtime
uv add --dev <package>    # dev dependency
```

## Git

- Commit messages: clear, concise, imperative ("Add feature" not "Added")
- Push new dependencies after updating `pyproject.toml` and `uv.lock`
