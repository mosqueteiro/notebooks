# Notebooks

Repository for hosting notebooks.

This repository houses a collection of personal and shared [Marimo](https://marimo.io/) notebooks.

It is designed to provide a highly reproducible, frictionless developer experience on NixOS (and other Linux/macOS systems with Nix installed) by drawing a clear boundary between **system dependencies** (managed by Nix) and **Python dependencies** (managed by `uv`).

## Architecture

- **Nix (`flake.nix`)**: Handles the system-level bootstrap. It provides the Python interpreter, `uv`, and any underlying C libraries required to compile Python wheels (like `zlib` or `gcc`).
- **`direnv`**: Automatically loads the Nix environment and sets required environment variables upon entering the project directory.
- **`uv`**: Manages all Python packages and the virtual environment (`.venv`). It acts as the single source of truth for Python tooling (LSPs, linters, data science libraries).
- **Marimo**: The notebook interface, running either within the unified project environment or via self-contained, sandboxed PEP 723 scripts.

## Prerequisites

To run this repository smoothly, you need the following installed globally on your system:

1. **Nix** (with [Flakes enabled](https://nixos.wiki/wiki/Flakes))
2. **`direnv`** and **`nix-direnv`**
3. **Editor Integration**: Ensure your IDE (VS Code, Neovim, etc.) has a `direnv` plugin installed so your LSPs can pick up the local `.venv`.

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd notebooks
   ```

2. **Allow direnv:**
   ```bash
   direnv allow
   ```
   Note: If you modify or create `flake.nix` from scratch, you must track it with git (`git add flake.nix`) before Nix will evaluate it.

3. **Sync Python dependencies:**
   ```bash
   uv sync
   ```

## Workflow

### Running Notebooks

You have two ways to run notebooks depending on your goal:

#### A. The Unified Environment (Default)

For daily work where you want access to the project's shared dependencies and dev tools:

```bash
uv run marimo edit
```

Alternatively, open a specific notebook:

```bash
uv run marimo edit my_notebook.py
```

#### B. The Sandboxed Environment (For Sharing/Isolation)

If you are preparing a notebook to share, or need an isolated environment to prevent dependency conflicts, run it in sandbox mode. Marimo will use PEP 723 inline script metadata to manage dependencies strictly for that file.

```bash
uv run marimo edit my_notebook.py --sandbox
```

### Managing Python Dependencies (uv)

To add a package globally to the workspace (available to all non-sandboxed notebooks and your LSP):

```bash
uv add pandas
```

Note: Because of our Nix configuration, uv is configured via `UV_PYTHON_PREFERENCE="system"` to use the Nix-provided Python interpreter rather than downloading its own.

### Managing System Dependencies (Nix)

If `uv` fails to install a package because of a missing C library or system tool (e.g., `psycopg2` complaining about `libpq`, or needing `ffmpeg` for media manipulation):

1. Open `flake.nix`.
2. Add the required package (e.g., `pkgs.postgresql`) to the packages list.
3. Run `direnv reload`.
4. Retry your `uv add` command.

### Language Server (basedpyright)

This project includes [basedpyright](https://basedpyright.readthedocs.io/) for type checking. To use it:

1. In marimo UI: **Settings** > **Language Servers** > enable **basedpyright**
2. From CLI: `basedpyright <file.py>` to type-check manually

Configuration in `pyproject.toml` (e.g., `[tool.basedpyright]`) is not yet applied in marimo - configure via marimo's UI settings instead.

## Troubleshooting

- **NixOS Dynamic Linking**: Pre-compiled Python wheels sometimes struggle on NixOS because standard `/lib` paths don't exist. Our `flake.nix` mitigates this by utilizing the Nix-patched Python and manually exporting `LD_LIBRARY_PATH` for common dependencies like `zlib` and `stdenv.cc.cc.lib`.

- **Unrecognized Flake Changes**: Nix flakes ignore files not tracked by Git. If you add a new file that Nix needs to know about, be sure to `git add` it first.