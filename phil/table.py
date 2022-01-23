import itertools
import math
from dataclasses import dataclass
from typing import Callable

from phil.deck import Rank

PRIMES = tuple(sorted(r.value for r in Rank))
NUM_DISTINCT_HANDS = 7462


def _straights():
    sorted_primes = (41,) + PRIMES
    table = {}
    for n in range(10):
        cards = sorted_primes[n: n + 5]
        order = tuple(cards[::-1])
        code = math.prod(cards)
        table[code] = order

    return sorted(table, key=table.get, reverse=True)


def _four_of_a_kind():
    primes_set = set(PRIMES)
    table = {}
    for p in primes_set:
        kickers = primes_set.difference((p,))
        for k in kickers:
            code = p ** 4 * k
            order = (p, k)
            table[code] = order

    return sorted(table, key=table.get, reverse=True)


def _full_house():
    primes_set = set(PRIMES)
    table = {}
    for p in primes_set:
        kickers = primes_set.difference((p,))
        for k in kickers:
            code = p ** 3 * k ** 2
            order = (p, k)
            table[code] = order

    return sorted(table, key=table.get, reverse=True)


def _three_of_a_kind():
    primes_set = set(PRIMES)
    table = {}
    for p in primes_set:
        kickers = primes_set.difference((p,))
        combs = itertools.combinations(kickers, 2)
        for k1, k2 in combs:
            # prime product: (base, high kick, low kick)
            table[p ** 3 * k1 * k2] = (p, max(k1, k2), min(k1, k2))

    return sorted(table, key=table.get, reverse=True)


def _two_pair():
    primes_set = set(PRIMES)
    table = {}
    for p1, p2 in itertools.combinations(primes_set, 2):
        kickers = primes_set.difference((p1, p2))
        for k in kickers:
            # prime product: (high pair, low_pair, kicker)
            table[p1 ** 2 * p2 ** 2 * k] = (max(p1, p2), min(p1, p2), k)

    return sorted(table, key=table.get, reverse=True)


def _one_pair():
    primes_set = set(PRIMES)
    table = {}
    for p in primes_set:
        kickers = primes_set.difference((p,))
        for ks in itertools.combinations(kickers, 3):
            code = p ** 2 * math.prod(ks)
            order = (p, *sorted(ks, reverse=True))
            # prime product: (pair, high kick, mid kick, low kick)
            table[code] = order

    return sorted(table, key=table.get, reverse=True)


def _high_card():
    primes_set = set(PRIMES)
    straights = _straights()
    table = {}
    for ks in itertools.combinations(primes_set, 5):
        code = math.prod(ks)
        if code in straights:
            continue

        order = tuple(sorted(ks, reverse=True))
        table[code] = order

    return sorted(table, key=table.get, reverse=True)


@dataclass
class NamedHand:
    name: str
    codes: list
    is_suited: bool
    max_ranking: int
    min_ranking: int
    multiplicity: int
    simulate: Callable = None

    def __post_init__(self):
        self.num_distinct = len(self.codes)
        self.num_unique = self.num_distinct * self.multiplicity

    @property
    def probability(self):
        return self.num_unique / NUM_DISTINCT_HANDS

    def __contains__(self, encoding):
        suited, prime_prod = encoding
        return (suited == self.is_suited) and (prime_prod in self.codes)

    def index(self, value):
        return self.codes.index(value)

    def __str__(self):
        return self.name.replace("_", " ").title()

    def __repr__(self):
        return f"<{self.name}>"

    def simulate(self):
        raise NotImplementedError


class Table:
    """
    Hand name     | Num distinct | Ranking interval
    ------------------------------------------------
    Straight flush        10        (   1 -   10)
    Four of a kind       156        (  11 -  166)    
    Full house           156        ( 167 -  322)
    Flush               1277        ( 323 - 1599) 
    Straight              10        (1600 - 1609)
    Three of a kind      858        (1610 - 2467) 
    Two pair             858        (2468 - 3325)
    One pair            2860        (3326 - 6185)
    High card           1277        (6186 - 7462)  
    """
    STRAIGHT_FLUSH  = NamedHand("straight_flush",        _straights(),  True,    1,   10,    4)
    FOUR_OF_A_KIND  = NamedHand("four_of_a_kind",   _four_of_a_kind(), False,   11,  166,    4)
    FULL_HOUSE      = NamedHand("full_house",           _full_house(), False,  167,  322,   24)
    FLUSH           = NamedHand("flush",                 _high_card(),  True,  323, 1599,    4)
    STRAIGHT        = NamedHand("straight",              _straights(), False, 1600, 1609, 1020)
    THREE_OF_A_KIND = NamedHand("three_of_a_kind", _three_of_a_kind(), False, 1610, 2467,   64)
    TWO_PAIR        = NamedHand("two_pair",               _two_pair(), False, 2468, 3325,  144)
    ONE_PAIR        = NamedHand("one_pair",               _one_pair(), False, 3326, 6185,  384)
    HIGH_CARD       = NamedHand("high_card",             _high_card(), False, 6186, 7462, 1020)

    _OPTIONS = (
        STRAIGHT_FLUSH,
        FOUR_OF_A_KIND,
        FULL_HOUSE,
        FLUSH,
        STRAIGHT,
        THREE_OF_A_KIND,
        TWO_PAIR,
        ONE_PAIR,
        HIGH_CARD,
    )

    def __init__(self):
        self._lookup = {
            (option.is_suited, code): option.max_ranking + option.index(code)
            for option in self._OPTIONS
            for code in option.codes
        }

    def __getitem__(self, index):
        return self._lookup[index]

    def lookup(self, hand):
        return min(self._lookup[self.encode(hand_5)] for hand_5 in itertools.combinations(hand, 5))

    def encode(self, hand):
        return self.is_suited(hand), math.prod(card.rank.value for card in hand)

    def is_suited(self, hand):
        return len(set(card.suit.value for card in hand)) == 1
