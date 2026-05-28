# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "altair==6.1.0",
#     "marimo>=0.23.8",
#     "pandas==3.0.3",
#     "polars==1.41.1",
#     "vega-datasets==0.9.0",
# ]
# ///

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def header(mo):
    mo.md("""
    # Gapminder Explorer
    Fertility vs Life Expectancy over time — inspired by Hans Rosling.
    """)
    return


@app.cell
def _():
    import marimo as mo
    import altair as alt
    import polars as pl
    from vega_datasets import data

    return alt, data, mo


@app.cell
def _(data):
    # Load and prepare gapminder data

    _gap_raw = data.gapminder()

    cluster_map = {
        0: "South Asia",
        1: "Europe & Central Asia",
        2: "Sub-Saharan Africa",
        3: "Americas",
        4: "Middle East & North Africa",
        5: "East Asia & Pacific",
    }

    df = _gap_raw.assign(
        continent=lambda d: d["cluster"].map(cluster_map)
    )

    years = sorted(df["year"].unique().tolist())
    continents = sorted(df["continent"].unique().tolist())
    return continents, df, years


@app.cell(hide_code=True)
def controls(continents, mo, years):
    year_slider = mo.ui.slider(steps=years, value=2000, label="Year")
    continent_picker = mo.ui.multiselect(continents, value=continents, label="Continents")

    controls = mo.hstack([
        year_slider,
        continent_picker
    ], justify="space-around", gap=1)

    controls
    return (year_slider,)


@app.cell(hide_code=True)
def scatter_plot(alt, df, year_slider):
    # Filter data
    filtered = df.query("year == @year_slider.value and continent.isin(@continent_picker.value)")

    # Scatter plot: fertility vs life expectancy
    scatter = (
        alt.Chart(filtered)
        .mark_circle(opacity=0.7)
        .encode(
            x=alt.X("fertility:Q", title="Fertility (births per woman)"),
            y=alt.Y("life_expect:Q", title="Life Expectancy (years)"),
            size=alt.Size("pop:Q", title="Population", scale=alt.Scale(range=[50, 1000])),
            color=alt.Color("continent:N", title="Continent"),
            tooltip=["country:N", "continent:N", "fertility:Q", "life_expect:Q", "pop:Q"],
        )
        .properties(width=700, height=450, title=f"Gapminder: {year_slider.value}")
        .interactive()
    )

    scatter
    return (filtered,)


@app.cell(hide_code=True)
def data_table(filtered):
    # Summary data table
    filtered.sort_values("pop", ascending=False)[["country", "continent", "fertility", "life_expect", "pop"]].head(10)
    return


if __name__ == "__main__":
    app.run()
