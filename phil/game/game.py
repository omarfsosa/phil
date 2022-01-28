from dataclasses import dataclass, field
from itertools import cycle

from phil.deck import Deck
from phil.exceptions import PokerContextError
from phil.game.policies import prompt_for_input

PHASES = ("preflop", "flop", "turn", "river")
ACTIONS = ("fold", "check", "call", "bet", "raise")


@dataclass(frozen=True)
class GameContext:
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


@dataclass
class Player:
    """
    A texas holdem player.

    Parameters
    ----------
    name: str
        The display name of the player.

    chips: float >= 0
        The amount of money available for betting

    policy: Callable[[Player, GameContext], [Action]]
        A function of the form `function(player, context)` that
        determines the amount of money the player will move in
        depending on the situation.

    position: int
        Position at the table. Dealer is at -1.
        The first player to talk is at postion 0.

    _round_bet: float
        How much money has the player bet in the current round

    _phase_bet: float
        How much money has the player bet in the current phase

    _talked: bool
        Whether or not the player has had the chance to make a decision
        in the current phase

    _folded: bool
        Whether or not the player has folded his/her hand.
    """

    name: str
    chips: float = 0
    hand: list = field(default_factory=list)
    policy: callable = field(repr=False, default=prompt_for_input)
    position: int = field(default=0, repr=False)
    _round_bet: float = field(default=0, repr=False)
    _phase_bet: float = field(default=0, repr=False)
    _talked: bool = field(default=False, repr=False)
    _folded: bool = field(default=False, repr=False)

    def bet(self, amount):
        if amount > self.chips:
            _msg = f"Max bet allowed is ${self.chips}, but attempted ${amount}"
            raise ValueError(_msg)

        self.chips -= amount
        self._phase_bet += amount
        self._round_bet += amount
        return amount

    @property
    def is_all_in(self):
        return self._round_bet and not self.chips and not self._folded


class PokerRound:
    """
    A round of poker between `players`. It will be assumed that
    the last player in the list `players` has the dealer button.
    All players entering the round must have chips to play.
    """

    def __init__(self, players, sb=1, bb=2):
        self.players = players
        self.sb = sb
        self.bb = bb
        # -- auto:
        self.phase = "preflop"
        self.board = []
        self.deck = Deck()
        self._num_phase_bets = 0
        self.reset_players_status()

    def reset_players_status(self):
        for n, player in enumerate(self.players):
            player.hand = []
            player._phase_bet = 0
            player._round_bet = 0
            player._talked = False
            player._folded = False
            player.position = n

    def play(self):
        iterplayers = self.iter_players()
        next(iterplayers).bet(self.sb)
        next(iterplayers).bet(self.bb)
        for phase in PHASES:
            self.phase = phase
            self.deal(phase)
            print(f"Phase: {phase}")
            print(f"Board: {self.board}")
            self.betting_round(iterplayers)
            self._reset_betting_round()
            iterplayers = self.iter_players()
            print("=" * 30)
        self.split_pot()

    def deal(self, phase):
        """
        Deal cards to player or to the board
        depending on the phase of the round.
        """
        if phase == "preflop":
            self._deal_hands()
        elif phase == "flop":
            self._deal_flop()
        elif phase in ["turn", "river"]:
            self._deal_turn_or_river()

    def _deal_hands(self):
        for player in self.players:
            player.hand = self.deck.draw(2)

    def _deal_flop(self):
        self.board.extend(self.deck.draw(3))

    def _deal_turn_or_river(self):
        self.board.extend(self.deck.draw(1))

    def iter_players(self, skip=True):
        """
        Cycle through the active players in the round.
        """
        for player in cycle(self.players):
            in_game = player.chips and not player._folded
            if in_game or not skip:
                yield player
            else:
                continue

    def betting_round(self, iterplayers):
        while not self.in_equilibrium:
            player = next(iterplayers)
            amount = player.policy(player, self.context)
            self.process_bet_in_context(player, amount)

    def process_bet_in_context(self, player, amount):
        current = player._phase_bet
        target = self.max_phase_bet
        delta = target - current
        chips = player.chips

        if player.is_all_in:  # Player cant take further actions
            return

        if not amount and not delta:
            action = "check"
        elif amount and not delta:
            action = "bet"
        elif amount > delta:
            action = "raise"
        elif amount == delta:  # exlcludes 0 == 0 by previous case
            action = "call"
        elif amount == chips < delta:  # allows amount < delta as long as we move all in
            action = "call"
        elif amount < delta:
            # invalid action, autofold
            action = "fold"
            amount = 0
        else:
            raise PokerContextError

        player.bet(amount)
        player._talked = True
        player._folded = action == "fold"
        if action in ["bet", "raise"]:
            self._num_phase_bets += 1

        return action

    def _reset_betting_round(self):
        for player in self.players:
            player._talked = False
            player._phase_bet = 0

    # --- Properties to keep track of the round
    @property
    def max_phase_bet(self):
        return max(p._phase_bet for p in self.players)

    @property
    def num_phase_bets(self):
        return self._num_phase_bets

    @property
    def pot(self):
        return sum(p._round_bet for p in self.players)

    @property
    def in_equilibrium(self):
        """
        Every player has had the chance to talk and
        match the target bet, or they are all in.
        their are either all in or
        """
        players = [p for p in self.players if not p._folded]
        max_bet = self.max_phase_bet
        talked = (p._talked for p in players)
        all_in = ((p._round_bet > 0) and (p.chips == 0) for p in players)
        has_bet = (p._phase_bet == max_bet for p in players)
        agreed = (t and b for t, b in zip(talked, has_bet))
        agreed_or_all_in = (a or b for a, b in zip(agreed, all_in))
        return all(agreed_or_all_in)

    @property
    def context(self):
        """
        Information about the current state of the round
        """
        return GameContext.from_round(self)

    # --- Logic to end the poker round
    def split_pot(self):
        pass
        # players = players that did not fold
        # bets = sorted unique (plyr.round_bet for plyr in players)
        # baseline = 0
        # for bet in bets:
        #     delta_bet = bet - baseline
        #     competing = select players with roundbet >= delta_bet
        #     winners = determine winner from competing players
        #     subpot = delta_bet * len(competing)
        #     split subpot equally among winners
        #     subtract subpot from total pot
        #     for each competing player
        #         subtract amount_left from plyr's round_bet
        #     baseline += delta_bet


if __name__ == "__main__":
    players = [
        Player("A", chips=20),
        Player("B", chips=40),
        Player("C", chips=10),
        Player("D", chips=40),
    ]
    round_ = PokerRound(players)
    round_.play()
    print("Round finished!")
    for p in round_.players:
        print(p.name, p.chips, p._round_bet, p._folded)
