from random import shuffle
from tkinter import E


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

    short_name = {
        'Strength':'Str',
        'Stamina':'Sta',
        'Speed':'Spd',
        'Quickness':'Qck',
        'Dexterity':'Dex',
        'Perception':'Per',
        'Intelligence':'Int',
        'Cunning':'Cun',
        'Luck':'Luc',
        'Fatigue':'Fat'
    }

    colors = {
        'Strength': 'R',
        'Stamina': 'R',
        'Speed': 'Y',
        'Quickness': 'Y',
        'Dexterity': 'G',
        'Perception': 'G',
        'Intelligence': 'B',
        'Cunning': 'B',
        'Luck': 'P'
    }

    def __init__(self, name):
        self.name = name
        self.type = Card.types[name]
        self.short = Card.short_name[name]
        self.color = Card.colors.get(name, '')


class Skill:
    costs = {
        'Focus': {'B': 2}
    }

    affinities = {
        'Focus': 'Intelligence'
    }

    effects = {
        'Focus': {'draw': 2}
    }

    def __init__(self, name):
        self.name = name
        self.cost = Skill.costs[name]
        self.affinity = Skill.affinities[name]
        self.effect = Skill.effects[name]
        self.cards = []

    def paid(self):
        p = {
            'B':0,
            'Y':0,
            'G':0,
            'R':0
        }
        for c in self.cards:
            if c.color == 'P':
                p[Card.colors[self.affinity]] += 2
                continue
            p[c.color] += 1
            if c.name == self.affinity:
                p[c.color] += 1
        return p

    def cost_text(self, p):
        return ''.join([x * p[x] for x in p])

    def is_paid(self):
        p = self.paid()
        for c in self.cost:
            if p[c] < self.cost[c]:
                return False
        return True

    def activate(self, deck):
        if self.is_paid():
            for e in self.effect:
                if e == 'draw':
                    deck.draw(self.effect[e])
        self.cards = []
                    

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

    def draw(self, n):
        if len(self.cards) < n:
            self.cards = self.discard[:] + self.cards[:] + [Card('Fatigue')]
            shuffle(self.cards)
            self.discard = []
        self.hand += self.cards[:n]
        del self.cards[:n]

    def refresh_hand(self):
        self.discard += self.hand
        self.hand = []
        self.draw(5)
        if len([x for x in self.hand if x.type == 'status']) >= 5:
            self.alive = False

    def display(self, turn):
        print(
            str(turn) + ' ' * (5-len(str(turn))), 
            f'Hand: {[x.short for x in self.hand]}', 
            f'Deck: {len(self.cards)}' + ' ' * (5-len(str(len(self.cards)))), 
            f'Discard: {len(self.discard)}' + ' ' * (5-len(str(len(self.discard))))
            )


if __name__ == '__main__':
    deck = Deck()
    skill = Skill('Focus')
    turn = 1
    i = ''
    while deck.alive:
        if i == 'q':
            break
        skill.cards = []
        deck.refresh_hand()
        while True:
            deck.display(turn)
            i = input('Action: ')
            if i in ['q', 'e']:
                break
            c = deck.hand.pop(int(i)-1)
            deck.discard.append(c)
            skill.cards.append(c)
            skill.activate(deck)
            print(f'{skill.name} ({skill.cost_text(skill.cost)}) : {skill.cost_text(skill.paid())} {skill.is_paid()}')
        turn += 1
    print('You died.')



