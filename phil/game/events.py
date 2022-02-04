from dataclasses import dataclass
from phil.game import Player
from phil.exceptions import PokerContextError


@dataclass
class Request:
    """
    Request the `player` to match the `target` bet.
    """
    turn: int
    player: Player
    target: float


@dataclass
class Response:
    """
    Players' amount of money to move into the pot
    in response to a `Request`.
    """
    amount: float
    blind: bool = False


class Event:
    def __init__(self, request, response):
        self.request = request
        self.response = response
        self.name = self._get_name()
        self.description = self._get_description()
        self._executed = False

    def execute(self):
        if self.name in ("call", "bet", "raise"):
            self.player.bet(self.amount)
        elif self.name == "fold":
            self.player._folded = True

        self.player._talked = not self.response.blind
        self._executed = True

    def describe(self):
        print(self.description)

    def _get_description(self):
        """
        A string describing the event. This must be constructed
        before the money is moved into the pot.
        """
        pre = f"{self.request.player.name} {self.name}s"
        if self.name in ("call", "bet", "raise"):
            pre += f" ${self.response.amount}"

        if self.amount == self.request.player.chips:
            pre += " ALL IN!"

        return pre

    def _get_name(self):
        amount = self.response.amount
        target = self.request.target
        tocall = target - self.request.player._phase_bet
        chips = self.request.player.chips

        if not amount and not tocall:
            return "check"
        elif amount and not tocall:
            return "bet"
        elif amount > tocall:
            return "raise"
        elif amount == tocall:
            # exlcludes 0 == 0 by previous case
            return "call"
        elif amount == chips < tocall:
            # allows amount < delta as long as we move all in
            return "call"
        elif amount == 0:
            return "fold"
        else:
            raise PokerContextError
