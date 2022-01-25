import pytest

from phil.deck import Hand
from phil.table import LookupTable


@pytest.fixture
def table():
    return LookupTable()

def known_hands():
    return {
        "argnames": ("string", "ranking"),
        "argvalues": [
            ("ah kh qh jh th", 1),
            ("ah ad as ac kh", 11),
            ("ah ad as kc kh", 167),
            ("ah kh qh jh 9h", 323),
            ("ah kh qh jh td", 1600),
            ("ah ad as kc qh", 1610),
            ("ah ad ks kc qh", 2468),
            ("ah ad ks qc jh", 3326),
            ("ah kh qh jh 9s", 6186),
        ],
        "ids": [
            "Straight flush",
            "Four of a kind",
            "Full house",
            "Flush",
            "Straight",
            "Three of a kind",
            "Two pair",
            "One pair",
            "High card",
        ]
    }


@pytest.mark.parametrize(**known_hands())
def test_table(table, string, ranking):
    assert table.find(Hand.from_string(string)) == ranking
