"""
Work in progress.
Card as an integer
"""
import math
import operator
import random
from collections import UserList
from functools import reduce
from itertools import product
from numbers import Integral

# RANKS
RANKS_STR = "23456789TJQKA"
RANKS_PRM = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)

# SUITS
SUITS_STR = "XCDXHXXXS"  # X: not used
SUITS_BIN = (1, 2, 4, 8)
SUITS_SYM = "X\u2667\u2662X\u2661XXX\u2664"  # unicode symbols, X not used.
_SUIT_FACTOR = 43


class Card(int):
    def __new__(cls, value):
        if isinstance(value, str):
            rank_str = value[0]
            suit_str = value[1]
            rank_int = RANKS_STR.index(rank_str.upper())
            suit_int = SUITS_STR.index(suit_str.upper())
            rank_prm = RANKS_PRM[rank_int]
            bitrank = 1 << rank_int << 16
            suit = suit_int << 12
            rank = rank_int << 8
            return cls(bitrank | suit | rank | rank_prm)
        elif isinstance(value, Integral):
            return int.__new__(cls, value)

    def __str__(self):
        return RANKS_STR[self.rank] + SUITS_SYM[self.suit]

    def __repr__(self):
        return RANKS_STR[self.rank] + SUITS_SYM[self.suit]

    @property
    def rank(self):
        return (self & 0xF00) >> 8

    @property
    def suit(self):
        return (self & 0xF000) >> 12

    @property
    def rank_prm(self):
        return self & 0xFF

    @property
    def bitrank(self):
        return (self & 0xFFFF0000) >> 16

    def as_bits(self):
        """
        For debugging purposes only.
        """
        b = format(self, "032b")
        bitrank, suit, rank, prime = b[:16], b[16:20], b[20:24], b[24:]
        return f"{bitrank}-{suit}-{rank}-{prime}"


class Deck(UserList):
    def __init__(self, cards=None):
        if cards is None:
            cards = self._generate_full_deck()

        super().__init__(cards)

    @staticmethod
    def _generate_full_deck(shuffle=True):
        ranks = RANKS_STR
        suits = SUITS_STR.replace("X", "")
        cards = [Card(r + s) for r, s in product(ranks, suits)]
        if shuffle:
            random.shuffle(cards)

        return cards

    def draw(self, n=1):
        """
        Take the top `n` cards.
        """
        return [self.pop() for _ in range(n)]

    def get(self, card):
        """
        Take a specific card out of the deck
        and return it.
        """
        card = Card(card)
        return self.pop(self.index(card))


class Hand:
    def __init__(self, cards):
        self.cards = list(cards)

    @classmethod
    def from_strings(cls, *strings):
        return cls(Card(s) for s in strings)

    @classmethod
    def from_string(cls, s):
        return cls.from_strings(*s.split())

    def __repr__(self):
        return f"Hand({str(self.cards)[1:-1]})"

    def __eq__(self, other):
        return set(self.cards) == set(other.cards)
    

    def __iter__(self):
        return iter(self.cards)

    def encode(self):
        prime_product = math.prod(card.rank_prm for card in self.cards)
        return prime_product * (_SUIT_FACTOR if self.suited else 1)

    @property
    def suited(self):
        return bool(reduce(operator.and_, self.cards) & 0xF000)
