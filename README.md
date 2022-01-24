# The Name is Phil
A python package for calculating stats in Texas Hold'em

## Install
```
pip install .
```

Install with developer dependencies
```
pip install .[dev,test]
```

## Example usage

```python
from phil.deck import Deck, Hand
from phil.table import LookupTable

deck = Deck() # Creates a full shuffled deck
hand = Hand(deck.draw(5))
print(hand)
```
Should output something like:
```
Hand(9♤, 9♧, 2♤, 7♡, J♡)
```

Then to get the hand ranking:
```python
table = LookupTable()
ranking = table.find(hand)
```

Also works with simple list of cards, or directly with the hand encoding:
```python
cards = hand.cards
encoding = hand.encode()

table.find(encoding) == table.find(cards) # True
```
