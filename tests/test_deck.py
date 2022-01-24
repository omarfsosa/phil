import pytest
from phil.deck import Deck, SUITS_BIN, RANKS_PRM


@pytest.fixture
def deck():
    return Deck()

def test_deck_length(deck):
    assert len(deck) == 52
    assert len(set(deck)) == 52

@pytest.mark.parametrize("suit", SUITS_BIN)
def test_deck_suits(deck, suit):
    assert sum(card.suit == suit for card in deck) == 13

@pytest.mark.parametrize("rank", range(13))
def test_deck_ranks(deck, rank):
    assert sum(card.rank == rank for card in deck) == 4

@pytest.mark.parametrize("prime", RANKS_PRM)
def test_deck_primes(deck, prime):
    assert sum(card.rank_prm == prime for card in deck) == 4

@pytest.mark.parametrize("card", Deck())
def test_card(card):
    bitrank = card.bitrank
    suit = card.suit
    rank = card.rank
    rank_prm = card.rank_prm
    bitstring = f"{bitrank:016b}-{suit:04b}-{rank:04b}-{rank_prm:08b}"
    assert card.as_bits() == bitstring