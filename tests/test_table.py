import pytest

from phil.deck import Hand
from phil.table import LookupTable


@pytest.fixture
def table():
    return LookupTable()


@pytest.mark.parametrize("hand", [("ah kh qh jh th", 1), ("2s 3h 4c 5d 7h", 7462)])
def test_table(table, hand):
    string, ranking = hand
    assert table.find(Hand.from_string(string)) == ranking
