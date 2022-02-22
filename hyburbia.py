from random import shuffle
from tkinter import Y
import numpy as np
import os

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
        'Strike': [{'R': 2}, 'Strength', {'damage': 2}],
        'Resist': [{'R': 2}, 'Stamina', {'heal': 2}],
        'Walk': [{'Y': 2}, 'Speed', {'move': 2}],
        'Dodge': [{'Y': 2}, 'Quickness', {'block': 2}],
        'Maneuver': [{'G': 2}, 'Dexterity', {'react': 2}],
        'Aim': [{'G': 2}, 'Perception', {'range': 2}],
        'Focus': [{'B': 2}, 'Intelligence', {'draw': 2}],
        'Plan': [{'B': 2}, 'Cunning', {'keep': 2}],
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
                if e == 'range':
                    player.range += self.effect[e]
                if e == 'move':
                    player.move += self.effect[e]
        self.cards = []
        self.used = True


class Enemy:
    types = {
        'Skate Punk': {'health':3, 'range':1, 'damage':2, 'move':3},
        'Air Soft Punk': {'health':2, 'range':3, 'damage':2, 'move':2}
    }

    def __init__(self, name, pos):
        self.name = name
        self.health = Enemy.types[name]['health']
        self.range = Enemy.types[name]['range']
        self.damage = Enemy.types[name]['damage']
        self.move = Enemy.types[name]['move']
        self.pos = pos
        self.distance = 0

    def take_hit(self, player):
        if player.range >= self.distance:
            self.health -= player.damage
            if self.health <= 0:
                player.enemies.remove(self)
            return True
        return False

    def attack(self, player):
        m = self.move
        while self.range < self.distance and m > 0:
            m -= 1
            x = np.sign(player.pos[1] -  self.pos[1])
            y = np.sign(player.pos[0] - self.pos[0])
            r = ['x', 'y']
            shuffle(r)
            if (r[0] == 'x' and x != 0) or y == 0:
                self.pos[1] += int(x)
            else:
                self.pos[0] += int(y)
            player.set_dist()
        if self.range >= self.distance:
            d = max(self.damage - player.block, 0)
            player.block = max(player.block - self.damage, 0)
            player.take_hit('Wound', d, self)

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
        self.move = 0
        self.pos = [5,5]
        self.death_message = '      You died'
        self.dam_messages = []
        self.skills = [
            Skill('Strike'),
            Skill('Resist'),
            Skill('Walk'),
            Skill('Dodge'),
            Skill('Maneuver'),
            Skill('Aim'),
            Skill('Focus'),           
            Skill('Plan'),   
        ]
        self.enemies = [
            Enemy('Skate Punk', [0, 0]),
            Enemy('Air Soft Punk', [10, 10])
        ]
        self.set_dist()

    def refresh_skills(self):
        for s in self.skills:
            s.cards = []
            s.used = False

    def refresh_stats(self):
        self.range = 1
        self.damage = 0
        self.block = 0
        self.move = 0

    def take_hit(self, type, amount, enemy):
        self.dam_messages.append(f'      {enemy.name} hits you for {amount} wounds')
        for d in range(amount):
            if type == 'Wound':
                self.deck.cards.append(Card('Wound'))
                shuffle(self.deck.cards)

    def go(self, dir, map):
        if self.move == 0:
            return
        if dir == 'w':
            if map[self.pos[0] - 1, self.pos[1]] != '.':
                return
            self.pos[0] -= 1
        if dir == 'a':
            if map[self.pos[0], self.pos[1] - 1] != '.':
                return
            self.pos[1] -= 1
        if dir == 's':
            print(map[self.pos[0] + 1, self.pos[1]])
            if map[self.pos[0] + 1, self.pos[1]] != '.':
                return
            self.pos[0] += 1
        if dir == 'd':
            if map[self.pos[0], self.pos[1] + 1] != '.':
                return
            self.pos[1] += 1
        self.move -= 1

    def set_dist(self):
        for e in self.enemies:
            e.distance = abs(self.pos[0] - e.pos[0]) + abs(self.pos[1] - e.pos[1])

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
                f'Move: {self.enemies[s].move}'
                )

    def display_map(self, map):
        if self.pos[0]+6 > len(map):
            map = np.vstack((map, [['.']*len(map[0])]))
        if self.pos[0]-5 < 0:
            map = np.vstack(([['.']*len(map[0])], map))
            self.pos[0] += 1
            for e in range(len(self.enemies)):
                self.enemies[e].pos[0] += 1
        if self.pos[1]+6 > len(map[0]):
            map = np.hstack((map, np.array(['.']*len(map))[:,np.newaxis]))
        if self.pos[1]-5 < 0:
            map = np.hstack((np.array(['.']*len(map))[:,np.newaxis], map))
            self.pos[1] += 1
            for e in range(len(self.enemies)):
                self.enemies[e].pos[1] += 1
        
        map = np.where(map == 'P', '.', map)
        map[self.pos[0], self.pos[1]] = 'P'
        for e in range(len(self.enemies)):
            map = np.where(map == f'{e + 1}', '.', map)
            map[self.enemies[e].pos[0], self.enemies[e].pos[1]] = f'{e + 1}'

        for el in map[self.pos[0]-5:self.pos[0]+6,self.pos[1]-5:self.pos[1]+6]:
            print(' '*12 + ' '.join(el.astype(str)))
        return map

    def display(self, turn):
        print(
            str(turn) + ' ' * (5-len(str(turn))), 
            f'Hand: {[x.short for x in self.deck.hand]} ', 
            f'Deck: {len(self.deck.cards)} ', 
            f'Discard: {len(self.deck.discard)} ',
            f'Damage: {self.damage} ',
            f'Range: {self.range} ',
            f'Block: {self.block} ',
            f'Move: {self.move} '
            )
        for d in self.dam_messages:
            print(d)
        self.dam_messages = []

    def is_dead(self):
        if len([x for x in self.deck.hand if x.type == 'status']) >= 5:
            return True
        return False


if __name__ == '__main__':
    p = Player()
    map = np.empty([11, 11], str)
    map.fill('.')
    map[1:3, 7:9] = '#'
    turn = 0
    show_skills = False
    show_enemies = False
    i = ''
    while not p.is_dead():
        turn += 1
        if i == 'q':
            break
        p.deck.refresh_hand()
        p.refresh_skills()
        p.refresh_stats()
        while not p.is_dead():
            # os.system('cls')
            map = p.display_map(map)
            print('')
            p.display(turn)
            if show_skills:
                p.display_skills()
                show_skills = False
            if show_enemies:
                p.display_enemies()
                show_enemies = False
            i = input('    Action: ')
            if i in 'qe':
                for e in p.enemies:
                    e.attack(p)
                break
            if i[0] == 'k':
                if len(i) == 1:
                    show_skills = True                  
                else:
                    sp = i[1:].split('c')
                    cards = []
                    if 'c' in i:
                        cards = [int(x)-1 for x in sp[1]]
                    p.skills[int(sp[0])-1].activate(p, cards)
            if i[0] == 'p':
                sp = i[1:].split('k')
                p.deck.play_card(int(sp[0])-1, p.skills[int(sp[1])-1])
            if i[0] == 'm':
                if len(i) == 1:
                    show_enemies = True
                else:
                    sp = i[1:].split('k')
                    if p.enemies[int(sp[0])-1].take_hit(p):
                        p.damage = 0
                        p.range = 1
            if i[0] in 'wasd':
                p.go(i[0], map)
                p.set_dist()
    if i[0] != 'q':
        os.system('cls')
        p.display_map(map)
        print('')
        p.display(turn)
        print(p.death_message)