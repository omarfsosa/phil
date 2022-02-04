from dataclasses import dataclass, field

from phil.game.policies import prompt_for_input


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

    policy: Callable[[Player, Contex], [Action]]
        A function of the form `function(player, context)` that
        determines the amount of money the player will move in
        depending on the situation.

    position: int
        Position at the table. Dealer is at -1.
        The first player to talk is at postion 0.

    _round_bet: float
        How much money has the player bet in the current round.

    _phase_bet: float
        How much money has the player bet in the current phase.

    _talked: bool
        Whether or not the player has had the chance to make a decision
        in the current phase.

    _folded: bool
        Whether or not the player has folded his/her hand in the round.
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
    _ranking: int = field(default=None, repr=False)

    def bet(self, amount):
        """
        Move `amout` out of the player's `chips` stack.
        Raises `ValueError` if there are not enough chips.`.
        """
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
