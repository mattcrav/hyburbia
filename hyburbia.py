from random import shuffle
from re import S
from tkinter import E


class Card:
    types = {
        'Strength': ['attribute','Str','R'],
        'Stamina': ['attribute','Sta','R'],
        'Speed': ['attribute','Spd','Y'],
        'Quickness': ['attribute','Qck','Y'],
        'Dexterity': ['attribute','Dex','G'],
        'Perception': ['attribute','Per','G'],
        'Intelligence': ['attribute','Int','B'],
        'Cunning': ['attribute','Cun','B'],
        'Luck': ['attribute','Luc','P'],
        'Fatigue': ['status','Fat',''],
    }

    def __init__(self, name):
        self.name = name
        self.type = Card.types[name][0]
        self.short = Card.types[name][1]
        self.color = Card.types[name][2]


class Skill:
    types = {
        'Focus': [{'B': 2},'Intelligence',{'draw': 2}],
        'Maneuver': [{'G': 2},'Dexterity',{'react': 2}],
        'Resist': [{'R': 2},'Stamina',{'heal': 2}],
        'Plan': [{'B': 2}, 'Cunning', {'keep': 2}]
    }

    def __init__(self, name):
        self.name = name
        self.cost = Skill.types[name][0]
        self.affinity = Skill.types[name][1]
        self.effect = Skill.types[name][2]
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
                p[Card.types[self.affinity][2]] += 2
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

    def activate(self, deck, cards):
        if self.is_paid():
            for e in self.effect:
                if e == 'draw':
                    deck.draw(self.effect[e])
                if e == 'react':
                    to_remove = []
                    for n in cards[:self.effect[e]]:
                        c = deck.hand[n]
                        to_remove.append(c)
                    deck.discard += to_remove
                    for r in to_remove:
                        deck.hand.remove(r)
                    deck.draw(self.effect[e])
                if e == 'heal':
                    to_remove = []
                    for n in cards[:self.effect[e]]:
                        c = deck.hand[n]
                        if c.type == 'status':
                            to_remove.append(c)
                    for r in to_remove:
                        deck.hand.remove(r)
                if e == 'keep':
                    to_remove = []
                    for n in cards[:self.effect[e]]:
                        c = deck.hand[n]
                        to_remove.append(c)
                    for r in to_remove:
                        deck.hand.remove(r)
                        deck.cards.insert(0, r)
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
            return False
        return True

    def play_card(self, n, skill):
        c = self.hand.pop(n)
        self.discard.append(c)
        skill.cards.append(c)

    def display(self, turn):
        print(
            str(turn) + ' ' * (5-len(str(turn))), 
            f'Hand: {[x.short for x in self.hand]}', 
            f'Deck: {len(self.cards)}' + ' ' * (5-len(str(len(self.cards)))), 
            f'Discard: {len(self.discard)}' + ' ' * (5-len(str(len(self.discard))))
            )


class Player:
    def __init__(self):
        self.deck = Deck()
        self.skills = [
            Skill('Focus'),
            Skill('Maneuver'),
            Skill('Resist'),
            Skill('Plan')
        ]

    def refresh_skills(self):
        for s in self.skills:
            s.cards = []

    def display_skills(self):
        for s in range(len(self.skills)):
            print(
                f'    {s+1}: ',
                f'{self.skills[s].name} ',
                f'({self.skills[s].cost_text(self.skills[s].cost)}) ',
                f'[{self.skills[s].cost_text(self.skills[s].paid())}] ',
                f"{'PAID' if self.skills[s].is_paid() else ''}"
                )

    def is_dead(self):
        if len([x for x in self.deck.hand if x.type == 'status']) >= 5:
            return True
        return False


if __name__ == '__main__':
    p = Player()
    turn = 1
    i = ''
    while not p.is_dead():
        if i == 'q':
            break
        p.deck.refresh_hand()
        p.refresh_skills()
        while not p.is_dead():
            p.deck.display(turn)
            i = input('Action: ')
            if i in 'qe':
                break
            if i[0] == 's':
                if len(i) == 1:
                    p.display_skills()
                else:
                    sp = i[1:].split('c')
                    cards = []
                    if 'c' in i:
                        cards = [int(x)-1 for x in sp[1]]
                    p.skills[int(sp[0])-1].activate(p.deck, cards)
            if i[0] == 'p':
                sp = i[1:].split('s')
                p.deck.play_card(int(sp[0])-1, p.skills[int(sp[1])-1])
        turn += 1
    print('You died.')