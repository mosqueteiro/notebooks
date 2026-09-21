import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", app_title="OpenCode Data Notebook")

with app.setup:
    import marimo as mo


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # OpenCode Data Notebook
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    /// attention | Under Construction 🚧
    This notebook will contain data from OpenCode about model availablility, costs, and usage for OpenCode Zen and Go, and AI model usage data globally.
    ///

    - Zen model pricing
    - Go model pricing and estimated requests per X limit
    - My usage
    - AI model usage across all OpenCode users
    - Model comparisons by OpenCode
    - Model comparisons from [Artificial Analysis](https://artificialanalysis.ai/)
    """)
    return


if __name__ == "__main__":
    app.run()
