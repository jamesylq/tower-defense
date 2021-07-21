import os
import pygame
import pickle
import random
import math

from _pickle import UnpicklingError
from typing import overload, List, Tuple
from tower_defense import __version__

current_path = os.path.dirname(__file__)
resource_path = os.path.join(current_path, 'resources')

MaxFPS = 100


class Map:
    def __init__(self, path: list, name: str, backgroundColor: Tuple[int], pathColor: Tuple[int], displayColor: Tuple[int] = None):
        self.name = name
        self.path = path
        self.backgroundColor = backgroundColor
        self.pathColor = pathColor
        self.displayColor = self.backgroundColor if displayColor is None else displayColor


class data:
    def __init__(self):
        self.PBs = {Map.name: (LOCKED if Map != Maps[0] else None) for Map in Maps}
        for attr, default in defaults.items():
            if type(default) in [dict, list]:
                setattr(self, attr, default.copy())
            else:
                setattr(self, attr, default)

    def reset(self):
        for attr, default in defaults.items():
            if attr in ['PBs', 'FinalHP', 'totalWaves', 'status', 'sandboxMode', 'Map', 'statistics']:
                continue

            if type(default) in [dict, list]:
                setattr(self, attr, default.copy())
            else:
                setattr(self, attr, default)


class Towers:
    def __init__(self, x: int, y: int, *, overrideCamoDetect: bool = False):
        self.x = x
        self.y = y
        self.timer = 0
        self.upgrades = [0, 0, 0]
        self.stun = 0
        self.hits = 0
        self.camoDetectionOverride = overrideCamoDetect

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
        self.cooldown = [60, 35, 20, 10][self.upgrades[1]]


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
                screen.blit(IceCircle, (self.x - 125, self.y - 125))

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
    snowCircleTimer = 0

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.snowCircle = self.SnowStormCircle(self, self.x, self.y)
        self.enabled = True

    def draw(self):
        super().draw()
        self.snowCircle.draw()

    def attack(self):
        if self.stun > 0:
            self.stun -= 1
            return

        if not self.enabled:
            return

        if self.timer >= self.cooldown:
            try:
                closest = getTarget(self)
                info.projectiles.append(Projectile(self, self.x, self.y, closest.x, closest.y, freezeDuration=self.freezeDuration))
                self.timer = 0

            except AttributeError:
                pass
        else:
            self.timer += 1

        if self.upgrades[2] >= 2:
            if self.snowCircleTimer >= self.cooldown * 10:
                self.snowCircle.freeze()
                self.snowCircleTimer = 0
            else:
                self.snowCircleTimer += 1

    def update(self):
        self.snowCircle.update()

        self.range = [150, 180, 200, 250][self.upgrades[0]]
        self.cooldown = [50, 38, 27, 20][self.upgrades[1]]
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
                        info.statistics['pops'] += 1
                    self.ignore.append(new if type(enemy.tier) is int else enemy)
                    self.parent.hits += 1
                    info.statistics['pops'] += 1

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
        self.cooldown = [100, 35, 10, 0][self.upgrades[1]]


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
        self.cooldown = [100, 50, 25, 25][self.upgrades[1]]


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
            self.t1 = None
            self.t2 = None
            self.t3 = None
            self.t4 = None
            self.t5 = None
            self.visibleTicks = 0

        def attack(self):
            self.visibleTicks = 50
            self.t1 = getTarget(Towers(self.parent.x, self.parent.y, overrideCamoDetect=self.parent.upgrades[1] >= 2), overrideRange=1000)
            if type(self.t1) is Enemy:
                self.t1.kill(coinMultiplier=getCoinMultiplier(self.parent), bossDamage=25)
                self.parent.hits += 1
                info.statistics['pops'] += 1
                self.t2 = getTarget(Towers(self.t1.x, self.t1.y, overrideCamoDetect=self.parent.upgrades[1] >= 2), ignore=[self.t1], overrideRange=1000)
                if type(self.t2) is Enemy:
                    self.t2.kill(coinMultiplier=getCoinMultiplier(self.parent), bossDamage=25)
                    self.parent.hits += 1
                    info.statistics['pops'] += 1
                    self.t3 = getTarget(Towers(self.t2.x, self.t2.y, overrideCamoDetect=self.parent.upgrades[1] >= 2), ignore=[self.t1, self.t2], overrideRange=1000)
                    if type(self.t3) is Enemy:
                        self.t3.kill(coinMultiplier=getCoinMultiplier(self.parent), bossDamage=25)
                        self.parent.hits += 1
                        info.statistics['pops'] += 1
                        if self.parent.upgrades[1] == 3:
                            self.t4 = getTarget(Towers(self.t3.x, self.t3.y, overrideCamoDetect=self.parent.upgrades[1] >= 2), ignore=[self.t1, self.t2, self.t3], overrideRange=1000)
                            if type(self.t4) is Enemy:
                                self.t4.kill(coinMultiplier=getCoinMultiplier(self.parent), bossDamage=25)
                                self.parent.hits += 1
                                info.statistics['pops'] += 1
                                self.t5 = getTarget(Towers(self.t4.x, self.t4.y, overrideCamoDetect=self.parent.upgrades[1] >= 2), ignore=[self.t1, self.t2, self.t3, self.t4], overrideRange=1000)
                                if type(self.t5) is Enemy:
                                    self.t5.kill(coinMultiplier=getCoinMultiplier(self.parent), bossDamage=25)
                                    self.parent.hits += 1
                                    info.statistics['pops'] += 1
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
                    pygame.draw.line(screen, (191, 0, 255), [self.parent.x, self.parent.y], [self.t1.x, self.t1.y], 3)
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
                    enemy.freezeTimer = max(enemy.freezeTimer, [0, 0, 25, 75][self.parent.upgrades[1]])
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
                info.projectiles.append(Projectile(self.parent, self.x, self.y, closest.x, closest.y, explosiveRadius=30 if self.parent.upgrades[0] >= 2 else 0))

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
        ['Anti-Camo', 'Bomber Villagers', 'Turret Villagers'],
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
        self.cooldown = [50, 50, 50, 20][self.upgrades[0]]
        self.range = [100, 125, 150, 175][self.upgrades[1]]
        self.targets = [villager.target for villager in self.villagers]

        for villager in self.villagers:
            villager.move()

        if len(self.villagers) <= self.upgrades[2]:
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
            try:
                info.projectiles.remove(self)
            except ValueError:
                pass

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
                info.statistics['pops'] += 1


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
    def __init__(self, camo: bool, tier: str or int, spawn: List[int], lineIndex: int):
        try:
            self.tier = int(tier)
        except ValueError:
            self.tier = tier

        self.x, self.y = spawn
        self.lineIndex = lineIndex
        self.totalMovement = 0
        self.freezeTimer = 0
        self.fireTicks = 0
        self.fireIgnitedBy = None
        self.timer = 0
        self.camo = camo

        if self.tier in trueHP.keys():
            self.HP = self.MaxHP = trueHP[self.tier]
        else:
            self.HP = self.MaxHP = 1

    def move(self):
        if self.timer > 0:
            self.timer -= 1
        elif self.tier == 'B':
            self.timer = 250
            info.enemies.append(Enemy(False, 3, [self.x, self.y], self.lineIndex))
        elif self.tier == 'C':
            self.timer = 250
            info.enemies.append(Enemy(False, 7, [self.x, self.y], self.lineIndex))

        if self.freezeTimer > 0:
            self.freezeTimer -= 1
        else:
            if len(info.Map.path) - 1 == self.lineIndex:
                self.kill(spawnNew=False, ignoreBoss=True)
                info.statistics['enemiesMissed'] += 1
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
                    info.statistics['enemiesMissed'] += 1

                self.totalMovement += 1

            try:
                self.freezeTimer = max(bossFreeze[self.tier], self.freezeTimer)
            except KeyError:
                pass

    def update(self):
        if self.fireTicks > 0:
            if self.fireTicks % 100 == 0:
                new = self.kill(burn=True)
                self.fireIgnitedBy.hits += 1
                info.statistics['pops'] += 1
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
                    self.freezeTimer = max(self.freezeTimer, projectile.freezeDuration // (3 if type(self.tier) is str else 1))
                else:
                    info.projectiles.remove(projectile)
                    if projectile.explosiveRadius > 0:
                        projectile.explode(self)
                        if self.tier in onlyExplosiveTiers:
                            new = self
                            for n in range(projectile.impactDamage):
                                new = new.kill(coinMultiplier=projectile.coinMultiplier, bossDamage=projectile.bossDamage)
                                projectile.parent.hits += 1
                                info.statistics['pops'] += 1

                    if self.tier not in onlyExplosiveTiers:
                        new = self
                        for n in range(projectile.impactDamage):
                            new = new.kill(coinMultiplier=projectile.coinMultiplier, bossDamage=projectile.bossDamage)
                            projectile.parent.hits += 1
                            info.statistics['pops'] += 1

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
                            info.statistics['pops'] += 1

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
            centredBlit(font, f'{math.ceil(self.HP / self.MaxHP * 100)}%', (0, 0, 0), (self.x, self.y - 35))

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
                    info.statistics['pops'] += 1
                except AttributeError:
                    pass


def reset() -> None:
    try:
        open('save.txt', 'r').close()
    except FileNotFoundError:
        print('tower-defense.core: No save file detected')
    else:
        with open('save.txt', 'w') as saveFile:
            saveFile.write('')
        print('tower-defense.core: Save file cleared!')


@overload
def removeCharset(s: str, charset: List[str]) -> str: ...
@overload
def removeCharset(s: str, charset: str) -> str: ...

def removeCharset(s, charset) -> str:
    for char in charset:
        s = s.replace(char, '')

    return s


def getSellPrice(tower: Towers) -> float:
    price = tower.price

    for n in range(3):
        for m in range(tower.upgrades[n]):
            price += tower.upgradePrices[n][m]

    return price * 0.5


def centredBlit(font: pygame.font.Font, text: str, color: Tuple[int], pos: Tuple[int]):
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
    if Tower.camoDetectionOverride:
        return True

    if type(Tower) is Turret and Tower.upgrades[2] >= 2:
        return True

    if type(Tower) is Wizard and Tower.upgrades[1] >= 2:
        return True

    if type(Tower) is Village and Tower.upgrades[0] >= 1:
        return True

    villages = [tower for tower in info.towers if type(tower) is Village and tower.upgrades[0] >= 1]
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


def hexToRGB(hexString: str) -> Tuple[int]:
    hexString = removeCharset(hexString, ['0x', '#'])

    if len(hexString) > 6:
        raise ValueError('RGB input error')

    if len(hexString) == 6:
        r, g, b = hexString[:2], hexString[2:4], hexString[4:]

    elif len(hexString) == 5:
        r, g, b = hexString[0], hexString[1:3], hexString[3:]

    else:
        r = '0'
        if len(hexString) == 4:
            g, b = hexString[:2], hexString[2:]

        elif len(hexString) == 3:
            g, b = hexString[0], hexString[1:]

        else:
            g, b = '0', hexString

    return int(r, 16), int(g, 16), int(b, 16)


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
        if info.selected.range in possibleRanges:
            modified = rangeImages[possibleRanges.index(info.selected.range)]
        else:
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
            if classObj.range in possibleRanges:
                modified = rangeImages[possibleRanges.index(classObj.range)]
            else:
                original = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'range.png')), (classObj.range * 2, classObj.range * 2))
                modified = original.copy()
                modified.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
            screen.blit(modified, (mx - classObj.range, my - classObj.range))

    pygame.draw.rect(screen, (221, 221, 221), (800, 0, 200, 450))

    n = 0
    for towerType in Towers.__subclasses__():
        if info.wave >= towerType.req or info.sandboxMode:
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
    screen.blit(font.render(f'Wave {max(info.wave, 1)} of {len(waves)}', True, 0), (825, 570))

    pygame.draw.rect(screen, (255, 0, 0), (0, 450, 20, 20))
    pygame.draw.line(screen, (0, 0, 0), (3, 453), (17, 467), 2)
    pygame.draw.line(screen, (0, 0, 0), (3, 467), (17, 453), 2)
    if mx <= 20 and 450 <= my <= 470:
        pygame.draw.rect(screen, (64, 64, 64), (0, 450, 20, 20), 3)
    else:
        pygame.draw.rect(screen, (0, 0, 0), (0, 450, 20, 20), 3)

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
            for m in range(3):
                if info.selected.upgrades[n] > m:
                    pygame.draw.circle(screen, (0, 255, 0), (560 + 12 * m, 497 + 30 * n), 5)
                pygame.draw.circle(screen, (0, 0, 0), (560 + 12 * m, 497 + 30 * n), 5, 2)

        pygame.draw.rect(screen, (128, 128, 128), (620, 545, 200, 25))
        pygame.draw.rect(screen, (200, 200, 200) if 620 < mx < 820 and 545 < my < 570 else (0, 0, 0), (620, 545, 200, 25), 3)
        screen.blit(font.render(f'Sell for [${round(getSellPrice(info.selected))}]', True, 0), (625, 545))

        if type(info.selected) is IceTower:
            pygame.draw.rect(screen, (0, 255, 0) if info.selected.enabled else (255, 0, 0), (620, 500, 150, 25))
            pygame.draw.rect(screen, (200, 200, 200) if 620 < mx < 770 and 500 < my < 525 else (0, 0, 0), (620, 500, 150, 25), 3)
            centredBlit(font, 'ENABLED' if info.selected.enabled else 'DISABLED', (0, 0, 0), (695, 512))

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


def getClosestPoint(mx: int, my: int, *, sx: int = None, sy: int = None) -> List[int]:
    if sx is None and sy is None:
        return [round((mx - 100) / 25) * 25 + 100, round((my - 125) / 25) * 25 + 125]

    closestDistance = 100000000
    closestX = 0
    closestY = 0

    for x in range(33):
        distance = abs(x * 25 + 100 - mx) ** 2 + (sy - my) ** 2

        if distance < closestDistance:
            closestDistance = distance
            closestX = x * 25 + 100
            closestY = sy

    for y in range(19):
        distance = (sx - mx) ** 2 + abs(y * 25 + 125 - my) ** 2

        if distance < closestDistance:
            closestDistance = distance
            closestX = sx
            closestY = y * 25 + 125

    return [closestX, closestY]


def updateDict(d: dict, l: list) -> dict:
    """Re-order the items in d based on the items in l and deletes redundant items."""

    newDict = {}
    oldDict = d.copy()

    keys = list(oldDict.keys())
    values = list(oldDict.values())

    for item in l:
        try:
            index = keys.index(item)
            newDict[keys[index]] = values[index]
        except ValueError:
            continue

    return newDict


def hasAllMaxScore() -> bool:
    for score in info.PBs.values():
        if score != 100:
            return False

    return True


def save() -> None:
    pickle.dump(info, open('save.txt', 'wb'))


def load() -> None:
    global info

    try:
        info = pickle.load(open('save.txt', 'rb'))

        for attr in ['win', 'lose', 'mapSelect']:
            if hasattr(info, attr):
                delattr(info, attr)

        for attr, default in defaults.items():
            if not hasattr(info, attr):
                setattr(info, attr, default)

        info.PBs = updateDict(info.PBs, [Map.name for Map in Maps])

        foundUnlocked = False
        for Map in Maps:
            if Map.name not in info.PBs.keys():
                info.PBs[Map.name] = LOCKED

            if info.PBs[Map.name] != LOCKED:
                foundUnlocked = True

            elif not foundUnlocked:
                info.PBs[Map.name] = None

        if info.totalWaves != len(waves):
            info.totalWaves = len(waves)
            if info.totalWaves < len(waves):
                for name, PB in info.PBs.items():
                    if type(PB) is int:
                        info.PBs[name] = None

        if not hasAllMaxScore():
            info.sandboxMode = False

    except FileNotFoundError:
        open('save.txt', 'w')
    except (EOFError, ValueError, UnpicklingError):
        pass


def app():
    load()

    if info.Map is not None and info.status == 'game':
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
                                info.status = 'mapSelect'
                                cont = True
                            elif 600 < mx < 775:
                                cont = True

            if cont:
                break

    while True:
        mx, my = pygame.mouse.get_pos()

        if info.status == 'mapSelect':
            screen.fill((68, 68, 68))

            screen.blit(font.render('Map Select', True, (255, 255, 255)), (450, 25))

            pygame.draw.rect(screen, (200, 200, 200), (25, 550, 125, 30))
            centredBlit(font, 'Map Maker', (0, 0, 0), (87, 565))
            if 25 <= mx <= 150 and 550 < my <= 580:
                pygame.draw.rect(screen, (128, 128, 128), (25, 550, 125, 30), 5)
            else:
                pygame.draw.rect(screen, (0, 0, 0), (25, 550, 125, 30), 3)

            if hasAllMaxScore():
                pygame.draw.rect(screen, (0, 225, 0) if info.sandboxMode else (255, 0, 0), (200, 550, 200, 30))
                centredBlit(font, 'Sandbox Mode: ' + ('ON' if info.sandboxMode else 'OFF'), (0, 0, 0), (300, 565))
                if 200 <= mx <= 400 and 550 <= my <= 580:
                    pygame.draw.rect(screen, (128, 128, 128), (200, 550, 200, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (200, 550, 200, 30), 3)

            pygame.draw.rect(screen, (200, 200, 200), (675, 550, 125, 30))
            centredBlit(font, 'Stats', (0, 0, 0), (737, 565))
            if 675 <= mx <= 800 and 550 < my <= 580:
                pygame.draw.rect(screen, (128, 128, 128), (675, 550, 125, 30), 5)
            else:
                pygame.draw.rect(screen, (0, 0, 0), (675, 550, 125, 30), 3)

            pygame.draw.rect(screen, (200, 200, 200), (850, 550, 125, 30))
            centredBlit(font, 'Random Map', (0, 0, 0), (912, 565))
            if 850 <= mx <= 975 and 550 < my <= 580:
                pygame.draw.rect(screen, (128, 128, 128), (850, 550, 125, 30), 5)
            else:
                pygame.draw.rect(screen, (0, 0, 0), (850, 550, 125, 30), 3)

            for n in range(len(Maps)):
                if info.PBs[Maps[n].name] != LOCKED or info.sandboxMode:
                    pygame.draw.rect(screen, Maps[n].displayColor, (10, 40 * n + 60, 980, 30))
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
                                if 40 * n + 60 <= my <= 40 * n + 90 and (list(info.PBs.values())[n] != LOCKED or info.sandboxMode):
                                    info.Map = Maps[n]
                                    info.status = 'game'
                                    info.coins = 100000 if info.sandboxMode else 50

                        if 850 <= mx <= 975 and 550 <= my <= 580:
                            info.Map = random.choice([Map for Map in Maps if info.PBs[Map.name] != LOCKED])
                            info.status = 'game'
                            info.coins = 100000 if info.sandboxMode else 50

                        if 25 <= mx <= 150 and 550 <= my <= 580:
                            info.status = 'mapMaker'

                        if 675 <= mx <= 800 and 550 < my <= 580:
                            info.status = 'statistics'
                            info.statistics['wins'] = updateDict(info.statistics['wins'], [Map.name for Map in Maps])

                        if 200 <= mx <= 400 and 550 <= my <= 580:
                            if hasAllMaxScore():
                                info.sandboxMode = not info.sandboxMode

        elif info.status == 'win':
            n = False
            for Map in Maps:
                if n and info.PBs[Map.name] == LOCKED:
                    info.PBs[Map.name] = None
                    break

                if Map.name == info.Map.name:
                    n = True

            cont = False
            if not info.sandboxMode:
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

                if info.sandboxMode:
                    centredBlit(font, 'You were playing on Sandbox Mode!', (255, 255, 255), (500, 350))

                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            info.status = 'mapSelect'
                            cont = True
                    elif event.type == pygame.QUIT:
                        save()
                        quit()

                clock.tick(MaxFPS)
                if cont:
                    break

        elif info.status == 'lose':
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
                            info.status = 'mapSelect'
                            cont = True

                    elif event.type == pygame.QUIT:
                        save()
                        quit()

                clock.tick(MaxFPS)
                if cont:
                    break

        elif info.status == 'mapMaker':
            if info.mapMakerData['path'] is None:
                ticks = 0
                uppercase = False
                try:
                    charInsertIndex = len(info.mapMakerData[info.mapMakerData['field']])
                except KeyError:
                    charInsertIndex = 0

                while True:
                    mx, my = pygame.mouse.get_pos()

                    translationKeys = {
                        pygame.K_0: '0',
                        pygame.K_1: '1',
                        pygame.K_2: '2',
                        pygame.K_3: '3',
                        pygame.K_4: '4',
                        pygame.K_5: '5',
                        pygame.K_6: '6',
                        pygame.K_7: '7',
                        pygame.K_8: '8',
                        pygame.K_9: '9',
                        pygame.K_a: 'a',
                        pygame.K_b: 'b',
                        pygame.K_c: 'c',
                        pygame.K_d: 'd',
                        pygame.K_e: 'e',
                        pygame.K_f: 'f',
                        pygame.K_g: 'g',
                        pygame.K_h: 'h',
                        pygame.K_i: 'i',
                        pygame.K_j: 'j',
                        pygame.K_k: 'k',
                        pygame.K_l: 'l',
                        pygame.K_m: 'm',
                        pygame.K_n: 'n',
                        pygame.K_o: 'o',
                        pygame.K_p: 'p',
                        pygame.K_q: 'q',
                        pygame.K_r: 'r',
                        pygame.K_s: 's',
                        pygame.K_t: 't',
                        pygame.K_u: 'u',
                        pygame.K_v: 'v',
                        pygame.K_w: 'w',
                        pygame.K_x: 'x',
                        pygame.K_y: 'y',
                        pygame.K_z: 'z',
                        pygame.K_SPACE: ' ',
                        pygame.K_COMMA: ',',
                        pygame.K_LEFTBRACKET: '[',
                        pygame.K_RIGHTBRACKET: ']',
                        pygame.K_QUOTE: '\''
                    }

                    screen.fill((200, 200, 200))
                    centredBlit(mediumFont, 'Map Maker (Beta)', (0, 0, 0), (500, 75))
                    screen.blit(font.render('Map Name: ', True, (0, 0, 0)), (130, 150))
                    screen.blit(font.render('Background Color: ', True, (0, 0, 0)), (50, 250))
                    screen.blit(font.render('Path Color: ', True, (0, 0, 0)), (110, 350))
                    pygame.draw.rect(screen, (100, 100, 100), (225, 150, 675, 30))
                    pygame.draw.rect(screen, (100, 100, 100), (225, 250, 675, 30))
                    pygame.draw.rect(screen, (100, 100, 100), (225, 350, 675, 30))

                    try:
                        if info.mapMakerData['backgroundColor'][0] == '#' or info.mapMakerData['backgroundColor'][:2] == '0x':
                            bgColor = hexToRGB(info.mapMakerData['backgroundColor'])
                        else:
                            bgColor = [int(n) for n in removeCharset(str(info.mapMakerData['backgroundColor']), ' ()[]').split(',')]
                            if len(bgColor) > 3:
                                raise ValueError
                        pygame.draw.rect(screen, bgColor, (925, 250, 30, 30))
                        pygame.draw.rect(screen, (0, 0, 0), (925, 250, 30, 30), 2)
                        validBGColor = True
                    except (ValueError, IndexError):
                        validBGColor = False

                    try:
                        if info.mapMakerData['pathColor'][0] == '#' or info.mapMakerData['pathColor'][:2] == '0x':
                            pathColor = hexToRGB(info.mapMakerData['pathColor'])
                        else:
                            pathColor = [int(n) for n in removeCharset(str(info.mapMakerData['pathColor']), ' ()[]').split(',')]
                            if len(pathColor) > 3:
                                raise ValueError
                        pygame.draw.rect(screen, pathColor, (925, 350, 30, 30))
                        pygame.draw.rect(screen, (0, 0, 0), (925, 350, 30, 30), 2)
                        validPathColor = True
                    except (ValueError, IndexError):
                        validPathColor = False

                    if validBGColor and validPathColor and info.mapMakerData['name'] != '':
                        pygame.draw.rect(screen, (44, 255, 44), (800, 450, 100, 30))
                        centredBlit(font, 'Next Step', (0, 0, 0), (850, 465))

                        if 800 < mx < 900 and 450 < my < 480:
                            pygame.draw.rect(screen, (32, 32, 32), (800, 450, 100, 30), 3)
                        else:
                            pygame.draw.rect(screen, (128, 128, 128), (800, 450, 100, 30), 3)

                    pygame.draw.rect(screen, (255, 0, 0), (30, 550, 100, 30))
                    centredBlit(font, 'Cancel', (0, 0, 0), (80, 565))

                    if 30 < mx < 130 and 550 < my < 580:
                        pygame.draw.rect(screen, (32, 32, 32), (30, 550, 100, 30), 3)
                    else:
                        pygame.draw.rect(screen, (128, 128, 128), (30, 550, 100, 30), 3)

                    field = info.mapMakerData['field']
                    cont = True
                    shifting = pygame.key.get_pressed()[pygame.K_LSHIFT]
                    for event in pygame.event.get():
                        if field is not None:
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_CAPSLOCK:
                                    uppercase = not uppercase

                                elif event.key in [pygame.K_TAB, pygame.K_UP, pygame.K_DOWN]:
                                    fields = ['name', 'backgroundColor', 'pathColor']

                                    if event.key == pygame.K_TAB:
                                        info.mapMakerData['field'] = fields[(fields.index(field) + (-1 if shifting else 1)) % 3]
                                    elif event.key == pygame.K_UP:
                                        info.mapMakerData['field'] = fields[(fields.index(field) - 1) % 3]
                                    elif event.key == pygame.K_DOWN:
                                        info.mapMakerData['field'] = fields[(fields.index(field) + 1) % 3]

                                    charInsertIndex = min(charInsertIndex, len(info.mapMakerData[info.mapMakerData['field']]))

                                elif event.key == pygame.K_LEFT:
                                    charInsertIndex = max(0, charInsertIndex - 1)

                                elif event.key == pygame.K_RIGHT:
                                    charInsertIndex = min(len(info.mapMakerData[info.mapMakerData['field']]), charInsertIndex + 1)

                                else:
                                    for translationKey, letter in translationKeys.items():
                                        if event.key == translationKey:
                                            if event.key == pygame.K_0 and shifting:
                                                letter = ')'
                                            if event.key == pygame.K_3 and shifting:
                                                letter = '#'
                                            if event.key == pygame.K_9 and shifting:
                                                letter = '('

                                            if charInsertIndex == 0:
                                                info.mapMakerData[field] = (letter.upper() if uppercase else letter.lower()) + info.mapMakerData[field]
                                            elif charInsertIndex == len(info.mapMakerData[field]):
                                                info.mapMakerData[field] += (letter.upper() if uppercase else letter.lower())
                                            else:
                                                info.mapMakerData[field] = info.mapMakerData[field][:charInsertIndex] + (letter.upper() if uppercase else letter.lower()) + info.mapMakerData[field][charInsertIndex:]

                                            charInsertIndex += 1

                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                if validBGColor and validPathColor and info.mapMakerData['name'] != '' and 800 < mx < 900 and 450 < my < 480:
                                    try:
                                        info.mapMakerData['backgroundColor'] = [int(n) for n in removeCharset(str(info.mapMakerData['backgroundColor']), ' ()[]').split(',')]
                                    except ValueError:
                                        info.mapMakerData['backgroundColor'] = hexToRGB(info.mapMakerData['backgroundColor'])

                                    try:
                                        info.mapMakerData['pathColor'] = [int(n) for n in removeCharset(str(info.mapMakerData['pathColor']), ' ()[]').split(',')]
                                    except ValueError:
                                        info.mapMakerData['pathColor'] = hexToRGB(info.mapMakerData['pathColor'])

                                    info.mapMakerData['path'] = []
                                    cont = False

                                elif 225 < mx < 900 and 150 < my < 180:
                                    info.mapMakerData['field'] = 'name'
                                    charInsertIndex = min((mx - 230) // font.size('a')[0], len(info.mapMakerData['name']))

                                elif 225 < mx < 900 and 250 < my < 280:
                                    info.mapMakerData['field'] = 'backgroundColor'
                                    charInsertIndex = min((mx - 230) // font.size('a')[0], len(info.mapMakerData['backgroundColor']))

                                elif 225 < mx < 900 and 350 < my < 380:
                                    info.mapMakerData['field'] = 'pathColor'
                                    charInsertIndex = min((mx - 230) // font.size('a')[0], len(info.mapMakerData['pathColor']))

                                elif 30 < mx < 130 and 550 < my < 580:
                                    info.mapMakerData = defaults['mapMakerData'].copy()
                                    info.status = 'mapSelect'
                                    cont = False

                                else:
                                    info.mapMakerData['field'] = None

                        if event.type == pygame.QUIT:
                            save()
                            quit()

                    if not cont:
                        break

                    if pygame.key.get_pressed()[pygame.K_BACKSPACE] and ticks % 10 == 0:
                        try:
                            if charInsertIndex == len(info.mapMakerData[field]):
                                info.mapMakerData[field] = info.mapMakerData[field][:-1]
                            elif charInsertIndex > 0:
                                info.mapMakerData[field] = info.mapMakerData[field][:charInsertIndex-1] + info.mapMakerData[field][charInsertIndex:]

                            charInsertIndex = max(0, charInsertIndex - 1)

                        except (IndexError, KeyError):
                            pass

                    for fieldName in ['name', 'backgroundColor', 'pathColor']:
                        info.mapMakerData[fieldName] = str(info.mapMakerData[fieldName])

                        if fieldName == 'name':
                            y = 150
                        elif fieldName == 'backgroundColor':
                            y = 250
                        else:
                            y = 350

                        txt = info.mapMakerData[fieldName]
                        if ticks < 25 and fieldName == field:
                            length = font.size('a' * charInsertIndex)[0]
                            pygame.draw.line(screen, (0, 0, 0), (230 + length, y), (230 + length, y + 20))

                        screen.blit(font.render(txt, True, (0, 0, 0)), (230, y))

                    pygame.display.update()
                    ticks = (ticks + 1) % 50
                    clock.tick(100)
            else:
                while True:
                    mx, my = pygame.mouse.get_pos()

                    if mx < 100 or mx > 900 or my < 125 or my > 575:
                        cx = cy = -1

                    else:
                        try:
                            cx, cy = getClosestPoint(mx, my, sx=info.mapMakerData['path'][-1][0], sy=info.mapMakerData['path'][-1][1])
                        except IndexError:
                            cx, cy = getClosestPoint(mx, my)

                    screen.fill((200, 200, 200))
                    centredBlit(mediumFont, 'Map Maker (Beta)', (0, 0, 0), (500, 75))
                    pygame.draw.rect(screen, (0, 0, 0), (100, 125, 800, 450), 5)
                    pygame.draw.rect(screen, info.mapMakerData['backgroundColor'], (100, 125, 800, 450))

                    if 100 <= cx <= 900 and 125 <= cy <= 575:
                        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), 3)

                    for i in range(len(info.mapMakerData['path']) - 1):
                        pygame.draw.line(screen, info.mapMakerData['pathColor'], info.mapMakerData['path'][i], info.mapMakerData['path'][i + 1], 10)

                    if info.mapMakerData['path']:
                        pygame.draw.circle(screen, info.mapMakerData['pathColor'], info.mapMakerData['path'][0], 10)

                    pygame.draw.rect(screen, (200, 200, 200), (90, 115, 900, 10))
                    pygame.draw.rect(screen, (200, 200, 200), (90, 575, 900, 10))
                    pygame.draw.rect(screen, (200, 200, 200), (90, 125, 10, 450))
                    pygame.draw.rect(screen, (200, 200, 200), (900, 125, 10, 450))

                    pygame.draw.rect(screen, (100, 100, 100), (0, 570, 60, 30))
                    centredBlit(font, 'Clear', (0, 0, 0), (30, 585))

                    if len(info.mapMakerData['path']) >= 2:
                        pygame.draw.rect(screen, (44, 255, 44), (940, 570, 60, 30))
                        centredBlit(font, 'Done', (0, 0, 0), (970, 585))

                    pygame.display.update()

                    cont = True
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            save()
                            quit()

                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                if 100 <= cx <= 900 and 125 <= cy <= 575:
                                    info.mapMakerData['path'].append([cx, cy])

                                elif 0 < mx < 60 and 570 < my:
                                    info.mapMakerData['path'].clear()

                                elif 940 < mx and 570 < my:
                                    mapVarName = ''
                                    for char in info.mapMakerData['name']:
                                        if char.lower() in 'abcdefghijklmnopqrstuvwxyz':
                                            mapVarName += char.upper()
                                        elif char in ' _-':
                                            mapVarName += '_'

                                    mapShiftedPath = [[point[0] - 100, point[1] - 125] for point in info.mapMakerData['path']]

                                    print(f'This is the map code for your map!\n\n{mapVarName} = Map({mapShiftedPath}, \"{info.mapMakerData["name"]}\", {tuple(info.mapMakerData["backgroundColor"])}, {tuple(info.mapMakerData["pathColor"])})')
                                    info.status = 'mapSelect'
                                    info.mapMakerData = defaults['mapMakerData'].copy()
                                    cont = False

                    if not cont:
                        break

                    clock.tick(100)

        elif info.status == 'game':
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
                if len(info.spawnleft) == 0 and info.ticksSinceNoEnemies == 0:
                    info.coins += 100
                    info.ticksSinceNoEnemies += 1

                if info.nextWave <= 0:
                    try:
                        info.spawnleft = waves[info.wave]
                        info.ticksSinceNoEnemies = 0

                    except IndexError:
                        info.status = 'win'

                        try:
                            info.statistics['wins'][info.Map.name] += 1
                        except KeyError:
                            info.statistics['wins'][info.Map.name] = 1

                    finally:
                        info.spawndelay = 20
                        info.nextWave = 300

                else:
                    if info.nextWave == 300:
                        info.wave += 1
                        info.statistics['wavesPlayed'] += 1

                    info.nextWave -= 1

            mx, my = pygame.mouse.get_pos()

            clock.tick(MaxFPS)
            info.coins += income()

            draw()
            move()

            if info.HP <= 0:
                info.status = 'lose'
                info.statistics['losses'] += 1

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
                                    info.statistics['towersPlaced'] += 1

                            found = False
                            for tower in info.towers:
                                if abs(tower.x - mx) ** 2 + abs(tower.y - my) ** 2 <= 225:
                                    info.selected = tower
                                    found = True

                            if not found:
                                info.selected = None

                        if 810 <= mx <= 910:
                            n = 0
                            for tower in Towers.__subclasses__():
                                if 40 + n * 80 + info.shopScroll <= my <= 70 + n * 80 + info.shopScroll <= 450 and info.coins >= tower.price and info.placing == '' and (
                                        info.wave >= tower.req or info.sandboxMode):
                                    info.coins -= tower.price
                                    info.placing = tower.name
                                    info.selected = None
                                n += 1

                        if mx <= 20 and 450 <= my <= 470:
                            info.reset()
                            info.status = 'mapSelect'

                        if issubclass(type(info.selected), Towers):
                            if 295 <= mx <= 595 and 485 <= my <= 570:
                                n = (my - 485) // 30
                                if info.selected.upgrades[n] < 3:
                                    cost = type(info.selected).upgradePrices[n][info.selected.upgrades[n]]
                                    if info.coins >= cost and (info.wave >= info.selected.req or info.sandboxMode):
                                        info.coins -= cost
                                        info.selected.upgrades[n] += 1

                            elif 620 <= mx < 820 and 545 <= my < 570:
                                info.towers.remove(info.selected)
                                info.coins += getSellPrice(info.selected)
                                info.statistics['towersSold'] += 1
                                info.selected = None


                            elif type(info.selected) is IceTower:
                                if 620 <= mx <= 770 and 500 <= my <= 525:
                                    info.selected.enabled = not info.selected.enabled

                    elif event.button == 4:
                        if mx > 800 and my < 450:
                            info.shopScroll = min(0, info.shopScroll + 10)

                    elif event.button == 5:
                        if mx > 800 and my < 450:
                            maxScroll = len([tower for tower in Towers.__subclasses__() if (info.wave >= tower.req or info.sandboxMode)]) * 80 - 450
                            if maxScroll > 0:
                                info.shopScroll = max(-maxScroll, info.shopScroll - 10)

            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_UP]:
                info.shopScroll = min(0, info.shopScroll + 10)

            elif pressed[pygame.K_DOWN]:
                maxScroll = len([tower for tower in Towers.__subclasses__() if (info.wave >= tower.req or info.sandboxMode)]) * 80 - 450
                if maxScroll > 0:
                    info.shopScroll = max(-maxScroll, info.shopScroll - 10)

        elif info.status == 'statistics':
            scroll = 0

            while True:
                mx, my = pygame.mouse.get_pos()

                screen.fill((200, 200, 200))

                centredBlit(mediumFont, 'General Statistics', (0, 0, 0), (500, 20 - scroll))
                screen.blit(font.render(f'Total Pops: {info.statistics["pops"]}', True, (0, 0, 0)), (20, 70 - scroll))
                screen.blit(font.render(f'Towers Placed: {info.statistics["towersPlaced"]}', True, (0, 0, 0)), (20, 100 - scroll))
                screen.blit(font.render(f'Towers Sold: {info.statistics["towersSold"]}', True, (0, 0, 0)), (20, 130 - scroll))
                screen.blit(font.render(f'Enemies Missed: {info.statistics["enemiesMissed"]}', True, (0, 0, 0)), (20, 160 - scroll))

                centredBlit(mediumFont, 'Wins and Losses', (0, 0, 0), (500, 210 - scroll))

                screen.blit(font.render(f'Total Losses: {info.statistics["losses"]}', True, (0, 0, 0)), (20, 290 - scroll))

                numMaps = 0
                totalWins = 0
                for mapName, wins in info.statistics['wins'].items():
                    numMaps += 1
                    totalWins += wins

                    screen.blit(font.render(f'{mapName}: {wins} ' + ('win' if wins == 1 else 'wins'), True, (0, 0, 0)), (20, 360 + 30 * numMaps - scroll))

                screen.blit(font.render(f'Total Wins: {totalWins}', True, (0, 0, 0)), (20, 260 - scroll))
                if totalWins > 0:
                    centredBlit(mediumFont, 'Wins by map', (0, 0, 0), (500, 340 - scroll))

                pygame.draw.rect(screen, (200, 200, 200), (0, 525, 1000, 75))

                pygame.draw.rect(screen, (255, 0, 0), (25, 550, 100, 30))
                centredBlit(font, 'Close', (0, 0, 0), (75, 565))
                if 25 <= mx <= 125 and 550 <= my <= 580:
                    pygame.draw.rect(screen, (0, 0, 0), (25, 550, 100, 30), 3)
                else:
                    pygame.draw.rect(screen, (128, 128, 128), (25, 550, 100, 30), 3)

                cont = True
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        save()
                        quit()

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if 25 <= mx <= 125 and 550 <= my <= 580:
                                cont = False
                                info.status = 'mapSelect'

                        elif event.button == 4:
                            scroll = max(0, scroll - 10)

                        elif event.button == 5:
                            scroll = min(scroll + 10, max(30 * numMaps - 85, 0))

                if not cont:
                    break

                pygame.display.update()


screen = pygame.display.set_mode((1000, 600))
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()
font = pygame.font.SysFont('Ubuntu Mono', 20)
mediumFont = pygame.font.SysFont('Ubuntu Mono', 30)
largeFont = pygame.font.SysFont('Ubuntu Mono', 75)
pygame.display.set_caption('Tower Defense')

screen.fill((200, 200, 200))
centredBlit(largeFont, f'Tower Defense v{__version__}', (100, 100, 100), (500, 200))
centredBlit(mediumFont, 'Loading...', (100, 100, 100), (500, 300))
pygame.display.update()

RACE_TRACK = Map([[25, 0], [25, 375], [775, 375], [775, 25], [40, 25], [40, 360], [760, 360], [760, 40], [55, 40], [55, 345], [745, 345], [745, 55], [0, 55]], "Race Track", (19, 109, 21), (189, 22, 44), (189, 22, 44))
WIZARDS_LAIR = Map([[0, 25], [775, 25], [775, 425], [25, 425], [25, 75], [725, 75], [725, 375], [0, 375]], "Wizard's Lair", (187, 11, 255), (153, 153, 153))
POND = Map([[0, 25], [700, 25], [700, 375], [100, 375], [100, 75], [800, 75]], "Pond", (6, 50, 98), (0, 0, 255))
LAVA_SPIRAL = Map([[300, 225], [575, 225], [575, 325], [125, 325], [125, 125], [675, 125], [675, 425], [25, 425], [25, 0]], "Lava Spiral", (207, 16, 32), (255, 140, 0), (178, 66, 0))
PLAINS = Map([[25, 0], [25, 425], [525, 425], [525, 25], [275, 25], [275, 275], [750, 275], [750, 0]], "Plains", (19, 109, 21), (155, 118, 83))
DESERT = Map([[0, 25], [750, 25], [750, 200], [25, 200], [25, 375], [800, 375]], "Desert", (170, 108, 35), (178, 151, 5))
THE_END = Map([[0, 225], [800, 225]], "The End", (100, 100, 100), (200, 200, 200))
Maps = [RACE_TRACK, WIZARDS_LAIR, POND, LAVA_SPIRAL, PLAINS, DESERT, THE_END]

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
    '1A' * 2,
    '18' * 50,
    '18' * 75,
    '0A' * 3,
    '0A' * 5,
    '0C'
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
    'B': (191, 64, 191),
    'C': (64, 64, 64)
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
    'B': 69,
    'C': 100
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
    'B': 1,
    'C': 1
}

onlyExplosiveTiers = [7, 8, 'C']

trueHP = {
    'A': 1000,
    'B': 1500,
    'C': 2100
}

bossCoins = {
    'A': 150,
    'B': 250,
    'C': 500
}

bossFreeze = {
    'A': 3,
    'B': 5,
    'C': 8
}

defaults = {
    'enemies': [],
    'projectiles': [],
    'piercingProjectiles': [],
    'towers': [],
    'HP': 100,
    'FinalHP': None,
    'coins': 50,
    'selected': None,
    'placing': '',
    'nextWave': 299,
    'wave': 0,
    'shopScroll': 0,
    'spawnleft': '',
    'spawndelay': 9,
    'Map': None,
    'totalWaves': len(waves),
    'status': 'mapSelect',
    'mapMakerData': {
        'name': '',
        'backgroundColor': '(0, 0, 0)',
        'pathColor': '(0, 0, 0)',
        'path': None,
        'field': None
    },
    'sandboxMode': False,
    'statistics': {
        'pops': 0,
        'towersPlaced': 0,
        'towersSold': 0,
        'enemiesMissed': 0,
        'wavesPlayed': 0,
        'wins': {},
        'losses': 0
    },
    'ticksSinceNoEnemies': 0
}
LOCKED = 'LOCKED'

IceCircle = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'ice_circle.png')), (250, 250)).copy()
IceCircle.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)

rangeImages = []
possibleRanges = [0, 50, 100, 125, 130, 150, 165, 175, 180, 200, 250, 400]
for possibleRange in possibleRanges:
    rangeImage = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'range.png')), (possibleRange * 2,) * 2)
    alphaImage = rangeImage.copy()
    alphaImage.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
    rangeImages.append(alphaImage)

SIN45 = COS45 = math.sqrt(2) / 2

info = data()
if __name__ == '__main__':
    app()
    print('tower-defense.core: An unexpected error occured.')
