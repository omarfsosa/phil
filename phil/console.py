from dataclasses import dataclass
import click

from phil.deck import Card
from phil.simulation import estimate_win_probabilty


@dataclass
class Summary:
    hand: list
    board: list
    win: float
    tie: float
    lose: float
    num_opponents: int
    num_samples: int

    def _header(self):
        hidden = "## "
        FLOP = hidden * 3
        TURN = hidden
        RIVER = hidden.strip()
        BOARD = FLOP + TURN + RIVER
        if len(self.board) >= 3:
            FLOP = " ".join(str(c) for c in self.board[:3]) + " "

        if len(self.board) >= 4:
            TURN = str(self.board[3]) + " "

        if len(self.board) == 5:
            RIVER = str(self.board[4])

        BOARD = FLOP + TURN + RIVER
        header = f"Board: {BOARD:<22}\n"
        divider = "=" * len(header) + "\n"
        return header + divider

    def _card_row(self):
        row_format = "{h0}{h1}: {win:3.2%} / {tie:3.2%} / {lose:3.2%}"
        return row_format.format(
            h0=self.hand[0],
            h1=self.hand[1],
            win=self.win,
            tie=self.tie,
            lose=self.lose,
        )

    def display(self):
        return self._header() + self._card_row()


@click.command()
@click.argument("hand")
@click.option("--board", type=str, default="", help="The board")
@click.option(
    "--num-opponents",
    type=int,
    default=1,
    help="How many opponents in the current hand?",
)
@click.option(
    "--num-samples",
    type=int,
    default=1000,
    help="Number of simulations used for the approximation.",
)
def win_probability(hand, board, num_opponents, num_samples):
    """Simple program that greets NAME for a total of COUNT times."""
    hand = [Card(s) for s in hand.split()]
    board = [Card(s) for s in board.split()]
    win_proba, tie_proba, lose_proba = estimate_win_probabilty(
        hand, board, num_opponents, num_samples
    )
    summary = Summary(
        hand, board, win_proba, tie_proba, lose_proba, num_opponents, num_samples
    )
    click.clear()
    click.echo(summary.display())
    # --- Continue?
    if len(board) == 0:
        flop = click.prompt("Flop?: ", type=str)
        board = board + [Card(s) for s in flop.split()]
        win_proba, tie_proba, lose_proba = estimate_win_probabilty(
            hand, board, num_opponents, num_samples
        )
        summary.board = board
        summary.win = win_proba
        summary.tie = tie_proba
        summary.lose = lose_proba
        click.clear()
        click.echo(summary.display())

    if len(board) == 3:
        turn = click.prompt("Turn?: ", type=str)
        board = board + [Card(turn)]
        win_proba, tie_proba, lose_proba = estimate_win_probabilty(
            hand, board, num_opponents, num_samples
        )
        summary.board = board
        summary.win = win_proba
        summary.tie = tie_proba
        summary.lose = lose_proba
        click.clear()
        click.echo(summary.display())

    if len(board) == 4:
        river = click.prompt("river?: ", type=str)
        board = board + [Card(river)]
        win_proba, tie_proba, lose_proba = estimate_win_probabilty(
            hand, board, num_opponents, num_samples
        )
        summary.board = board
        summary.win = win_proba
        summary.tie = tie_proba
        summary.lose = lose_proba
        click.clear()
        click.echo(summary.display())


if __name__ == "__main__":
    win_probability()
