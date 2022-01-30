from random import shuffle

class Card:
    types = {
            'Strength':'attribute',
            'Stamina':'attribute',
            'Speed':'attribute',
            'Quickness':'attribute',
            'Dexterity':'attribute',
            'Perception':'attribute',
            'Intelligence':'attribute',
            'Cunning':'attribute',
            'Luck':'attribute',
            'Fatigue':'status'
        }

    def __init__(self, name):
        self.name = name
        self.type = Card.types[name]


class Deck:
    def __init__(self):
        self.cards = [
            Card('Strength'),
            Card('Stamina'),
            Card('Speed'),
            Card('Quickness'),
            Card('Dexterity'),
            Card('Perception'),
            Card('Intelligence'),
            Card('Cunning')
        ] * 3 + [Card('Luck')]
        self.discard = []
        self.hand = []
        self.alive = True
        shuffle(self.cards)

    def draw(self):
        self.discard += self.hand
        if len(self.cards) < 5:
            self.cards = self.discard[:] + self.cards[:] + [Card('Fatigue')]
            shuffle(self.cards)
            self.discard = []
        self.hand = self.cards[:5]
        if all([x.type == 'status' for x in self.hand]):
            self.alive = False
        del self.cards[:5]


if __name__ == '__main__':
    deck = Deck()
    turn = 1
    while deck.alive:
        deck.draw()
        print(turn, [x.name for x in deck.hand], len(deck.cards))
        # input('')
        turn += 1
    print('dead')



