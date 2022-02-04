from itertools import cycle
from .events import Event, Request


def all_talked(players):
    """
    All players with chips have had the chance to act.
    """
    return all(
        player._talked or not player.chips
        for player in players if player.chips
    )


def all_matched(players, target):
    """
    All players who havent folded match the target bet or are all in.
    """
    return all(
        player._phase_bet == target or not player.chips
        for player in players
        if not player._folded
    )


def betting_round(players):
    assert all(not plyr._folded for plyr in players)
    for plyr in players:
        plyr._talked = False

    target = 0
    iterplayers = enumerate(cycle(players))
    for n, player in iterplayers:
        if player._folded or not player.chips:
            continue

        request = Request(n, player, target)
        response = yield request
        event = Event(request, response)
        event.execute()
        event.describe()
        target = max(plyr._phase_bet for plyr in players)
        finished = all_talked(players) and all_matched(players, target)
        if finished:
            break
