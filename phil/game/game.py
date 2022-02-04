from dataclasses import dataclass
from itertools import chain, repeat

from phil.deck import Deck
from phil.table import LookupTable
from .betting import betting_round
from .events import Response


@dataclass(frozen=True)
class Context:
    """
    A dataclass with a summary of the current state of a poker round
    """

    sb: float
    bb: float
    board: list
    pot: float
    num_phase_bets: int
    max_phase_bet: float
    num_players: int
    _max_number_of_phase_bets: int = 4

    @classmethod
    def from_round(cls, poker_round):
        return cls(
            sb=poker_round.sb,
            bb=poker_round.bb,
            board=poker_round.board,
            pot=poker_round.pot,
            num_phase_bets=poker_round.num_phase_bets,
            max_phase_bet=poker_round.max_phase_bet,
            num_players=len(poker_round.players),
        )


class Round:
    """
    A round of poker between `players`. It will be assumed that
    the last player in the list `players` has the dealer button.
    All players entering the round must have chips to play.
    """
    PHASES = (
        "preflop",
        "flop",
        "turn",
        "river",
    )

    def __init__(self, players, sb=1, bb=2):
        self.players = players
        self.sb = sb
        self.bb = bb
        # -- auto:
        self.phase = "preflop"
        self.board = []
        self.deck = Deck()
        self.reset_players_status()

    def run(self, auto_blinds=True):
        for phase in self.PHASES:
            self.phase = phase
            self.deal()
            players = [plyr for plyr in self.players if not plyr._folded]
            betting = betting_round(players)
            request = next(betting)
            while True:
                is_blind = request.turn < 2 and phase == "preflop"
                if auto_blinds and is_blind:
                    amount = [self.sb, self.bb][request.turn]
                else:
                    player = request.player
                    amount = player.policy(player, self.context)

                response = Response(amount, is_blind)
                try:
                    request = betting.send(response)
                except StopIteration:
                    break

            num_in_game = sum(not plyr._folded for plyr in players)
            if num_in_game == 1:
                break
        else:
            print("Showdown!")

        self.split_pot()

    def reset_players_status(self):
        for n, player in enumerate(self.players):
            player.hand = []
            player._phase_bet = 0
            player._round_bet = 0
            player._talked = False
            player._folded = False
            player._ranking = None
            player.position = n

    def deal(self):
        """
        Deal cards to player or to the board
        depending on the phase of the round.
        """
        if self.phase == "preflop":
            seats = chain.from_iterable(repeat(self.players, 2))
            for player in seats:
                player.hand.extend(self.deck.draw())
        elif self.phase == "flop":
            self.board.extend(self.deck.draw(3))
        elif self.phase in ["turn", "river"]:
            self.board.extend(self.deck.draw(1))

    @property
    def pot(self):
        return sum(p._round_bet for p in self.players)

    @property
    def max_phase_bet(self):
        return max(p._phase_bet for p in self.players)

    @property
    def max_round_bet(self):
        return max(p._round_bet for p in self.players if not p._folded)

    @property
    def context(self):
        """
        Information about the current state of the round
        """
        return Context.from_round(self)

    def split_pot(self):
        # -- rank the hand of each player
        table = LookupTable()
        for plyr in self.players:
            cards = plyr.hand.cards + self.board
            plyr._ranking = table.find(cards)

        # -- determine the winner(s) and split the pot
        players = [plyr for plyr in self.players if not plyr._folded]
        while self.pot > 0:
            minbet = min(p._round_bet for p in players)
            subpot = sum(min(p._round_bet, minbet) for p in players)
            top_ranking = min(p._ranking for p in players)
            top_players = [p for p in players if p._ranking == top_ranking]

            # -- split the subpot equally among winners
            for p in top_players:
                amount = subpot / len(top_players)
                p.chips += amount

            # -- update the pot:
            for p in self.players:
                p._round_bet -= min(p._round_bet, minbet)

        assert self.pot == 0
