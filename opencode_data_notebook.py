import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", app_title="OpenCode Data Notebook")

with app.setup:
    import marimo as mo
    import polars as pl
    import requests
    import json
    import re
    from bs4 import BeautifulSoup
    import altair as alt


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

    - ~~Zen model pricing~~
    - ~~Go model pricing~~ and ~~estimated requests per X limit~~
    - My usage
    - AI model usage across all OpenCode users
    - Model comparisons by OpenCode
    - Model comparisons from [Artificial Analysis](https://artificialanalysis.ai/)
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    - [Opencode AI Model Usage Rankings](https://opencode.ai/data/)
    - [Opencode Model Pricing](https://opencode.ai/v2/docs/console/models/#pricing)
    - [Opencode Go Usage Limits](https://opencode.ai/v2/docs/console/go/#usage-limits)
    - [Opencode Console](https://opencode.ai/console/)
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## OpenCode Zen & Go pricing

    Pricing is sourced from two places, preferring the machine-readable API where possible:

    - **[models.dev](https://models.dev/)** catalog API (`catalog.json`) — a community-maintained, provider-agnostic database of model metadata and pricing. This is the primary structured source.
    - **OpenCode docs** — [`console/models`](https://opencode.ai/v2/docs/console/models/#pricing) for Zen and [`console/go`](https://opencode.ai/v2/docs/console/go/#usage-limits) for Go. These are scraped for the values OpenCode itself publishes (including \"Free\" tiers and Go's monthly spend limits, which models.dev does not expose).

    All prices are **USD per 1,000,000 tokens** unless noted otherwise.
    """)
    return


@app.cell(hide_code=True)
def _():
    def parse_html_tables(html_text):
        """Extract {headers, rows} from every <table> in an HTML document."""
        soup = BeautifulSoup(html_text, "html.parser")
        tables = []
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            body = table.find("tbody") or table
            rows = []
            for tr in body.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all("td")]
                if cells:
                    rows.append(cells)
            tables.append({"headers": headers, "rows": rows})
        return tables


    def parse_price(value):
        """Convert a price cell ('$0.30', 'Free', '-') into a float or None."""
        if value is None:
            return None
        v = str(value).strip().replace(",", "")
        if v.lower() in ("free", "$0", "$0.00", "$0.0"):
            return 0.0
        if v in ("", "-", "\u2014", "N/A"):
            return None
        match = re.search(r"-?\d+(?:\.\d+)?", v)
        return float(match.group()) if match else None


    def parse_count(value):
        """Convert a request-count cell ('6,320', 'Unlimited', '-') into an int or None."""
        if value is None:
            return None
        v = str(value).strip().replace(",", "")
        if v.lower() in ("unlimited", "", "-", "\u2014", "N/A"):
            return None
        match = re.search(r"\d+", v)
        return int(match.group()) if match else None


    def fetch_html(url):
        """GET a URL and return its decoded HTML (forced to UTF-8)."""
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        return resp.text

    return fetch_html, parse_count, parse_html_tables, parse_price


@app.cell(hide_code=True)
def _(fetch_html, parse_html_tables):
    OPENCODE_MODELS_URL = "https://opencode.ai/v2/docs/console/models/"
    OPENCODE_GO_URL = "https://opencode.ai/v2/docs/console/go/"

    zen_docs_tables = parse_html_tables(fetch_html(OPENCODE_MODELS_URL))
    go_docs_tables = parse_html_tables(fetch_html(OPENCODE_GO_URL))

    zen_pricing_table = next(
        t for t in zen_docs_tables
        if t["headers"] == ["Model", "Input", "Output", "Cached Read", "Cached Write"]
    )
    go_pricing_table = next(t for t in go_docs_tables if "Monthly limit" in t["headers"])
    go_estimated_requests_table = next(
        t for t in go_docs_tables if "requests per 5 hour" in t["headers"]
    )
    go_endpoints_table = next(t for t in go_docs_tables if "Endpoint" in t["headers"])
    go_privacy_table = next(t for t in go_docs_tables if "Data retention" in t["headers"])

    mo.md(f"Parsed {len(zen_docs_tables)} Zen and {len(go_docs_tables)} Go docs tables.")
    return (
        go_endpoints_table,
        go_estimated_requests_table,
        go_pricing_table,
        go_privacy_table,
        zen_pricing_table,
    )


@app.cell(hide_code=True)
def _(
    go_endpoints_table,
    go_estimated_requests_table,
    go_pricing_table,
    go_privacy_table,
    parse_count,
    parse_price,
    zen_pricing_table,
):
    PRICE_HEADERS = ["Input", "Output", "Cached Read", "Cached Write", "Monthly limit"]
    PRICE_RENAMES = {
        "Input": "input", "Input usd": "input_usd",
        "Output": "output", "Output usd": "output_usd",
        "Cached Read": "cached_read", "Cached Read usd": "cached_read_usd",
        "Cached Write": "cached_write", "Cached Write usd": "cached_write_usd",
        "Monthly limit": "monthly_limit", "Monthly limit usd": "monthly_limit_usd",
    }
    MODEL_COL = "model"


    def build_pricing_df(table):
        """Turn a parsed OpenCode pricing table into a typed polars DataFrame."""
        headers = table["headers"]
        price_fields = [h for h in headers if h in PRICE_HEADERS]
        records = []
        for row in table["rows"]:
            record = {MODEL_COL: row[0]}
            for header in price_fields:
                cell = row[headers.index(header)]
                record[header] = cell
                record[f"{header} usd"] = parse_price(cell)
            records.append(record)
        df = pl.DataFrame(records)
        renames = {k: v for k, v in PRICE_RENAMES.items() if k in df.columns}
        return df.rename(renames).with_columns(
            ((pl.col("input_usd") == 0) & (pl.col("output_usd") == 0)).fill_null(False).alias("free")
        )


    def build_estimated_requests_df(table):
        """Turn the Go 'estimated requests' table into a typed polars DataFrame."""
        headers = table["headers"]
        records = []
        for row in table["rows"]:
            record = {MODEL_COL: row[0], "unlimited": True}
            for header, cell in zip(headers[1:], row[1:]):
                value = parse_count(cell)
                record[header] = value
                if value is not None:
                    record["unlimited"] = False
            records.append(record)
        return pl.DataFrame(records).rename({
            "requests per 5 hour": "per_5h",
            "requests per week": "per_week",
            "requests per month": "per_month",
        })


    def build_model_info_df(table, rename):
        """Turn a plain Model + attribute table into a DataFrame with snake_case columns."""
        headers = [rename.get(h, h) for h in table["headers"]]
        headers[0] = MODEL_COL
        return pl.DataFrame(table["rows"], schema=headers, orient="row")


    zen_pricing_df = build_pricing_df(zen_pricing_table)
    go_pricing_df = build_pricing_df(go_pricing_table)
    go_estimated_requests_df = build_estimated_requests_df(go_estimated_requests_table)
    go_endpoints_df = build_model_info_df(
        go_endpoints_table,
        {"Model ID": "model_id", "Endpoint": "endpoint", "AI SDK Package": "ai_sdk_package"},
    )
    go_privacy_df = build_model_info_df(
        go_privacy_table,
        {"Model training": "model_training", "Data retention": "data_retention"},
    )
    return (
        MODEL_COL,
        go_endpoints_df,
        go_estimated_requests_df,
        go_pricing_df,
        go_privacy_df,
        zen_pricing_df,
    )


@app.cell(hide_code=True)
def _(
    MODEL_COL,
    go_endpoints_df,
    go_estimated_requests_df,
    go_pricing_df,
    go_privacy_df,
):
    go_combined_df = (
        go_pricing_df
        .join(go_estimated_requests_df, on=MODEL_COL, how="full", coalesce=True)
        .join(go_endpoints_df, on=MODEL_COL, how="full", coalesce=True)
        .join(go_privacy_df, on=MODEL_COL, how="full", coalesce=True)
        .with_columns(
            ((pl.col("input_usd") == 0) & (pl.col("output_usd") == 0)).fill_null(False).alias("free")
        )
    )
    # go_combined_display_df = go_combined_df.select(sorted(go_combined_df.columns))
    go_combined_display_df = go_combined_df
    return go_combined_df, go_combined_display_df


@app.cell(hide_code=True)
def _():
    models_dev_catalog = requests.get(
        "https://models.dev/catalog.json?type=all",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=60,
    ).json()


    def models_dev_provider_df(provider_key):
        """Flatten a models.dev provider's models into a tidy DataFrame."""
        provider = models_dev_catalog["providers"][provider_key]
        records = []
        for model_id, model in provider["models"].items():
            cost = model.get("cost") or {}
            limit = model.get("limit") or {}
            records.append({
                "model_id": model_id,
                "name": model.get("name"),
                "input_usd": cost.get("input"),
                "output_usd": cost.get("output"),
                "cache_read_usd": cost.get("cache_read"),
                "cache_write_usd": cost.get("cache_write"),
                "context": limit.get("context"),
                "max_output": limit.get("output"),
                "reasoning": model.get("reasoning"),
                "tool_call": model.get("tool_call"),
            })
        return pl.DataFrame(records)


    zen_models_dev_df = models_dev_provider_df("opencode")
    go_models_dev_df = models_dev_provider_df("opencode-go")

    # (zen_models_dev_df.shape, go_models_dev_df.shape)
    return go_models_dev_df, zen_models_dev_df


@app.cell(hide_code=True)
def _():
    top_n_models = mo.ui.slider(5, 30, value=15, step=1, label="Top N models to chart")
    top_n_models
    return (top_n_models,)


@app.function(hide_code=True)
def price_chart(df, n, title, metric_labels):
    """Grouped bar chart of the n most expensive models by output price."""
    chart_df = (
        df.filter(~pl.col("free"))
        .sort("output_usd", descending=True)
        .head(n)
        .unpivot(index="model", on=list(metric_labels), variable_name="metric", value_name="usd")
        .with_columns(pl.col("metric").replace(metric_labels))
        .filter(pl.col("usd").is_not_null())
    )
    order = (
        chart_df.filter(pl.col("metric") == metric_labels["output_usd"])
        .sort("usd", descending=True)["model"]
        .to_list()
    )
    return (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("usd:Q", title="USD per 1M tokens"),
            y=alt.Y("model:N", sort=order, title=None),
            color=alt.Color("metric:N", title=None),
            tooltip=["model", "metric", "usd"],
        )
        .properties(title=title, height=max(220, 26 * n))
    )


@app.cell(hide_code=True)
def _(top_n_models, zen_pricing_df):
    zen_display_df = zen_pricing_df.select(
        "model", "input_usd", "output_usd", "cached_read_usd", "cached_write_usd", "free"
    ).sort("output_usd", descending=True, nulls_last=True)

    mo.vstack([
        mo.md(f"### OpenCode Zen pricing ({zen_pricing_df.height} models, {zen_pricing_df['free'].sum()} free)"),
        mo.ui.table(zen_display_df),
        price_chart(
            zen_pricing_df,
            top_n_models.value,
            f"Top {top_n_models.value} Zen models by output price",
            {"input_usd": "Input", "output_usd": "Output"},
        ),
    ])
    return


@app.cell(hide_code=True)
def _(go_pricing_df, top_n_models):
    go_display_df = go_pricing_df.select(
        "model", "input_usd", "output_usd", "cached_read_usd", "cached_write_usd", "monthly_limit_usd"
    ).sort("output_usd", descending=True, nulls_last=True)

    mo.vstack([
        mo.md(f"### OpenCode Go pricing ({go_pricing_df.height} models) — monthly spend limits in USD"),
        mo.ui.table(go_display_df),
        price_chart(
            go_pricing_df,
            top_n_models.value,
            f"Top {top_n_models.value} Go models by output price",
            {"input_usd": "Input", "output_usd": "Output"},
        ),
    ])
    return


@app.cell(hide_code=True)
def _(
    go_combined_df,
    go_combined_display_df,
    go_endpoints_df,
    go_estimated_requests_df,
    go_pricing_df,
    go_privacy_df,
):
    go_estimated_requests_display_df = go_estimated_requests_df.sort(
        "per_month", descending=True, nulls_last=True
    )

    mo.vstack([
        mo.md(
            f"### OpenCode Go — model reference ({len(go_combined_df)} models)"
            "\n\nAll Go model data in one place. Use the tabs to see the combined table or each "
            "source table on its own."
        ),
        mo.ui.tabs({
            "Combined": mo.ui.table(go_combined_display_df),
            "Pricing": mo.ui.table(go_pricing_df),
            "Est. requests": mo.ui.table(go_estimated_requests_display_df),
            "Endpoints": mo.ui.table(go_endpoints_df),
            "Privacy": mo.ui.table(go_privacy_df),
        }),
    ])
    return


@app.cell(hide_code=True)
def _():
    models_dev_provider = mo.ui.dropdown(
        options={"OpenCode Zen": "opencode", "OpenCode Go": "opencode-go"},
        value="OpenCode Zen",
        label="Provider (models.dev catalog API)",
    )
    models_dev_provider
    return (models_dev_provider,)


@app.cell(hide_code=True)
def _(go_models_dev_df, models_dev_provider, zen_models_dev_df):
    models_dev_df = (
        zen_models_dev_df if models_dev_provider.value == "opencode" else go_models_dev_df
    ).sort("output_usd", descending=True, nulls_last=True)

    mo.vstack([
        mo.md(
            f"### models.dev catalog API — {models_dev_provider.value} "
            f"({models_dev_df.height} models, USD per 1M tokens)"
        ),
        mo.ui.table(models_dev_df),
    ])
    return


if __name__ == "__main__":
    app.run()
