# /// script
# dependencies = [
#     "gdrive-fsspec==0.4.1",
#     "marimo",
#     "polars==2.0.0",
# ]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    from gdrive_fsspec import GoogleDriveFileSystem

    return GoogleDriveFileSystem, mo


@app.cell
def _(GoogleDriveFileSystem):
    fs = GoogleDriveFileSystem(use_listings_cache=False, skip_instance_cache=True)
    return (fs,)


@app.cell
def _():
    return


@app.cell
def _(fs, mo):
    documents_files = fs.ls("Documents", detail=True)

    rows = "\n".join(
        f"- **{f['name'].split('/')[-1]}**"
        for f in documents_files
    )

    mo.md(
        f"""## Files in the `Documents` directory ({len(documents_files)} found)

    {rows}
    """
    )
    return


if __name__ == "__main__":
    app.run()
