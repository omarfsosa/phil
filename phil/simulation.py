import random

from phil.deck import Deck
from phil.table import LookupTable
from phil.utils import group


def simulate(deck, board=None, num_opponents=1):
    board = board or []
    remaining = 5 - len(board)
    num_cards = remaining + 2 * num_opponents
    sim_cards = random.sample(deck, num_cards)
    if remaining > 0:
        sim_hands, sim_board = sim_cards[:-remaining], sim_cards[-remaining:]
    else:
        sim_hands, sim_board = sim_cards[:], []

    return sim_hands, board + sim_board


def is_win_or_tie(my_hand, op_hands, board, table=LookupTable()):
    rankings = [table.find(h + board) for h in group(op_hands, 2)]
    my_ranking = table.find(my_hand + board)
    is_win = all(my_ranking < r for r in rankings)
    is_tie = all(my_ranking <= r for r in rankings)
    return is_win, is_tie


def estimate_win_probabilty(my_hand, board=None, num_opponents=1, num_samples=1000):
    deck = Deck()
    table = LookupTable()
    board = board or []
    for card in my_hand:
        deck.remove(card)

    for card in board:
        deck.remove(card)

    num_wins = 0
    num_ties = 0
    for _ in range(num_samples):
        sim_hands, sim_board = simulate(deck, board, num_opponents)
        # print(sim_hands)
        win, tie = is_win_or_tie(my_hand, sim_hands, sim_board, table)
        num_wins += win
        num_ties += tie

    win_rate = num_wins / num_samples
    tie_rate = (num_ties - num_wins) / num_samples
    lose_rate = 1 - win_rate - tie_rate
    return win_rate, tie_rate, lose_rate
