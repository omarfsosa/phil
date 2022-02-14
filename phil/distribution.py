import abc
import itertools
import random

from phil.deck import Card, RANKS_STR


class HandKey:
    """
    A str representing a type of hand.
    For example:
        - AAo: Pair of Aces
        - AKs: Ace + King, suited
        - ATo: Ace + Ten, offsuit

    The hand with the largest rank always goes first.
    """
    def __init__(self, key):
        self.key = key
        self.rank_1 = key[0]
        self.rank_2 = key[1]
        self.suited = key[2] == "s"

    def sample(self):
        if self.suited:
            suit1, suit2 = random.choices("chds", k=2)
        else:
            suit1 = random.choice("chds")
            suit2 = suit1

        return Card(self.rank_1 + suit1), Card(self.rank_2 + suit2)

    @classmethod
    def iterkeys(cls):
        """
        A generator for all possible hand keys
        """
        combinations = itertools.combinations_with_replacement(RANKS_STR, 2)
        for ranks in combinations:
            key = "".join(sorted(ranks, key=RANKS_STR.index, reverse=True))
            suits = "os" if key[0] != key[1] else "o"
            for suited in suits:
                yield cls(key + suited)


class BaseDistribution(abc.ABC):
    """
    A distribution over handkeys
    """
    def __init__(self, probabilities: dict):
        self.probabilities = probabilities

    def keys(self):
        return self.probabilities.keys()

    def values(self):
        return self.probabilities.values()

    def sample(self, n: int, block: list | None = None):
        """
        Return n hands sampled with replacement.
        Any hand that contains any of the blocked
        cards is rejected from the samples
        """
        block = set(block or [])
        population = list(self.keys())
        weights = list(self.values())
        samples = []
        while len(samples) < n:
            handkey, = random.choices(population, weights=weights, k=1)
            sample = handkey.sample()
            if set(sample).intersection(block):
                continue

            samples.append(sample)

        return samples


class Frequency(BaseDistribution):
    def __init__(self):
        super().__init__({k: self._proba(k) for k in HandKey.iterkeys()})

    def _proba(self, k):
        if k.suited:
            return 4 / 1326

        # pocket pair
        if k.rank_1 == k.rank_2:
            return 6 / 1326

        # offsuit
        return 12 / 1326
