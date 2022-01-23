import pytest

from phil.table import Table
from phil.deck import Deck, Card
from phil.simulator import (
    _simulate_straight,
    _simulate_four_of_a_kind
)


@pytest.fixture
def table():
    return Table()

@pytest.fixture
def deck():
    return Deck()

@pytest.fixture
def hand():
    strings = ["ah", "kh", "qh", "jh", "10h"]
    return [Card.from_string(s) for s in strings]

@pytest.mark.parametrize("suit", ["h", "d", "s", "c"])
def test_royal_flush(table, suit):
    ranks = ["a", "k", "q", "j", "10"]
    hand = [Card.from_string(r + suit) for r in ranks]
    assert table[table.encode(hand)] == 1

def test_straight(table):
    for _ in range(1000):
        hand = _simulate_straight()
        low = table.STRAIGHT.min_ranking
        top = table.STRAIGHT.max_ranking
        encoding = table.encode(hand)
        ranking = table[encoding]
        assert top <= ranking, hand
        assert ranking <= low, hand



