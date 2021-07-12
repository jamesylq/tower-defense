import os
import pygame
import pickle
import random
import math

from _pickle import UnpicklingError

current_path = os.path.dirname(__file__)
resource_path = os.path.join(current_path, 'resources')

MaxFPS = 0
cheats = True


class Map:
    def __init__(self, path: list, name: str, backgroundColor: (int, int, int), pathColor: (int, int, int)):
        self.name = name
        self.path = path
        self.backgroundColor = backgroundColor
        self.pathColor = pathColor


screen = pygame.display.set_mode((1000, 600))
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()
font = pygame.font.SysFont('Ubuntu Mono', 20)
mediumFont = pygame.font.SysFont('Ubuntu Mono', 30)
largeFont = pygame.font.SysFont('Ubuntu Mono', 75)
pygame.display.set_caption('Tower Defense')

POND = Map([[0, 25], [700, 25], [700, 375], [100, 375], [100, 75], [800, 75]], "Pond", (6, 50, 98), (0, 0, 255))
LAVA_SPIRAL = Map([[300, 225], [575, 225], [575, 325], [125, 325], [125, 125], [675, 125], [675, 425], [25, 425], [25, 0]], "Lava Spiral", (207, 16, 32), (255, 140, 0))
PLAINS = Map([[25, 0], [25, 375], [500, 375], [500, 25], [350, 25], [350, 175], [750, 175], [750, 0]], "Plains", (19, 109, 21), (155, 118, 83))
DESERT = Map([[0, 25], [750, 25], [750, 200], [25, 200], [25, 375], [800, 375]], "Desert", (170, 108, 35), (178, 151, 5))
THE_END = Map([[0, 225], [800, 225]], "The End", (100, 100, 100), (200, 200, 200))
Maps = [POND, LAVA_SPIRAL, PLAINS, DESERT, THE_END]

waves = [
    '00' * 3,
    '00' * 5 + '01' * 3,
    '00' * 3 + '01' * 5 + '02' * 3,
    '00' * 3 + '01' * 5 + '02' * 5 + '03' * 3,
    '03' * 30,
    '02' * 30 + '03' * 30,
    '04' * 30,
    '04' * 15 + '05' * 15,
    '06' * 25,
    '0A',
    '06' * 30,
    '07' * 25,
    '07' * 50,
    '08' * 25,
    '0B',
    '16' * 25,
    '17' * 25,
    '17' * 50,
    '18' * 25,
    '1A',
]

enemyColors = {
    '0': (255, 0, 0),
    '1': (0, 0, 221),
    '2': (0, 255, 0),
    '3': (255, 255, 0),
    '4': (255, 20, 147),
    '5': (68, 68, 68),
    '6': (255, 255, 255),
    '7': (16, 16, 16),
    '8': (110, 38, 14),
    'A': (146, 43, 62),
    'B': (191, 64, 191)
}

damages = {
    '0': 1,
    '1': 2,
    '2': 3,
    '3': 4,
    '4': 5,
    '5': 6,
    '6': 7,
    '7': 8,
    '8': 9,
    'A': 30,
    'B': 69
}

speed = {
    '0': 1,
    '1': 1,
    '2': 2,
    '3': 2,
    '4': 3,
    '5': 4,
    '6': 3,
    '7': 2,
    '8': 2,
    'A': 1,
    'B': 1
}

onlyExplosiveTiers = [7, 8]

trueHP = {
    'A': 1000,
    'B': 1500
}

bossCoins = {
    'A': 150,
    'B': 250
}

defaults = {
    'enemies': [],
    'projectiles': [],
    'piercingProjectiles': [],
    'towers': [],
    'HP': 100,
    'FinalHP': None,
    'coins': 100000 if cheats else 50,
    'selected': None,
    'placing': '',
    'nextWave': 299,
    'wave': 0,
    'win': False,
    'lose': False,
    'MapSelect': True,
    'shopScroll': 0,
    'spawnleft': '',
    'spawndelay': 9,
    'Map': None,
    'totalWaves': len(waves)
}
LOCKED = 'LOCKED'

IceCircle = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'ice_circle.png')), (250, 250))
smallIceCircle = IceCircle.copy()
smallIceCircle.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)

IceCircle = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'ice_circle.png')), (350, 350))
largeIceCircle = IceCircle.copy()
largeIceCircle.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)

SIN45 = COS45 = math.sqrt(2) / 2


class data:
    def __init__(self):
        self.PBs = {Map.name: (LOCKED if Map.name != 'Pond' else None) for Map in Maps}
        for attr, default in defaults.items():
            setattr(self, attr, default)

    def reset(self):
        for attr, default in defaults.items():
            if attr in ['PBs', 'FinalHP', 'totalWaves']:
                continue

            setattr(self, attr, default if type(default) is not list else [])


class Towers:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.timer = 0
        self.upgrades = [0, 0, 0]
        self.stun = 0
        self.hits = 0

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

    def attack(self):
        pass

    def update(self):
        pass


class Turret(Towers):
    name = 'Turret'
    color = (128, 128, 128)
    req = 0
    price = 50

    upgradePrices = [
        [30, 75, 125],
        [20, 60, 275],
        [75, 125, 175]
    ]

    upgradeNames = [
        ['Longer Range', 'Extreme Range', 'Ultra Range'],
        ['More Bullets', 'Bullet Rain', 'Double Bullets'],
        ['Explosive Shots', 'Camo Detection', 'Boss Shred']
    ]

    range = 100
    cooldown = 75

    def __init__(self, x: int, y: int):
        super().__init__(x, y)

    def attack(self):
        if self.stun > 0:
            self.stun -= 1
            return

        if self.timer >= self.cooldown:
            try:
                closest = getTarget(self)
                explosiveRadius = 30 if self.upgrades[2] >= 1 else 0
                info.projectiles.append(Projectile(self, self.x, self.y, closest.x, closest.y, bossDamage= 5 if self.upgrades[2] == 3 else 1, explosiveRadius=explosiveRadius))
                self.timer = 0
            except AttributeError:
                pass
        else:
            self.timer += 1

    def update(self):
        self.range = [100, 130, 165, 200][self.upgrades[0]]
        self.cooldown = [100, 50, 25, 10][self.upgrades[1]]


class IceTower(Towers):
    class SnowStormCircle:
        def __init__(self, parent, x, y):
            self.x = x
            self.y = y
            self.parent = parent
            self.freezeDuration = [100, 150, 150, 199][self.parent.upgrades[2]]
            self.visibleTicks = 0

        def draw(self):
            if self.visibleTicks > 0:
                self.visibleTicks -= 1
                screen.blit(largeIceCircle if self.parent.upgrades[0] >= 1 else smallIceCircle, (self.x - self.parent.range, self.y - self.parent.range))

        def freeze(self):
            self.visibleTicks = 50

            for enemy in info.enemies:
                if abs(enemy.x - self.x) ** 2 + abs(enemy.y - self.y) ** 2 <= self.parent.range ** 2:
                    if type(enemy.tier) is int:
                        enemy.freezeTimer = self.freezeDuration

        def update(self):
            self.freezeDuration = [100, 150, 150, 199][self.parent.upgrades[2]]

    name = 'Ice Tower'
    color = (32, 32, 200)
    req = 2
    price = 30
    upgradePrices = [
        [30, 60, 100],
        [30, 50, 85],
        [30, 50, 75]
    ]
    upgradeNames = [
        ['Longer Range', 'Extreme Range', 'Ultra Range'],
        ['Lesser Cooldown', 'Snowball Shower', 'Heavy Snowfall'],
        ['Longer Freeze', 'Snowstorm Circle', 'Ultra Freeze']
    ]
    range = 125
    cooldown = 100
    freezeDuration = 20

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.snowCircle = self.SnowStormCircle(self, self.x, self.y)

    def draw(self):
        super().draw()
        self.snowCircle.draw()

    def attack(self):
        if self.stun > 0:
            self.stun -= 1
            return

        if self.timer >= self.cooldown:
            if self.upgrades[2] >= 2:
                self.snowCircle.freeze()
                self.timer = 0
            else:
                try:
                    closest = getTarget(self)
                    info.projectiles.append(Projectile(self, self.x, self.y, closest.x, closest.y, freezeDuration=self.freezeDuration))
                    self.timer = 0
                except AttributeError:
                    pass
        else:
            self.timer += 1

    def update(self):
        self.snowCircle.update()

        self.range = [150, 180, 200, 250][self.upgrades[0]]
        self.cooldown = [1, 0.75, 0.55, 0.4][self.upgrades[1]] * (50 if self.upgrades[2] < 2 else 1000)
        if self.upgrades[2] >= 1:
            self.freezeDuration = 45
        if self.upgrades[2] == 3:
            self.freezeDuration = 75


class SpikeTower(Towers):
    class Spike:
        def __init__(self, parent, angle: int):
            self.parent = parent
            self.x = self.parent.x
            self.y = self.parent.y
            self.angle = angle
            self.dx = {0: 0, 45: SIN45, 90: 1, 135: SIN45, 180: 0, 225: -SIN45, 270: -1, 315: -SIN45, 360: 0}[angle]
            self.dy = {0: -1, 45: -COS45, 90: 0, 135: COS45, 180: 1, 225: COS45, 270: 0, 315: -COS45, 360: -1}[angle]
            self.visible = False
            self.ignore = []

        def move(self):
            if not self.visible or (getTarget(self.parent) is None and [self.x, self.y] == [self.parent.x, self.parent.y]):
                return

            self.x += self.dx * self.parent.projectileSpeed
            self.y += self.dy * self.parent.projectileSpeed

            for enemy in info.enemies:
                if enemy in self.ignore or (enemy.tier in onlyExplosiveTiers and self.parent.upgrades[2] < 2):
                    continue

                if abs(enemy.x - self.x) ** 2 + abs(enemy.y - self.y) ** 2 < (144 if type(enemy.tier) is int else 484):
                    self.visible = False
                    if self.parent.upgrades[2] == 3:
                        enemy.fireTicks = 300
                        enemy.fireIgnitedBy = self.parent

                    new = enemy.kill(coinMultiplier=getCoinMultiplier(self.parent))
                    if self.parent.upgrades[2] >= 1 and new is not None:
                        new = new.kill(coinMultiplier=getCoinMultiplier(self.parent))
                    self.ignore.append(new if type(enemy.tier) is int else enemy)
                    self.parent.hits += 1

        def draw(self):
            if not self.visible:
                return

            pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), 2)

    class Spikes:
        def __init__(self, parent):
            self.parent = parent
            self.spikes = []
            for n in range(8):
                self.spikes.append(SpikeTower.Spike(self.parent, n * 45))

        def moveSpikes(self):
            for spike in self.spikes:
                spike.move()

                if abs(spike.x - self.parent.x) ** 2 + abs(spike.y - self.parent.y) ** 2 >= self.parent.range ** 2:
                    spike.visible = False

        def drawSpikes(self):
            for spike in self.spikes:
                spike.draw()

    name = 'Spike Tower'
    color = (224, 17, 95)
    req = 2
    price = 125
    upgradePrices = [
        [50, 100, 150],
        [75, 350, 500],
        [100, 125, 200]
    ]
    upgradeNames = [
        ['Fast Spikes', 'Hyperspeed Spikes', 'Bullet-like Speed'],
        ['Shorter Cooldown', 'Super Reloading', 'No Cooldown'],
        ['Double Damage', 'Lead-pierce', 'Burning Spikes']
    ]
    range = 50
    projectileSpeed = 1
    cooldown = 100

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.spikes = SpikeTower.Spikes(self)

    def draw(self):
        self.spikes.drawSpikes()
        super().draw()

    def attack(self):
        if self.stun > 0:
            self.stun -= 1
            return

        if True in [s.visible for s in self.spikes.spikes]:
            self.spikes.moveSpikes()
        elif self.timer >= self.cooldown:
            for spike in self.spikes.spikes:
                spike.visible = True
                spike.x = self.x
                spike.y = self.y
                spike.ignore = []
            self.timer = 0
        else:
            self.timer += 1

    def update(self):
        self.projectileSpeed = [1, 1.5, 2.2, 3][self.upgrades[0]]
        self.cooldown = [100, 50, 25, 0][self.upgrades[1]]


class BombTower(Towers):
    name = 'Bomb Tower'
    color = (0, 0, 0)
    req = 4
    price = 100
    upgradePrices = [
        [30, 50, 75],
        [20, 35, 50],
        [75, 100, 125]
    ]
    upgradeNames = [
        ['Longer Range', 'Extra Range', 'Ultra Range'],
        ['More Bombs', 'Heavy Fire', 'Twin-Fire'],
        ['Larger Explosions', 'Burning Bombs', '2x Impact Damage']
    ]
    range = 50
    cooldown = 200

    def __init__(self, x: int, y: int):
        super().__init__(x, y)

    def attack(self):
        if self.stun > 0:
            self.stun -= 1
            return

        if self.timer >= self.cooldown:
            try:
                explosionRadius = 60 if self.upgrades[2] >= 1 else 30
                closest = getTarget(self)
                info.projectiles.append(Projectile(self, self.x, self.y, closest.x, closest.y, explosiveRadius=explosionRadius))
                if self.upgrades[2] == 3:
                    twin = Projectile(self, self.x, self.y, closest.x, closest.y, explosiveRadius=explosionRadius)
                    for n in range(5):
                        twin.move()
                    info.projectiles.append(twin)
                self.timer = 0
            except AttributeError:
                pass
        else:
            self.timer += 1

    def update(self):
        self.range = [50, 100, 150, 200][self.upgrades[0]]
        self.cooldown = [200, 145, 75, 75][self.upgrades[1]]


class BananaFarm(Towers):
    name = 'Banana Farm'
    color = (255, 255, 0)
    req = 4
    price = 150
    upgradePrices = [
        [30, 50, 65],
        [30, 45, 60],
        [40, 75, 115]
    ]
    upgradeNames = [
        ['Banana Cannon', 'More Banana Shots', 'Super Range'],
        ['Increased Income', 'Money Farm', 'Money Factory'],
        ['Double Coin Drop', '5x Coin Drop', '10x Coin Drop']
    ]
    range = 100
    cooldown = 0

    def __init__(self, x: int, y: int):
        super().__init__(x, y)

    def attack(self):
        if self.stun > 0:
            self.stun -= 1
            return

        if self.upgrades[0] >= 1:
            if self.timer >= self.cooldown:
                try:
                    closest = getTarget(self)
                    info.projectiles.append(Projectile(self, self.x, self.y, closest.x, closest.y))
                    self.timer = 0
                except AttributeError:
                    pass
            else:
                self.timer += 1

    def update(self):
        self.cooldown = [0, 50, 25, 25][self.upgrades[0]]
        if self.upgrades[0] == 3:
            self.range = 150


class Bowler(Towers):
    name = 'Bowler'
    color = (32, 32, 32)
    req = 5
    price = 175
    upgradePrices = [
        [20, 40, 60],
        [20, 50, 100],
        [50, 100, 175]
    ]
    upgradeNames = [
        ['Faster Rocks', 'Double Damage', 'Snipe'],
        ['More Rocks', 'Double Rocks', 'Infini-Rocks'],
        ['5 Enemies Pierce', '10 Enemies Pierce', '20 Enemies Pierce']
    ]
    range = 0
    cooldown = 300
    pierce = 3

    def __init__(self, x: int, y: int):
        super().__init__(x, y)

    def attack(self):
        if self.stun > 0:
            self.stun -= 1
            return

        if self.timer >= self.cooldown:
            try:
                for direction in ['left', 'right', 'up', 'down']:
                    info.piercingProjectiles.append(PiercingProjectile(self, self.x, self.y, self.pierce, direction))
                self.timer = 0
            except AttributeError:
                pass
        else:
            self.timer += 1

    def update(self):
        self.cooldown = [300, 200, 150, 100][self.upgrades[1]]
        self.pierce = [3, 5, 10, 20][self.upgrades[2]]


class Wizard(Towers):
    class LightningBolt:
        def __init__(self, parent):
            self.parent = parent
            self.pos = [self.parent.x, self.parent.y]
            self.t1 = None
            self.t2 = None
            self.t3 = None
            self.t4 = None
            self.t5 = None
            self.visibleTicks = 0

        def attack(self):
            self.visibleTicks = 50
            self.t1 = getTarget(Towers(self.pos[0], self.pos[1]), overrideRange=1000)
            if type(self.t1) is Enemy:
                self.t1.kill(coinMultiplier=getCoinMultiplier(self.parent))
                self.parent.hits += 1
                self.t2 = getTarget(Towers(self.t1.x, self.t1.y), ignore=[self.t1], overrideRange=1000)
                if type(self.t2) is Enemy:
                    self.t2.kill(coinMultiplier=getCoinMultiplier(self.parent))
                    self.parent.hits += 1
                    self.t3 = getTarget(Towers(self.t2.x, self.t2.y), ignore=[self.t1, self.t2], overrideRange=1000)
                    if type(self.t3) is Enemy:
                        self.t3.kill(coinMultiplier=getCoinMultiplier(self.parent))
                        self.parent.hits += 1
                        if self.parent.upgrades[1] == 3:
                            self.t4 = getTarget(Towers(self.t3.x, self.t3.y), ignore=[self.t1, self.t2, self.t3], overrideRange=1000)
                            if type(self.t4) is Enemy:
                                self.t4.kill(coinMultiplier=getCoinMultiplier(self.parent))
                                self.parent.hits += 1
                                self.t5 = getTarget(Towers(self.t4.x, self.t4.y), ignore=[self.t1, self.t2, self.t3, self.t4], overrideRange=1000)
                                if type(self.t5) is Enemy:
                                    self.t5.kill(coinMultiplier=getCoinMultiplier(self.parent))
                            else:
                                self.t5 = None
                        else:
                            self.t4 = None
                            self.t5 = None
                    else:
                        self.t4 = None
                        self.t5 = None
                else:
                    self.t3 = None
                    self.t4 = None
                    self.t5 = None
            else:
                self.t2 = None
                self.t3 = None
                self.t4 = None
                self.t5 = None

            if self.t1 is None:
                self.parent.lightningTimer = 500
            else:
                self.parent.lightningTimer = 0

        def draw(self):
            if self.visibleTicks > 0:
                self.visibleTicks -= 1

                if self.t1 is not None:
                    pygame.draw.line(screen, (191, 0, 255), self.pos, [self.t1.x, self.t1.y], 3)
                    if self.t2 is not None:
                        pygame.draw.line(screen, (191, 0, 255), [self.t1.x, self.t1.y], [self.t2.x, self.t2.y], 3)
                        if self.t3 is not None:
                            pygame.draw.line(screen, (191, 0, 255), [self.t2.x, self.t2.y], [self.t3.x, self.t3.y], 3)
                            if self.t4 is not None:
                                pygame.draw.line(screen, (191, 0, 255), [self.t3.x, self.t3.y], [self.t4.x, self.t4.y], 3)
                                if self.t5 is not None:
                                    pygame.draw.line(screen, (191, 0, 255), [self.t4.x, self.t4.y], [self.t5.x, self.t5.y], 3)

    name = 'Wizard'
    color = (128, 0, 128)
    req = 7
    price = 250
    upgradePrices = [
        [30, 60, 90],
        [75, 95, 150],
        [50, 65, 90]
    ]
    upgradeNames = [
        ['Longer Range', 'Extreme Range', 'Ultra Range'],
        ['Lighning Zap', 'Wisdom of Camo', '5-hit Lightning'],
        ['Big Blast Radius', 'Faster Reload', 'Hyper Reload']
    ]
    range = 125
    cooldown = 100

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.lightning = self.LightningBolt(self)
        self.lightningTimer = 0

    def draw(self):
        super().draw()
        self.lightning.draw()

    def attack(self):
        if self.stun > 0:
            self.stun -= 1
            return

        if self.timer >= self.cooldown:
            try:
                closest = getTarget(self)
                info.projectiles.append(Projectile(self, self.x, self.y, closest.x, closest.y, explosiveRadius=60 if self.upgrades[2] else 30))
                self.timer = 0
            except AttributeError:
                pass
        else:
            self.timer += 1

        if self.lightningTimer >= 500:
            self.lightning.attack()
        elif self.upgrades[1]:
            self.lightningTimer += 1

    def update(self):
        self.range = [125, 150, 175, 200][self.upgrades[0]]
        self.cooldown = [50, 50, 33, 16][self.upgrades[2]]


class InfernoTower(Towers):
    class AttackRender:
        def __init__(self, parent, target):
            self.parent = parent
            self.target = target
            self.visibleTicks = 50

        def draw(self):
            pygame.draw.line(screen, (255, 69, 0), (self.parent.x, self.parent.y), (self.target.x, self.target.y), 2)
            self.visibleTicks -= 1
            if self.visibleTicks == 0:
                self.parent.inferno.renders.remove(self)

    class Inferno:
        def __init__(self, parent):
            self.parent = parent
            self.renders = []

        def attack(self):
            found = False
            for enemy in info.enemies:
                if (abs(enemy.x - self.parent.x) ** 2 + abs(enemy.y - self.parent.y) ** 2 <= self.parent.range ** 2) and (not enemy.camo or canSeeCamo(self.parent)):
                    enemy.fireTicks = (500 if self.parent.upgrades[2] else 300)
                    enemy.fireIgnitedBy = self.parent
                    enemy.freezeTimer = [0, 0, 25, 75][self.parent.upgrades[1]]
                    self.renders.append(InfernoTower.AttackRender(self.parent, enemy))
                    found = True

            if not found:
                self.parent.timer = 500

        def draw(self):
            for render in self.renders:
                render.draw()

    name = 'Inferno'
    color = (255, 69, 0)
    req = 8
    price = 500
    upgradePrices = [
        [100, 200, 350],
        [120, 175, 250],
        [150, 200, 275]
    ]
    upgradeNames = [
        ['Longer Range', 'Extreme Range', 'Ultra Range'],
        ['Shortened Cooldown', 'More Infernoes', 'Hyper Infernoes'],
        ['Longer Burning', 'Firey Stun', 'Longer Stun']
    ]
    range = 100
    cooldown = 500

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.inferno = self.Inferno(self)

    def draw(self):
        super().draw()
        self.inferno.draw()

    def attack(self):
        if self.stun > 0:
            self.stun -= 1
            return

        if self.timer >= self.cooldown:
            self.inferno.attack()
            self.timer = 0
        else:
            self.timer += 1

    def update(self):
        self.range = [100, 150, 250, 400][self.upgrades[0]]
        self.cooldown = [500, 375, 250, 200][self.upgrades[1]]


class Village(Towers):
    class Villager:
        def __init__(self, parent):
            self.parent = parent
            self.x = self.parent.x
            self.y = self.parent.y
            self.tx = None
            self.ty = None
            self.dx = None
            self.dy = None
            self.target = None
            self.moveCooldown = 250
            self.timer = 0

        def attack(self):
            closest = getTarget(Towers(self.x, self.y), overrideRange=self.parent.range)
            if closest is None:
                self.parent.timer = 100
            else:
                info.projectiles.append(Projectile(self.parent, self.x, self.y, closest.x, closest.y))

        def draw(self):
            pygame.draw.circle(screen, (184, 134, 69), (self.x, self.y), 10)

        def move(self):
            try:
                pygame.display.update()
            except:
                pass

            if self.dx is None:
                if self.tx is None:
                    if self.moveCooldown >= 250:
                        closest = getTarget(Towers(self.x, self.y), overrideRange=self.parent.range, ignore=self.parent.targets)
                        if closest is None:
                            self.tx = self.parent.x
                            self.ty = self.parent.y
                        else:
                            self.tx = closest.x
                            self.ty = closest.y
                            self.target = closest
                            self.moveCooldown = 0
                            self.parent.targets = [villager.target for villager in self.parent.villagers]
                    elif getTarget(Towers(self.x, self.y), overrideRange=self.parent.range) is None or (self.x - self.parent.x) ** 2 + (self.y - self.parent.y) ** 2 < 625:
                        self.moveCooldown += 1
                else:
                    dx, dy = abs(self.x - self.tx), abs(self.y - self.ty)
                    try:
                        self.dx = abs(dx / (dx + dy)) * (-1 if self.tx < self.x else 1) * 2
                        self.dy = abs(dy / (dx + dy)) * (-1 if self.ty < self.y else 1) * 2
                    except ZeroDivisionError:
                        self.dx = None
                        self.dy = None
                        self.tx = None
                        self.ty = None
                        self.target = None
                    else:
                        self.x += self.dx
                        self.y += self.dy
            else:
                self.x += self.dx
                self.y += self.dy

                if abs(self.x - self.tx) ** 2 + abs(self.y - self.ty) ** 2 < 100:
                    self.dx = None
                    self.dy = None
                    self.tx = None
                    self.ty = None
                    self.target = None
                    self.moveCooldown = 0

    name = 'Village'
    color = (202, 164, 114)
    req = 10
    price = 400
    upgradePrices = [
        [120, 150, 200],
        [100, 125, 175],
        [50, 75, 100]
    ]
    upgradeNames = [
        ['Anti-Camo', 'Powerful Villagers', 'Turret Villagers'],
        ['Longer Range', 'Extreme Range', 'Ultra Range'],
        ['Two Villagers', 'Three Villagers', 'Four Villagers']
    ]
    range = 100
    cooldown = 100

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.villagers = [self.Villager(self)]
        self.targets = []

    def draw(self):
        super().draw()
        for villager in self.villagers:
            villager.draw()

    def attack(self):
        for villager in self.villagers:
            if villager.timer >= self.cooldown:
                villager.attack()
                villager.timer = 0
            else:
                villager.timer += 1

    def update(self):
        self.cooldown = [50, 50, 40, 27][self.upgrades[0]]
        self.range = [100, 125, 150, 175][self.upgrades[1]]
        self.targets = [villager.target for villager in self.villagers]

        for villager in self.villagers:
            villager.move()

        if len(self.villagers) < self.upgrades[2]:
            self.villagers.append(self.Villager(self))


class Projectile:
    def __init__(self, parent: Towers, x: int, y: int, tx: int, ty: int, *, explosiveRadius: int = 0, freezeDuration: int = 0, bossDamage: int = 1, impactDamage: int = 1, fireTicks: int = 0):
        self.parent = parent
        self.x = x
        self.y = y
        self.tx = tx
        self.ty = ty
        self.dx = None
        self.dy = None
        self.explosiveRadius = explosiveRadius
        self.freezeDuration = freezeDuration
        self.coinMultiplier = getCoinMultiplier(parent)
        self.bossDamage = bossDamage
        self.impactDamage = impactDamage
        self.fireTicks = fireTicks

        if self.explosiveRadius > 0:
            self.color = (0, 0, 0)
        elif self.freezeDuration > 0:
            self.color = (0, 0, 187)
        elif self.coinMultiplier > 1:
            self.color = (255, 255, 0)
        else:
            self.color = (187, 187, 187)

    def move(self):
        try:
            if self.dx is None:
                dx, dy = self.x - self.tx, self.y - self.ty
                self.dx = abs(dx / (dx + dy)) * (-1 if self.tx < self.x else 1) * 5
                self.dy = abs(dy / (dx + dy)) * (-1 if self.ty < self.y else 1) * 5

                self.x += self.dx
                self.y += self.dy
            else:
                self.x += self.dx
                self.y += self.dy

            if self.x < 0 or self.x > 800 or self.y < 0 or self.y > 450:
                raise ZeroDivisionError

        except ZeroDivisionError:
            info.projectiles.remove(self)

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 3)

    def explode(self, centre):
        for enemy in info.enemies:
            if enemy == centre:
                continue

            if abs(enemy.x - self.x) ** 2 + abs(enemy.y - self.y) ** 2 < self.explosiveRadius ** 2:
                if self.fireTicks > 0:
                    enemy.fireTicks = self.fireTicks
                    enemy.fireIgnitedBy = self.parent
                enemy.kill(coinMultiplier=getCoinMultiplier(self.parent))
                self.parent.hits += 1


class PiercingProjectile:
    def __init__(self, parent: Towers, x: int, y: int, pierceLimit: int, direction: str, *, speed: int = 2):
        self.parent = parent
        self.coinMultiplier = getCoinMultiplier(self.parent)
        self.x = x
        self.y = y
        self.pierce = pierceLimit
        self.direction = direction
        self.ignore = []
        self.movement = 0
        self.speed = speed

    def move(self):
        self.movement += self.speed

        if self.direction == 'left':
            self.x -= self.speed
        elif self.direction == 'right':
            self.x += self.speed
        elif self.direction == 'up':
            self.y -= self.speed
        elif self.direction == 'down':
            self.y += self.speed

        if self.x < 0 or self.x > 800 or self.y < 0 or self.y > 450:
            info.piercingProjectiles.remove(self)

    def draw(self):
        pygame.draw.circle(screen, (16, 16, 16), (self.x, self.y), 5)


class Enemy:
    def __init__(self, camo: bool, tier: str or int, spawn: [int, int], lineIndex: int):
        try:
            self.tier = int(tier)
        except ValueError:
            self.tier = tier

        self.x, self.y = spawn
        self.lineIndex = lineIndex
        self.totalMovement = 0
        self.freezeTimer = 0
        if self.tier in trueHP.keys():
            self.HP = self.MaxHP = trueHP[self.tier]
        else:
            self.HP = self.MaxHP = 1
        self.fireTicks = 0
        self.fireIgnitedBy = None
        self.timer = 0
        self.camo = camo

    def move(self):
        if self.timer > 0:
            self.timer -= 1
        elif self.tier == 'B':
            self.timer = 250
            info.enemies.append(Enemy(False, 3, [self.x, self.y], self.lineIndex))

        if self.freezeTimer > 0:
            self.freezeTimer -= 1
        else:
            if len(info.Map.path) - 1 == self.lineIndex:
                self.kill(spawnNew=False, ignoreBoss=True)
                info.HP -= damages[str(self.tier)]
            else:
                current = info.Map.path[self.lineIndex]
                new = info.Map.path[self.lineIndex + 1]

                if current[0] < new[0]:
                    self.x += 1
                    if self.x >= new[0]:
                        self.lineIndex += 1
                elif current[0] > new[0]:
                    self.x -= 1
                    if self.x <= new[0]:
                        self.lineIndex += 1
                elif current[1] < new[1]:
                    self.y += 1
                    if self.y >= new[1]:
                        self.lineIndex += 1
                elif current[1] > new[1]:
                    self.y -= 1
                    if self.y <= new[1]:
                        self.lineIndex += 1
                else:
                    self.kill(spawnNew=False, ignoreBoss=True)

                self.totalMovement += 1

            try:
                self.freezeTimer = max({'A': 5, 'B': 8}[self.tier], self.freezeTimer)
            except KeyError:
                pass

    def update(self):
        if self.fireTicks > 0:
            if self.fireTicks % 100 == 0:
                new = self.kill(burn=True)
                self.fireIgnitedBy.hits += 1
                if new is not None:
                    new.fireTicks -= 1
                else:
                    self.fireTicks -= 1
            else:
                self.fireTicks -= 1

        for projectile in info.projectiles:
            if abs(self.x - projectile.x) ** 2 + abs(self.y - projectile.y) ** 2 < (625 if type(self.tier) is str else 100):
                if projectile.freezeDuration > 0:
                    info.projectiles.remove(projectile)
                    self.freezeTimer = max(self.freezeTimer, projectile.freezeDuration // (2 if type(self.tier) is str else 1))
                else:
                    info.projectiles.remove(projectile)
                    if projectile.explosiveRadius > 0:
                        projectile.explode(self)
                        if self.tier in onlyExplosiveTiers:
                            new = self
                            for n in range(projectile.impactDamage):
                                new = new.kill(coinMultiplier=projectile.coinMultiplier, bossDamage=projectile.bossDamage)
                                projectile.parent.hits += 1
                    if self.tier not in onlyExplosiveTiers:
                        new = self
                        for n in range(projectile.impactDamage):
                            new = new.kill(coinMultiplier=projectile.coinMultiplier, bossDamage=projectile.bossDamage)
                            projectile.parent.hits += 1

                            if new is None:
                                break

        if self.tier not in onlyExplosiveTiers:
            for projectile in info.piercingProjectiles:
                if abs(self.x - projectile.x) ** 2 + abs(self.y - projectile.y) ** 2 < 100:
                    if (self not in projectile.ignore) and (not self.camo):
                        damage = 1
                        if type(projectile.parent) is Bowler:
                            if projectile.parent.upgrades[0] == 2:
                                damage = 2
                            elif projectile.parent.upgrades[0] == 3:
                                damage = 2 * (projectile.movement // 100 + 1)

                        new = self
                        for n in range(damage):
                            new = new.kill(coinMultiplier=projectile.coinMultiplier)
                            projectile.parent.hits += 1

                            if new is None:
                                break

                        projectile.ignore.append(new)

                        if projectile.pierce <= 1:
                            info.piercingProjectiles.remove(projectile)
                        else:
                            projectile.pierce -= 1

    def draw(self):
        if type(self.tier) is str:
            if self.HP > 800:
                color = (191, 255, 0)
            elif self.HP > 600:
                color = (196, 211, 0)
            elif self.HP > 400:
                color = (255, 255, 0)
            elif self.HP > 200:
                color = (255, 69, 0)
            else:
                color = (255, 0, 0)

            pygame.draw.rect(screen, (128, 128, 128), (self.x - 50, self.y - 25, 100, 5))
            pygame.draw.rect(screen, (0, 0, 0), (self.x - 50, self.y - 25, 100, 5), 1)
            pygame.draw.rect(screen, color, (self.x - 50, self.y - 25, round(self.HP / self.MaxHP * 100), 5))

        pygame.draw.circle(screen, enemyColors[str(self.tier)], (self.x, self.y), 20 if type(self.tier) is str else 10)
        if self.camo:
            pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), 20 if type(self.tier) is str else 10, 2)

    def kill(self, *, spawnNew: bool = True, coinMultiplier: int = 1, ignoreBoss: bool = False, burn: bool = False, bossDamage: int = 1):
        if type(self.tier) is int or ignoreBoss:
            try:
                info.enemies.remove(self)
            except ValueError:
                pass

            if spawnNew:
                if self.tier == 0:
                    info.coins += 3 * coinMultiplier
                elif self.tier in bossCoins.keys():
                    info.coins += bossCoins[self.tier]
                else:
                    new = Enemy(self.camo, self.tier - 1, (self.x, self.y), self.lineIndex)
                    new.fireTicks = self.fireTicks
                    new.fireIgnitedBy = self.fireIgnitedBy
                    info.enemies.append(new)
                    return new
        elif type(self.tier) is str:
            self.HP -= 10 if burn else bossDamage
            if self.HP <= 0:
                self.kill(spawnNew=spawnNew, coinMultiplier=coinMultiplier, ignoreBoss=True)
                try:
                    self.fireIgnitedBy.hits += 1
                except AttributeError:
                    pass


def getSellPrice(tower: Towers) -> float:
    price = tower.price
    for n in range(3):
        for m in range(tower.upgrades[n]):
            price += tower.upgradePrices[n][m]

    return price * 0.5


def centredBlit(font: pygame.font.Font, text: str, color: (int, int, int), pos: (int, int)):
    textObj = font.render(text, True, color)
    screen.blit(textObj, textObj.get_rect(center=pos))


def income() -> float:
    total = 0.001
    for tower in info.towers:
        if type(tower) is BananaFarm:
            total += [0.001, 0.003, 0.0075, 0.015][tower.upgrades[1]]

    return total


def getCoinMultiplier(Tower: Towers) -> int:
    bananaFarms = [tower for tower in info.towers if type(tower) is BananaFarm]
    maxCoinMult = 1
    for bananaFarm in bananaFarms:
        if abs(Tower.x - bananaFarm.x) ** 2 + abs(Tower.y - bananaFarm.y) ** 2 < bananaFarm.range ** 2:
            maxCoinMult = max(maxCoinMult, [1, 2, 5, 10][bananaFarm.upgrades[2]])

    return maxCoinMult


def canSeeCamo(Tower: Towers) -> bool:
    if type(Tower) is Turret and Tower.upgrades[2] >= 2:
        return True

    if type(Tower) is Wizard and Tower.upgrades[1] >= 2:
        return True

    villages = [tower for tower in info.towers if type(tower) is Village and tower.upgrades[0] > 0]
    for village in villages:
        if abs(Tower.x - village.x) ** 2 + abs(Tower.y - village.y) ** 2 < village.range ** 2:
            return True
    return False


def getTarget(tower: Towers, *, ignore: [Enemy] = None, overrideRange: int = None) -> Enemy:
    if ignore is None:
        ignore = []

    if overrideRange is None:
        rangeRadius = tower.range
    else:
        rangeRadius = overrideRange

    maxDistance = None

    for enemy in info.enemies:
        if (abs(enemy.x - tower.x) ** 2 + abs(enemy.y - tower.y) ** 2 <= rangeRadius ** 2) and (enemy not in ignore):
            if (enemy.camo and canSeeCamo(tower)) or not enemy.camo:
                try:
                    if enemy.totalMovement > maxDistance:
                        maxDistance = enemy.totalMovement
                except TypeError:
                    maxDistance = enemy.totalMovement

    if maxDistance is not None:
        for enemy in info.enemies:
            if enemy.totalMovement == maxDistance:
                return enemy


def draw():
    mx, my = pygame.mouse.get_pos()

    screen.fill(info.Map.backgroundColor)

    for i in range(len(info.Map.path) - 1):
        pygame.draw.line(screen, info.Map.pathColor, info.Map.path[i], info.Map.path[i + 1], 10)
    pygame.draw.circle(screen, info.Map.pathColor, info.Map.path[0], 10)

    for tower in info.towers:
        tower.draw()

    for enemy in info.enemies:
        enemy.draw()

    for projectile in info.projectiles:
        projectile.draw()

    for projectile in info.piercingProjectiles:
        projectile.draw()

    if info.selected is not None:
        original = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'range.png')), (info.selected.range * 2, info.selected.range * 2))
        modified = original.copy()
        modified.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
        screen.blit(modified, (info.selected.x - info.selected.range, info.selected.y - info.selected.range))

    if info.placing != '':
        screen.blit(font.render(f'Click anywhere on the map to place the {info.placing}!', True, 0), (250, 400))
        if 0 <= mx <= 800 and 0 <= my <= 450:
            classObj = None
            for tower in Towers.__subclasses__():
                if tower.name == info.placing:
                    classObj = tower

            pygame.draw.circle(screen, classObj.color, (mx, my), 15)
            original = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'range.png')), (classObj.range * 2, classObj.range * 2))
            modified = original.copy()
            modified.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
            screen.blit(modified, (mx - classObj.range, my - classObj.range))

    pygame.draw.rect(screen, (221, 221, 221), (800, 0, 200, 450))

    n = 0
    for towerType in Towers.__subclasses__():
        if info.wave >= towerType.req or cheats:
            screen.blit(font.render(f'{towerType.name} (${towerType.price})', True, 0), (810, 10 + 80 * n + info.shopScroll))
            pygame.draw.rect(screen, (187, 187, 187), (945, 30 + 80 * n + info.shopScroll, 42, 42))
            pygame.draw.circle(screen, towerType.color, (966, 51 + 80 * n + info.shopScroll), 15)
            pygame.draw.line(screen, 0, (800, 80 + 80 * n + info.shopScroll), (1000, 80 + 80 * n + info.shopScroll), 3)
            pygame.draw.line(screen, 0, (800, 80 * n + info.shopScroll), (1000, 80 * n + info.shopScroll), 3)
            pygame.draw.rect(screen, (136, 136, 136), (810, 40 + 80 * n + info.shopScroll, 100, 30))
            screen.blit(font.render('Buy New', True, 0), (820, 42 + 80 * n + info.shopScroll))
        n += 1

    pygame.draw.rect(screen, (170, 170, 170), (0, 450, 1000, 150))

    screen.blit(font.render(f'Health: {info.HP} HP', True, 0), (10, 545))
    screen.blit(font.render(f'Coins: {math.floor(info.coins)}', True, 0), (10, 570))
    screen.blit(font.render(f'FPS: {round(clock.get_fps(), 1)}', True, (0, 0, 0)), (10, 520))
    screen.blit(font.render(f'Wave {max(info.wave, 1)}', True, 0), (900, 570))

    pygame.draw.rect(screen, (128, 128, 128), (775, 500, 200, 30))
    screen.blit(font.render('Map Selection', True, (0, 0, 0)), (800, 505))

    if issubclass(type(info.selected), Towers):
        screen.blit(font.render('Upgrades:', True, 0), (200, 487))
        screen.blit(font.render(f'Pops: {info.selected.hits}', True, 0), (200, 460))

        for n in range(3):
            if info.selected.upgrades[n] == 3:
                pygame.draw.rect(screen, (255, 255, 191), (295, 485 + 30 * n, 300, 30))
                pygame.draw.rect(screen, (128, 128, 128), (295, 485 + 30 * n, 300, 30), 5)
                centredBlit(font, 'MAX', (0, 0, 0), (445, 500 + 30 * n))
            else:
                pygame.draw.rect(screen, (128, 128, 128), (295, 485 + 30 * n, 300, 30), 5)

                nameWithSpace = ''
                for m in range(18):
                    nameWithSpace += info.selected.upgradeNames[n][info.selected.upgrades[n]][m] if m < len(info.selected.upgradeNames[n][info.selected.upgrades[n]]) else ' '

                screen.blit(font.render(f'{nameWithSpace} [${info.selected.upgradePrices[n][info.selected.upgrades[n]]}]', True, (32, 32, 32)), (300, 485 + n * 30))

        pygame.draw.rect(screen, (128, 128, 128), (620, 545, 200, 25))
        pygame.draw.rect(screen, (200, 200, 200) if 620 < mx < 820 and 545 < my < 570 else (0, 0, 0), (620, 545, 200, 25), 3)
        screen.blit(font.render(f'Sell for [${round(getSellPrice(info.selected))}]', True, 0), (625, 545))

    pygame.display.update()


def move():
    for enemy in info.enemies:
        for i in range(speed[str(enemy.tier)]):
            enemy.move()
            enemy.update()

    for tower in info.towers:
        tower.update()
        tower.attack()

    for projectile in info.projectiles:
        projectile.move()

    for projectile in info.piercingProjectiles:
        projectile.move()


def iterate():
    if info.spawndelay == 0 and len(info.spawnleft) > 0:
        if type(info.spawnleft[1]) is str:
            info.enemies.append(Enemy(True if info.spawnleft[0] == '1' else False, info.spawnleft[1], info.Map.path[0], 0))
        else:
            info.enemies.append(Enemy(True if info.spawnleft[0] == '1' else False, int(info.spawnleft[1]), info.Map.path[0], 0))
        info.spawnleft = info.spawnleft[2:]
        info.spawndelay = 20
    else:
        info.spawndelay -= 1

    if len(info.enemies) == 0:
        if info.nextWave <= 0:
            try:
                info.spawnleft = waves[info.wave]
            except IndexError:
                info.win = True
            info.spawndelay = 20
            info.nextWave = 300
        else:
            if info.nextWave == 279 and info.wave > 0:
                info.coins += 100

            if info.nextWave == 300:
                info.wave += 1
            info.nextWave -= 1

    mx, my = pygame.mouse.get_pos()

    clock.tick(MaxFPS)
    info.coins += income()

    draw()
    move()

    if info.HP <= 0:
        info.lose = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save()
            quit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if mx <= 800 and my <= 450:
                    for towerType in Towers.__subclasses__():
                        if towerType.name == info.placing:
                            info.placing = ''
                            info.towers.append(towerType(mx, my))
                            return

                    for tower in info.towers:
                        if abs(tower.x - mx) ** 2 + abs(tower.y - my) ** 2 <= 225:
                            info.selected = tower
                            return
                    info.selected = None

                if 810 <= mx <= 910:
                    n = 0
                    for tower in Towers.__subclasses__():
                        if 40 + n * 80 + info.shopScroll <= my <= 70 + n * 80 + info.shopScroll <= 450 and info.coins >= tower.price and info.placing == '' and (info.wave >= tower.req or cheats):
                            info.coins -= tower.price
                            info.placing = tower.name
                            info.selected = None
                        n += 1

                if 775 <= mx <= 975 and 500 <= my <= 530:
                    info.reset()

                if issubclass(type(info.selected), Towers):
                    if 295 <= mx <= 595 and 485 <= my <= 570:
                        n = (my - 485) // 30
                        if info.selected.upgrades[n] < 3:
                            cost = type(info.selected).upgradePrices[n][info.selected.upgrades[n]]
                            if info.coins >= cost and (info.wave >= info.selected.req or cheats):
                                info.coins -= cost
                                info.selected.upgrades[n] += 1

                    elif 620 <= mx < 820 and 545 <= my < 570:
                        info.towers.remove(info.selected)
                        info.coins += getSellPrice(info.selected)
                        info.selected = None

            elif event.button == 4:
                if mx > 800 and my < 450:
                    info.shopScroll = min(0, info.shopScroll + 10)

            elif event.button == 5:
                if mx > 800 and my < 450:
                    maxScroll = len([tower for tower in Towers.__subclasses__() if (info.wave >= tower.req or cheats)]) * 80 - 450
                    if maxScroll > 0:
                        info.shopScroll = max(-maxScroll, info.shopScroll - 10)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                d = info.__dict__.copy()
                d['towers'] = [t.__dict__.copy() for t in d['towers']]
                d['enemies'] = [e.__dict__.copy() for e in d['enemies']]
                d['projectiles'] = [p.__dict__.copy() for p in d['projectiles']]
                d['piercingProjectiles'] = [p.__dict__.copy() for p in d['piercingProjectiles']]
                for n in range(len(d['towers'])):
                    if type(d['towers'][n]) is Village:
                        d['towers'][n]['villager'] = d['towers'][n].villager.__dict__.copy()
                    elif type(d['towers'][n]) is InfernoTower:
                        d['towers'][n]['inferno'] = d['towers'][n].inferno.__dict__.copy()
                        d['towers'][n]['inferno']['renders'] = [render.__dict__.copy() for render in d['towers'][n]['inferno']['renders']]
                    elif type(d['towers'][n]) is IceTower:
                        d['towers'][n]['snowCircle'] = d['towers'][n].snowCircle.__dict__.copy()
                    elif type(d['towers'][n]) is SpikeTower:
                        d['towers'][n]['spikes'] = d['towers'][n].spikes.__dict__.copy()
                        d['towers'][n]['spikes']['spikes'] = [spike.__dict__.copy() for spike in d['towers'][n]['spikes']['spikes']]
                    elif type(d['towers'][n]) is Wizard:
                        d['towers'][n]['lightning'] = d['towers'][n].lightning.__dict__.copy()

                print(str(d) + '\n')

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_UP]:
        info.shopScroll = min(0, info.shopScroll + 10)

    elif pressed[pygame.K_DOWN]:
        maxScroll = len([tower for tower in Towers.__subclasses__() if (info.wave >= tower.req or cheats)]) * 80 - 450
        if maxScroll > 0:
            info.shopScroll = max(-maxScroll, info.shopScroll - 10)


def save():
    pickle.dump(info, open('save.txt', 'wb'))


def load():
    global info

    try:
        info = pickle.load(open('save.txt', 'rb'))

        for attr, default in defaults.items():
            if not hasattr(info, attr):
                setattr(info, attr, default)

        for Map in Maps:
            if Map.name not in info.PBs.keys():
                info.PBs[Map.name] = None

        if info.totalWaves != len(waves):
            info.totalWaves = len(waves)
            if info.totalWaves < len(waves):
                for name, PB in info.PBs.items():
                    if type(PB) is int:
                        info.PBs[name] = None

    except FileNotFoundError:
        open('save.txt', 'w')
    except (EOFError, ValueError, UnpicklingError):
        pass


def app():
    load()

    if info.Map is not None:
        cont = False

        while True:
            mx, my = pygame.mouse.get_pos()

            screen.fill((64, 64, 64))
            pygame.draw.rect(screen, (255, 0, 0), (225, 375, 175, 50))
            pygame.draw.rect(screen, (124, 252, 0), (600, 375, 175, 50))
            centredBlit(mediumFont, 'Do you want to load saved game?', (0, 0, 0), (500, 150))
            centredBlit(font, 'If you encounter an error, you should choose \"No\" because', (0, 0, 0), (500, 200))
            centredBlit(font, 'tower-defense might not be compatible with earlier versions.', (0, 0, 0), (500, 230))
            centredBlit(mediumFont, 'Yes', (0, 0, 0), (687, 400))
            centredBlit(mediumFont, 'No', (0, 0, 0), (313, 400))
            pygame.draw.rect(screen, (128, 128, 128), (225, 375, 175, 50), 3)
            pygame.draw.rect(screen, (128, 128, 128), (600, 375, 175, 50), 3)

            if 375 < my < 425:
                if 225 < mx < 400:
                    pygame.draw.rect(screen, (0, 0, 0), (225, 375, 175, 50), 5)

                if 600 < mx < 775:
                    pygame.draw.rect(screen, (0, 0, 0), (600, 375, 175, 50), 5)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if 375 < my < 425:
                            if 225 < mx < 400:
                                info.reset()
                                cont = True
                            elif 600 < mx < 775:
                                cont = True

            if cont:
                break

    while True:
        mx, my = pygame.mouse.get_pos()

        if info.MapSelect:
            screen.fill((68, 68, 68))

            screen.blit(font.render('Map Select', True, (255, 255, 255)), (450, 25))

            if LOCKED not in list(info.PBs.values()) or cheats:
                pygame.draw.rect(screen, (200, 200, 200), (850, 550, 125, 30))
                screen.blit(font.render('Random Map', True, (0, 0, 0)), (860, 555))
                if 850 <= mx <= 975 and 550 < my <= 580:
                    pygame.draw.rect(screen, (128, 128, 128), (850, 550, 125, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (850, 550, 125, 30), 3)

            for n in range(len(Maps)):
                if info.PBs[Maps[n].name] != LOCKED or cheats:
                    pygame.draw.rect(screen, Maps[n].backgroundColor, (10, 40 * n + 60, 980, 30))
                    if 10 <= mx <= 980 and 40 * n + 60 < my <= 40 * n + 90:
                        pygame.draw.rect(screen, (128, 128, 128), (10, 40 * n + 60, 980, 30), 5)
                    else:
                        pygame.draw.rect(screen, (0, 0, 0), (10, 40 * n + 60, 980, 30), 3)
                    screen.blit(font.render(Maps[n].name.upper(), True, (0, 0, 0)), (20, 62 + n * 40))
                    screen.blit(font.render(f'(Best: {info.PBs[Maps[n].name]})', True, (225, 255, 0) if info.PBs[Maps[n].name] == 100 else (0, 0, 0)), (800, 62 + n * 40))
                else:
                    pygame.draw.rect(screen, (32, 32, 32), (10, 40 * n + 60, 980, 30))
                    pygame.draw.rect(screen, (0, 0, 0), (10, 40 * n + 60, 980, 30), 3)
                    screen.blit(font.render(Maps[n].name.upper(), True, (0, 0, 0)), (20, 62 + n * 40))
                    screen.blit(font.render(LOCKED, True, (0, 0, 0)), (830, 62 + n * 40))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if 10 <= mx <= 980:
                            for n in range(len(Maps)):
                                if 40 * n + 60 <= my <= 40 * n + 90 and (list(info.PBs.values())[n] != LOCKED or cheats):
                                    info.Map = Maps[n]
                                    info.MapSelect = False
                        if 850 <= mx <= 975 and 550 <= my <= 580 and (LOCKED not in info.PBs.values() or cheats):
                            info.Map = random.choice(Maps)
                            info.MapSelect = False
        else:
            if info.win:
                n = False
                for Map in Maps:
                    if n and info.PBs[Map.name] == LOCKED:
                        info.PBs[Map.name] = None
                        break

                    if Map.name == info.Map.name:
                        n = True

                cont = False
                if info.PBs[info.Map.name] is None or info.PBs[info.Map.name] == LOCKED:
                    info.PBs[info.Map.name] = info.HP
                elif info.PBs[info.Map.name] < info.HP:
                    info.PBs[info.Map.name] = info.HP
                info.FinalHP = info.HP
                info.reset()
                save()

                while True:
                    screen.fill((32, 32, 32))
                    centredBlit(largeFont, 'You Win!', (255, 255, 255), (500, 125))
                    centredBlit(font, f'Your Final Score: {info.FinalHP}', (255, 255, 255), (500, 250))
                    centredBlit(font, f'Press [SPACE] to continue!', (255, 255, 255), (500, 280))
                    pygame.display.update()

                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                cont = True
                        elif event.type == pygame.QUIT:
                            save()
                            quit()

                    clock.tick(MaxFPS)
                    if cont:
                        break
            elif info.lose:
                cont = False
                info.reset()
                save()

                while True:
                    screen.fill((32, 32, 32))
                    centredBlit(largeFont, 'You Lost!', (255, 255, 255), (500, 125))
                    centredBlit(font, 'Press [SPACE] to continue!', (255, 255, 255), (500, 250))
                    pygame.display.update()

                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                cont = True
                        elif event.type == pygame.QUIT:
                            save()
                            quit()

                    clock.tick(MaxFPS)
                    if cont:
                        break
            else:
                iterate()


info = data()
if __name__ == '__main__':
    app()
