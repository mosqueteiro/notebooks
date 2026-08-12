import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    from dataclasses import dataclass

    import marimo as mo

    return dataclass, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Select Players

    {players_slider}

    {players_array_form}
    """)
    return


@app.cell
def _(mo):
    min_p = 3
    max_p = 6
    players_slider = mo.ui.slider(start=min_p, stop=max_p, label="\# of players")

    player_arr = mo.ui.array(
        [mo.ui.text(label=f"Player {i+1}") for i in range(max_p)]
    )
    return player_arr, players_slider


@app.cell
def _(mo, player_arr, players_slider):
    selected_players = player_arr[:players_slider.value]
    rounds = 60 // players_slider.value

    mo.output.append(mo.hstack(
        [mo.md(f"{players_slider} {players_slider.value}"),
         mo.md(f"Rounds: {rounds}"),
        ],
        justify="space-around"
    ))
    mo.output.append(selected_players)
    return (selected_players,)


@app.cell
def _(player_arr):
    player_arr.value
    return


@app.cell
def _(selected_players):
    players = [player.value for player in selected_players]
    players
    return (players,)


@app.cell
def _(dataclass, mo):
    _get_game_state, _set_game_state = mo.state()

    @dataclass
    class GameState:
        players: list[str]
        max_round: int
        round: int
    

    return


@app.cell
def _(mo):
    def create_bid_form(players: list[str], round: int) -> mo.Html:
        if round <= 0:
            raise ValueError("Round must be positive")

        player_bids = {
            player: mo.ui.number(start=0, stop=round) for player in players
        }
        player_bids_form = (
            mo.md("\n".join(
                ["\n", "| Player | Bid |", "| ---: | :--- |"]
                + [f"| {player} | {{{player}}} |" for player in players]
            ))
            .batch(**player_bids)
            .form(label=f"**Set Bids**  \nRound: {round}")
        )

        return player_bids_form

    def create_trick_form(players: list[str], round: int) -> mo.Html:
        if round <= 0:
            raise ValueError("Round must be positive")

        def validate_trick_sum(val):
            if sum(val.values()) != round:
                return"Sum of Tricks must equal round #"

        player_bids = {
            player: mo.ui.number(start=0, stop=round) for player in players
        }
        player_bids_form = (
            mo.md("\n".join(
                ["\n", "| Player | Tricks |", "| ---: | :--- |"]
                + [f"| {player} | {{{player}}} |" for player in players]
            ))
            .batch(**player_bids)
            .form(
                label=f"**Set Tricks**  \nRound: {round}",
                validate=validate_trick_sum,
            )
        )

        return player_bids_form

    return create_bid_form, create_trick_form


@app.cell
def _(create_bid_form, players):
    bid_form = create_bid_form(players, 2)
    bid_form
    return (bid_form,)


@app.cell
def _(create_trick_form, players):
    trick_form = create_trick_form(players, 2)
    trick_form
    return (trick_form,)


@app.cell
def _(bid_form, trick_form):
    {
        "bid": bid_form.value,
        "trick": trick_form.value,
    }
    return


@app.function
def round_score(round: dict[str, dict[str, int]]) -> dict[str, int]:
    bids = round["bid"]
    tricks = round["trick"]
    score = {}
    for player, bid in bids.items():
        if bid == tricks[player]:
            score[player] = 20 + bid * 10
        else:
            score[player] = abs(bid - tricks[player]) * -10
    return score


@app.cell
def _(bid_form, trick_form):
    round_score({
        "bid": bid_form.value,
        "trick": trick_form.value,
    })
    return


if __name__ == "__main__":
    app.run()
