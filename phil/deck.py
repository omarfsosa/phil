import enum
import itertools
import random
from dataclasses import dataclass


# Ranks
_PRIME_RANKS = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
_STR_RANKS = list("23456789") + ["10", "J", "Q", "K", "A"]
_STR_TO_PRIME = dict(zip(_STR_RANKS, _PRIME_RANKS))
_PRIME_TO_STR = dict(zip(_PRIME_RANKS, _STR_RANKS))

# Suits
_HEART_SYMBOL = u"\u2661"
_DIAMOND_SYMBOL = u"\u2662"
_SPADE_SYMBOL = u"\u2664"
_CLUB_SYMBOL = u"\u2667"
_STR_SUITS = list("HDSC")
_SYM_SUITS = [_HEART_SYMBOL, _DIAMOND_SYMBOL, _SPADE_SYMBOL, _CLUB_SYMBOL]
_INT_TO_SYM = dict(zip(range(4), _SYM_SUITS))
_STR_TO_INT = dict(zip(_STR_SUITS, range(4)))

class Suit(enum.Enum):
    HEARTS = 0
    DIAMONDS = 1
    SPADES = 2
    CLUBS = 3

    def __str__(self):
        return _INT_TO_SYM[self.value]
    
    @classmethod
    def from_string(cls, s):
        return cls(_STR_TO_INT[s.upper()])


class Rank(enum.Enum):
    """
    Enumerate with prime numbers for fast hand evaluation.
    http://suffe.cool/poker/evaluator.html
    """
    TWO = 2
    THREE = 3
    FOUR = 5
    FIVE = 7
    SIX = 11
    SEVEN = 13
    EIGHT = 17
    NINE = 19
    TEN = 23
    JACK = 29
    QUEEN = 31
    KING = 37
    ACE = 41
    
    def __str__(self):
        return _PRIME_TO_STR[self.value]
    
    @classmethod
    def from_string(cls, r):
        return cls(_STR_TO_PRIME[r.upper()])


@dataclass
class Card:
    rank: Rank
    suit: Suit

    def __str__(self):
        return f"{self.rank!s}{self.suit!s}"
    
    def __repr__(self):
        return f"{self.rank!s}{self.suit!s}"
    
    @classmethod
    def from_string(cls, rs):
        rs = rs.upper()
        rank = Rank.from_string(rs[:-1])
        suit = Suit.from_string(rs[-1])
        return cls(rank, suit)



class Deck:
    def __init__(self, cards=None):
        if cards is not None:
            self.cards = list(cards)
        else:
            self._reset()
            self.shuffle()
            
    def _reset(self):
        """
        Return all cards to the deck, in order.
        """
        self.cards = [Card(r, s) for r, s in itertools.product(Rank, Suit)]

    def shuffle(self):
        """
        Shuffle all cards (in place)
        """
        random.shuffle(self.cards)
    
    def __len__(self):
        return len(self.cards)
    
    def __getitem__(self, index):
        return self.cards[index]
    
    def __iter__(self):
        return iter(self.cards)
    
    def show(self, n=None):
        top = list(reversed(self))
        print(", ".join(str(card) for card in top[:n]))
    
    def draw(self, n=1):
        if n == 1:
            return self.cards.pop()        
        
        return [self.cards.pop() for _ in range(n)]
    
    def remove(self, *cards):
        for card in cards:
            self.cards.remove(card)

if __name__ == "__main__":
    r = Rank.ACE
    s = Suit.DIAMONDS
    c = Card(rank=Rank.TWO, suit=Suit.SPADES)
    d = Deck()
    hand = d.draw(5)
    print(hand)
    colors = set(card.suit for card in hand)
    print(colors)