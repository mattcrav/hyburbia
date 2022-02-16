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
        'Wound': ['status','Wnd','']
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
        'Plan': [{'B': 2}, 'Cunning', {'keep': 2}],
        'Strike': [{'R': 2}, 'Strength', {'damage': 2}],
        'Dodge': [{'Y': 2}, 'Quickness', {'block': 2}],
    }

    def __init__(self, name):
        self.name = name
        self.cost = Skill.types[name][0]
        self.affinity = Skill.types[name][1]
        self.effect = Skill.types[name][2]
        self.cards = []
        self.used = False

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

    def activate(self, player, cards):
        if self.is_paid():
            for e in self.effect:
                if e == 'draw':
                    player.deck.draw(self.effect[e])
                if e == 'react':
                    to_remove = []
                    for n in cards[:self.effect[e]]:
                        c = player.deck.hand[n]
                        to_remove.append(c)
                    player.deck.discard += to_remove
                    for r in to_remove:
                        player.deck.hand.remove(r)
                    player.deck.draw(self.effect[e])
                if e == 'heal':
                    to_remove = []
                    for n in cards[:self.effect[e]]:
                        c = player.deck.hand[n]
                        if c.type == 'status':
                            to_remove.append(c)
                    for r in to_remove:
                        player.deck.hand.remove(r)
                if e == 'keep':
                    to_remove = []
                    for n in cards[:self.effect[e]]:
                        c = player.deck.hand[n]
                        to_remove.append(c)
                    for r in to_remove:
                        player.deck.hand.remove(r)
                        player.deck.cards.insert(0, r)
                if e == 'damage':
                    player.damage += self.effect[e]
                if e == 'block':
                    player.block += self.effect[e]
        self.cards = []
        self.used = True


class Enemy:
    types = {
        'Skate Punk': {'health':3, 'range':1, 'damage':2}
    }

    def __init__(self, name):
        self.name = name
        self.health = Enemy.types[name]['health']
        self.range = Enemy.types[name]['range']
        self.damage = Enemy.types[name]['damage']
        self.distance = 1

    def take_hit(self, player):
        if player.range >= self.distance:
            self.health -= player.damage

    def attack(self, player):
        if self.range >= self.distance:
            d = max(self.damage - player.block, 0)
            player.block = max(player.block - self.damage, 0)
            for i in range(d):
                player.take_hit('Wound')

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
        if not skill.used:
            c = self.hand.pop(n)
            self.discard.append(c)
            skill.cards.append(c)


class Player:
    def __init__(self):
        self.deck = Deck()
        self.range = 1
        self.damage = 0
        self.block = 0
        self.death_message = 'You died'
        self.skills = [
            Skill('Focus'),
            Skill('Maneuver'),
            Skill('Resist'),
            Skill('Plan'),
            Skill('Strike'),
            Skill('Dodge')
        ]
        self.enemies = [Enemy('Skate Punk')]

    def refresh_skills(self):
        for s in self.skills:
            s.cards = []
            s.used = False

    def refresh_stats(self):
        self.range = 1
        self.damage = 0
        self.block = 0

    def take_hit(self, type):
        if type == 'Wound':
            self.deck.cards.append(Card('Wound'))
            shuffle(self.deck.cards)

    def display_skills(self):
        for s in range(len(self.skills)):
            print(
                f'        {s+1}: ',
                f'{self.skills[s].name} ',
                f'({self.skills[s].cost_text(self.skills[s].cost)}) ',
                f'[{self.skills[s].cost_text(self.skills[s].paid())}] ',
                f"{'PAID' if self.skills[s].is_paid() else 'USED' if self.skills[s].used else ''}"
                )

    def display_enemies(self):
        for s in range(len(self.enemies)):
            print(
                f'        {s+1}: ',
                f'{self.enemies[s].name} ({self.enemies[s].distance})',
                f'Health: {self.enemies[s].health} ',
                f'Damage: {self.enemies[s].damage} ',
                f'Range: {self.enemies[s].range} ',
                )

    def display(self, turn):
        print(
            str(turn) + ' ' * (5-len(str(turn))), 
            f'Hand: {[x.short for x in self.deck.hand]} ', 
            f'Deck: {len(self.deck.cards)} ', 
            f'Discard: {len(self.deck.discard)} ',
            f'Damage: {self.damage} ',
            f'Range: {self.range} ',
            f'Block: {self.block} '
            )

    def is_dead(self):
        if len([x for x in self.deck.hand if x.type == 'status']) >= 5:
            return True
        return False


if __name__ == '__main__':
    p = Player()
    turn = 0
    i = ''
    while not p.is_dead():
        turn += 1
        if i == 'q':
            break
        p.deck.refresh_hand()
        p.refresh_skills()
        p.refresh_stats()
        while not p.is_dead():
            p.display(turn)
            i = input('    Action: ')
            if i in 'qe':
                for e in p.enemies:
                    e.attack(p)
                break
            if i[0] == 's':
                if len(i) == 1:
                    p.display_skills()
                else:
                    sp = i[1:].split('c')
                    cards = []
                    if 'c' in i:
                        cards = [int(x)-1 for x in sp[1]]
                    p.skills[int(sp[0])-1].activate(p, cards)
            if i[0] == 'p':
                sp = i[1:].split('s')
                p.deck.play_card(int(sp[0])-1, p.skills[int(sp[1])-1])
            if i[0] == 'm':
                if len(i) == 1:
                    p.display_enemies()
                else:
                    sp = i[1:].split('s')
                    p.enemies[int(sp[0])-1].take_hit(p)
                    p.damage = 0
                    p.range = 1
    if i[0] != 'q':
        p.display(turn)
        print(p.death_message)