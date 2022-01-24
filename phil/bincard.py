"""
Work in progress.
Card as an integer
"""
from numbers import Integral

# SUITS
RANKS_STR = "23456789TJQKA"
RANKS_PRM = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)

# SUITS
SUITS_STR = "XCDXHXXXS" # X: not used
SUITS_BIN = (1, 2, 4, 8)

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
        return RANKS_STR[self.rank] + SUITS_STR[self.suit]
    
    @property
    def rank(self):
        return (self & 0xF00) >> 8
    
    @property
    def suit(self):
        return (self & 0xF000) >> 12
    
    @property
    def rank_prm(self):
        return (self & 0xFF)
    
    @property
    def bitrank(self):
        return (c & 0xFFFF0000) >> 16