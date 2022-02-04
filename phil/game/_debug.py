from phil.deck import Card, Deck
from .player import Player


def force_hands(deck, config):
    """
    Modify the deck so that the specified
    cards are deal to the players in the preflop phase.
    """
    players = config["players"]
    sorted_players = sorted(
        players,
        key=lambda x: players[x]["position"]
    )
    first_cards = []
    second_cards = []
    for name in sorted_players:
        if hand := players[name].get("hand", ""):
            first, second = hand.split()
            first_cards.append(first)
            second_cards.append(second)

    for card in reversed(second_cards):
        deck.append(deck.get(card))

    for card in reversed(first_cards):
        deck.append(deck.get(card))

    return deck


def force_phases(deck, config):
    """
    Modify the deck so that the specified
    cards are dealt to the board during the
    post-flop phases.
    """
    for phase in "river turn flop".split():
        cards_string = config["deck"][phase]
        cards = (Card(s) for s in cards_string.split())
        for card in cards:
            deck.append(deck.get(card))

    return deck


def build_deck(config):
    deck = Deck()
    deck = force_phases(deck, config)
    deck = force_hands(deck, config)
    return deck


def _get_policy(name):
    import importlib
    module_name = "phil.game.policies"
    module = importlib.import_module(module_name)
    policy = getattr(module, name)
    return policy


def build_players(config, keep_hand=False):
    players_info = config["players"]
    players_objects = []
    for _, kwargs in players_info.items():
        kwargs = kwargs.copy()
        if not keep_hand:
            kwargs.pop("hand")
        else:
            kwargs["hand"] = [Card(s) for s in kwargs["hand"].split()]

        kwargs["policy"] = _get_policy(kwargs["policy"])
        players_objects.append(Player(**kwargs))

    return sorted(players_objects, key=lambda x: x.position)
