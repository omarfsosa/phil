import itertools
import math
import operator
from functools import reduce

from phil.deck import RANKS_PRM, SUIT_FACTOR


def _straights(suited=False):
    sorted_primes = (41,) + RANKS_PRM
    table = {}
    for n in range(10):
        cards = sorted_primes[n : n + 5]
        order = tuple(cards[::-1])
        code = math.prod(cards) * (SUIT_FACTOR if suited else 1)
        table[code] = order

    return sorted(table, key=table.get, reverse=True)


def _four_of_a_kind():
    primes_set = set(RANKS_PRM)
    table = {}
    for p in primes_set:
        kickers = primes_set.difference((p,))
        for k in kickers:
            code = p ** 4 * k
            order = (p, k)
            table[code] = order

    return sorted(table, key=table.get, reverse=True)


def _full_house():
    primes_set = set(RANKS_PRM)
    table = {}
    for p in primes_set:
        kickers = primes_set.difference((p,))
        for k in kickers:
            code = p ** 3 * k ** 2
            order = (p, k)
            table[code] = order

    return sorted(table, key=table.get, reverse=True)


def _three_of_a_kind():
    primes_set = set(RANKS_PRM)
    table = {}
    for p in primes_set:
        kickers = primes_set.difference((p,))
        combs = itertools.combinations(kickers, 2)
        for k1, k2 in combs:
            # prime product: (base, high kick, low kick)
            table[p ** 3 * k1 * k2] = (p, max(k1, k2), min(k1, k2))

    return sorted(table, key=table.get, reverse=True)


def _two_pair():
    primes_set = set(RANKS_PRM)
    table = {}
    for p1, p2 in itertools.combinations(primes_set, 2):
        kickers = primes_set.difference((p1, p2))
        for k in kickers:
            # prime product: (high pair, low_pair, kicker)
            table[p1 ** 2 * p2 ** 2 * k] = (max(p1, p2), min(p1, p2), k)

    return sorted(table, key=table.get, reverse=True)


def _one_pair():
    primes_set = set(RANKS_PRM)
    table = {}
    for p in primes_set:
        kickers = primes_set.difference((p,))
        for ks in itertools.combinations(kickers, 3):
            code = p ** 2 * math.prod(ks)
            order = (p, *sorted(ks, reverse=True))
            # prime product: (pair, high kick, mid kick, low kick)
            table[code] = order

    return sorted(table, key=table.get, reverse=True)


def _high_card(suited=False):
    primes_set = set(RANKS_PRM)
    straights = _straights()
    table = {}
    for ks in itertools.combinations(primes_set, 5):
        code = math.prod(ks)
        if code in straights:
            continue

        code *= SUIT_FACTOR if suited else 1
        order = tuple(sorted(ks, reverse=True))
        table[code] = order

    return sorted(table, key=table.get, reverse=True)


class NamedHand:
    def __init__(self, name, codes, top_ranking, multiplicity):
        self.name = name
        self.codes = codes
        self.top_ranking = top_ranking
        self.multiplicity = multiplicity
        self.num_distinct = len(self.codes)
        self.num_unique = self.num_distinct * self.multiplicity

    @property
    def suited(self):
        return not (self.codes[0] % SUIT_FACTOR)

    def index(self, value):
        return self.codes.index(value)

    def __repr__(self):
        return f"<NamedHand({self.name})>"


class LookupTable:
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

    STRAIGHT_FLUSH = NamedHand("SF", _straights(True), 1, 4)
    FOUR_OF_A_KIND = NamedHand("FK", _four_of_a_kind(), 11, 4)
    FULL_HOUSE = NamedHand("FH", _full_house(), 167, 24)
    FLUSH = NamedHand("FL", _high_card(True), 323, 4)
    STRAIGHT = NamedHand("ST", _straights(), 1600, 1020)
    THREE_OF_A_KIND = NamedHand("TK", _three_of_a_kind(), 1610, 64)
    TWO_PAIR = NamedHand("TP", _two_pair(), 2468, 144)
    ONE_PAIR = NamedHand("OP", _one_pair(), 3326, 384)
    HIGH_CARD = NamedHand("HC", _high_card(), 6186, 1020)

    NAMED_HANDS = (
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
        self._table = {
            code: named.top_ranking + named.index(code)
            for named in self.NAMED_HANDS
            for code in named.codes
        }

    def __getitem__(self, index):
        return self._table[index]

    def find(self, cards):
        combinations = itertools.combinations(cards, 5)
        codes = (self.encode(comb) for comb in combinations)
        return min(self[code] for code in codes)

    @staticmethod
    def encode(cards):
        prime_product = math.prod(card.rank_prm for card in cards)
        suited = bool(reduce(operator.and_, cards) & 0xF000)
        return prime_product * (SUIT_FACTOR if suited else 1)
