import random
from phil.deck import Card

STR_SUITS = "hdsc"
STR_SORTED_RANKS = list("A23456789") + ["10", "J", "Q", "K", "A"]
HAND_SIZE = 5


def parse(strings):
    return [Card.from_string(s) for s in strings]

def _simulate_straight():
    suits = random.choices(STR_SUITS, k=5)
    while len(set(suits)) == 1:
        # all suits should not be equal!
        suits = random.choices(STR_SUITS, k=5)

    low = random.randint(0, 9)
    ranks = STR_SORTED_RANKS[low: low + 5]
    cards = [r + s for r, s in zip(ranks, suits)]
    return parse(cards)

def _simulate_four_of_a_kind():
    four, kicker = random.sample(STR_SORTED_RANKS[1:], k=2)
    doubled_suit = random.choice(STR_SUITS)
    cards = [four + s for s in STR_SUITS] + [kicker + doubled_suit]
    return parse(cards)


if __name__ == "__main__":
    from collections import Counter
    
    def sim1():
        suits = random.choices(STR_SUITS, k=5)
        while len(set(suits)) == 1:
            suits = random.choices(STR_SUITS, k=5)
        
        return "".join(sorted(suits))
    
    def sim2():
        suits = STR_SUITS * 4
        return "".join(sorted(random.sample(suits, k=5)))
    
    num_sims = 100_000
    x1 = [sim1() for _ in range(num_sims)]
    x2 = [sim2() for _ in range(num_sims)]
    c1 = Counter(x1)
    c2 = Counter(x2)
    print(c1)
    print()
    print(c2)