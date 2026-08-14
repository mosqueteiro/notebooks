# /// script
# dependencies = [
#     "marimo",
#     "openai==3.0.0",
# ]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from openai import OpenAI

    return OpenAI, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Max server
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    First experiment, getting the docker container running. Initially the container wouldn't work with `gemma-3-27b-it`. It said there wasn't enough memory, `66.37 GiB > 56.29 GiB`. There shold be plenty of memory though. I checked and there was like 96 GB available.

    ```error
    RuntimeError: Model size exceeds available memory (66.37 GiB > 56.29 GiB). Model weights: 51.10 GiB, Activation memory: 15.00 GiB, Signal buffers: 280.75 MiB. Try running a smaller model, using a smaller precision, or using a device with more memory.
    ```

    Eventually I found a very small model, `gemma-3-4b-it`, however this is taking quite a large amount of memory. This model isn't quantized, it is using BG16. It is taking like 70 GB or something.

    Ran with `podman`

    ```bash
    podman run \
      -v ~/.cache/huggingface:/root/.cache/huggingface \
      -v ~/.cache/max_cache:/opt/venv/share/max/.max_cache \
      --env "HF_TOKEN=${HF_TOKEN}" \
      -p 8000:8000 \
      --group-add keep-groups \
      --device /dev/kfd \
      --device /dev/dri \
      docker.io/modular/max-amd:latest \
      --model google/gemma-3-4b-it
    ```

    I'll have to see if max can run quantized versions of models it supports.
    """)
    return


@app.cell
def _(OpenAI):
    client =  OpenAI(
        base_url="http://0.0.0.0:8000/v1",
        api_key="EMPTY",
    )
    return (client,)


@app.cell
def _(mo):
    current_model_input = mo.ui.text(label="Model: ").form()
    current_model_input
    return (current_model_input,)


@app.cell
def _(client, current_model_input, mo):
    mo.stop(not current_model_input.value, "Input model to contiue")

    completion = client.chat.completions.create(
        model=current_model_input.value,
        messages=[
            {"role": "user",
             "content": "Who won the world series in 2020?"
            }
        ],
    )
    return (completion,)


@app.cell
def _(completion):
    completion
    return


@app.cell
def _(completion):
    completion.choices, completion.choices[0].message, completion.choices[0].message.content
    return


@app.cell
def _(current_model_input, mo):
    chatbot = mo.ui.chat(
        mo.ai.llm.openai(
            current_model_input.value,
            system_message="You unhelpful assistant.",
            api_key="EMPTY",
            base_url="http://0.0.0.0:8000/v1",
        ),
    )

    chatbot
    return


if __name__ == "__main__":
    app.run()
