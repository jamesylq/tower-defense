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
Maps = []
Runes = []


class Map:
    def __init__(self, path: list, name: str, backgroundColor: Tuple[int], pathColor: Tuple[int], displayColor: Tuple[int] = None):
        self.name = name
        self.path = path
        self.backgroundColor = backgroundColor
        self.pathColor = pathColor
        self.displayColor = self.backgroundColor if displayColor is None else displayColor
        Maps.append(self)

    def __str__(self):
        return self.name

Map([[25, 0], [25, 375], [775, 375], [775, 25], [40, 25], [40, 360], [760, 360], [760, 40], [55, 40], [55, 345], [745, 345], [745, 55], [0, 55]], "Race Track", (19, 109, 21), (189, 22, 44), (189, 22, 44))
Map([[0, 25], [775, 25], [775, 425], [25, 425], [25, 75], [725, 75], [725, 375], [0, 375]], "Wizard's Lair", (187, 11, 255), (153, 153, 153))
Map([[0, 25], [700, 25], [700, 375], [100, 375], [100, 75], [800, 75]], "Pond", (6, 50, 98), (0, 0, 255))
Map([[400, 225], [400, 50], [50, 50], [50, 400], [50, 50], [750, 50], [750, 400], [750, 50], [400, 50], [400, 225]], "The Sky", (171, 205, 239), (255, 255, 255))
Map([[350, 0], [350, 150], [25, 150], [25, 300], [350, 300], [350, 450], [450, 450], [450, 300], [775, 300], [775, 150], [450, 150], [450, 0]], "Candyland", (255, 105, 180), (199, 21, 133))
Map([[0, 400], [725, 400], [725, 325], [650, 325], [650, 375], [750, 375], [750, 75], [650, 75], [650, 125], [725, 125], [725, 50], [0, 50]], "The Moon", (100, 100, 100), (255, 255, 102), (255, 255, 102))
Map([[300, 225], [575, 225], [575, 325], [125, 325], [125, 125], [675, 125], [675, 425], [25, 425], [25, 0]], "Lava Spiral", (207, 16, 32), (255, 140, 0), (178, 66, 0))
Map([[25, 0], [25, 425], [525, 425], [525, 25], [275, 25], [275, 275], [750, 275], [750, 0]], "Plains", (19, 109, 21), (155, 118, 83))
Map([[0, 25], [750, 25], [750, 200], [25, 200], [25, 375], [800, 375]], "Desert", (170, 108, 35), (178, 151, 5))
Map([[125, 0], [125, 500], [400, 500], [400, -50], [675, -50], [675, 500]], "Disconnected", (64, 64, 64), (100, 100, 100), (100, 0, 0))
Map([[0, 225], [800, 225]], "The End", (100, 100, 100), (200, 200, 200))


class Rune:
    def __init__(self, name: str, dropChance: float, lore: str, imageName: str = 'rune.png'):
        self.name = name
        self.ID = len(Runes)
        self.dropChance = dropChance
        self.lore = lore

        try:
            self.imageTexture = pygame.image.load(os.path.join(resource_path, imageName))
        except FileNotFoundError:
            self.imageTexture = pygame.image.load(os.path.join(resource_path, 'rune.png'))

        if self.imageTexture.get_size() != (99, 99):
            self.imageTexture = pygame.transform.scale(self.imageTexture, (99, 99))

        self.smallImageTexture = pygame.transform.scale(self.imageTexture, (66, 66))

        Runes.append(self)

    def roll(self) -> bool:
        if random.randint(1, 100) <= self.dropChance and self.name not in info.runes:
            return True
        return False

    def draw(self, x: int, y: int, size: int = 99):
        if size == 99:
            texture = self.imageTexture
        elif size == 66:
            texture = self.smallImageTexture
        else:
            texture = pygame.transform.scale(self.imageTexture, (size, size))

        screen.blit(texture, texture.get_rect(center=[x, y]))

    def __str__(self):
        return self.name


class RuneEffect:
    class BloodRuneEffect:
        def __init__(self, x: int, y: int):
            self.x = x
            self.y = y
            self.visibleTicks = 50

        def draw(self):
            pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), 2)

    class IceRuneEffect:
        def __init__(self, x: int, y: int):
            self.x = x
            self.y = y
            self.visibleTicks = 50

        def draw(self):
            pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y), 2)

    class GoldRuneEffect:
        def __init__(self, x: int, y: int):
            self.x = x
            self.y = y
            self.visibleTicks = 50

        def draw(self):
            pygame.draw.circle(screen, (255, 255, 0), (self.x, self.y), 2)

    class LightningRuneEffect:
        def __init__(self, x: int, y: int):
            self.x = x
            self.y = y
            self.visibleTicks = 50

        def draw(self):
            pygame.draw.line(screen, (191, 0, 255), (self.x, self.y), (500, -200), 3)

    class ShrinkRuneEffect:
        def __init__(self, x: int, y: int, radius: int, color: Tuple[int]):
            self.x = x
            self.y = y
            self.radius = radius
            self.color = color
            self.visibleTicks = 50

        def draw(self):
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius * self.visibleTicks // 50)

    class LeapRuneEffect:
        def __init__(self, x: int, y: int, radius: int, color: Tuple[int]):
            self.x = x
            self.y = y
            self.radius = radius
            self.color = color
            self.visibleTicks = 50

        def draw(self):
            pygame.draw.circle(screen, self.color, (self.x, self.y - 600 + 12 * self.visibleTicks), self.radius)

    def __init__(self):
        self.rune = info.equippedRune
        self.effects = []

    def createEffects(self, target, *, color: Tuple[int] = None):
        if self.rune == 'Blood Rune':
            for n in range(5):
                self.effects.append(self.BloodRuneEffect(target.x + random.randint(-3, 3), target.y + random.randint(-3, 3)))

        elif self.rune == 'Ice Rune':
            for n in range(5):
                self.effects.append(self.IceRuneEffect(target.x + random.randint(-3, 3), target.y + random.randint(-3, 3)))

        elif self.rune == 'Gold Rune':
            for n in range(5):
                self.effects.append(self.GoldRuneEffect(target.x + random.randint(-3, 3), target.y + random.randint(-3, 3)))

        elif self.rune == 'Lightning Rune':
            self.effects.append(self.LightningRuneEffect(target.x, target.y))

        elif self.rune == 'Shrink Rune':
            self.effects.append(self.ShrinkRuneEffect(target.x, target.y, 20 if type(target.tier) is str else 10, enemyColors[str(target.tier)] if color is None else color))

        elif self.rune == 'Leap Rune':
            self.effects.append(self.LeapRuneEffect(target.x, target.y, 20 if type(target.tier) is str else 10, enemyColors[str(target.tier)] if color is None else color))

    def draw(self):
        for effect in self.effects:
            effect.draw()
            effect.visibleTicks -= 1

            if effect.visibleTicks == 0:
                self.effects.remove(effect)

    def update(self):
        self.rune = info.equippedRune


Rune('null', 0, 'A glitched rune. How did you get this?')
Rune('Blood Rune', 15, 'The rune forged by the Blood Gods.', 'blood_rune.png')
Rune('Ice Rune', 12, 'A rune as cold as ice.', 'ice_rune.png')
Rune('Gold Rune', 8, 'The rune of the wealthy - Classy!', 'gold_rune.png')
Rune('Leap Rune', 8, 'Jump!', 'leap_rune.png')
Rune('Lightning Rune', 5, 'Legends say it was created by Zeus himself.', 'lightning_rune.png')
Rune('Shrink Rune', 3, 'This magical rune compresses its foes!', 'shrink_rune.png')
Rune('Rainbow Rune', 2, 'A rainbow tail forms behind your cursor!', 'rainbow_rune.png')


class PhysicalPowerUp:
    class Spike:
        def __init__(self, x, y, parent):
            self.x = x
            self.y = y
            self.parent = parent

        def update(self):
            for enemy in info.enemies:
                if type(enemy.tier) is str:
                    if abs(self.x - enemy.x) ** 2 + abs(self.y - enemy.y) ** 2 <= 484:
                        enemy.kill(bossDamage=25)
                        self.parent.objects.remove(self)
                        break
                else:
                    if abs(self.x - enemy.x) ** 2 + abs(self.y - enemy.y) ** 2 <= 144:
                        enemy.kill()
                        self.parent.objects.remove(self)
                        break

        def draw(self):
            pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), 3)

    class Lightning:
        def __init__(self, x, y, parent):
            self.x = x
            self.y = y
            self.parent = parent
            self.visibleTicks = 50

        def update(self):
            self.visibleTicks -= 1
            if self.visibleTicks == 0:
                self.parent.objects.remove(self)

        def draw(self):
            pygame.draw.line(screen, (191, 0, 255), (500, -200), (self.x, self.y), 3)

    def __init__(self):
        self.objects = []

    def update(self):
        for obj in self.objects:
            obj.update()

    def draw(self):
        for obj in self.objects:
            obj.draw()


class data:
    def __init__(self):
        self.PBs = {Map.name: (LOCKED if Map != Maps[0] else None) for Map in Maps}
        for attr, default in defaults.items():
            if type(default) in [dict, list]:
                setattr(self, attr, default.copy())
            else:
                setattr(self, attr, default)

    def reset(self):
        for attr in ['enemies', 'projectiles', 'piercingProjectiles', 'towers', 'HP', 'coins', 'selected', 'placing', 'nextWave', 'wave', 'shopScroll', 'spawnleft', 'spawndelay', 'ticksSinceNoEnemies']:
            default = defaults[attr]

            if type(default) in [dict, list]:
                setattr(self, attr, default.copy())
            else:
                setattr(self, attr, default)


class Towers:
    def __init__(self, x: int, y: int, *, overrideCamoDetect: bool = False, overrideAddToTowers: bool = False):
        self.x = x
        self.y = y
        self.timer = 0
        self.upgrades = [0, 0, 0]
        self.stun = 0
        self.hits = 0
        self.camoDetectionOverride = overrideCamoDetect
        if not overrideAddToTowers:
            info.towers.append(self)

    def draw(self):
        if towerImages[self.name] is not None:
            try:
                screen.blit(towerImages[self.name], (self.x - 15, self.y - 15))
            except TypeError:
                screen.blit(towerImages[self.name][self.getImageFrame()], (self.x - 15, self.y - 15))
        else:
            pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

    def attack(self):
        pass

    def update(self):
        pass


class Turret(Towers):
    name = 'Turret'
    imageName = 'turret.png'
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
        self.rotation = 0

    def attack(self):
        if self.stun > 0:
            self.stun -= 1
            return

        if self.timer >= self.cooldown:
            try:
                closest = getTarget(self)
                explosiveRadius = 30 if self.upgrades[2] >= 1 else 0

                proj = Projectile(self, self.x, self.y, closest.x, closest.y, bossDamage=(10 if self.upgrades[2] == 3 else 1), explosiveRadius=explosiveRadius)
                proj.move(0)

                try:
                    if 1 >= proj.dx >= 0.5 >= proj.dy >= 0:
                        self.rotation = 0
                    elif 1 >= proj.dx >= 0.5 >= proj.dy >= 0:
                        self.rotation = 1
                    elif -0.5 <= proj.dx <= 0 <= 0.5 <= proj.dy <= 1:
                        self.rotation = 7
                    elif 1 >= proj.dx >= 0.5 >= 0 >= proj.dy >= -0.5:
                        self.rotation = 2
                    elif -1 <= proj.dx <= -0.5 <= 0 <= proj.dy <= 0.5:
                        self.rotation = 6
                    elif -1 <= proj.dx <= -0.5 <= proj.dy <= 0:
                        self.rotation = 5
                    elif 0.5 >= proj.dx >= 0 >= -0.5 >= proj.dy >= -1:
                        self.rotation = 3
                    elif 0 >= proj.dx >= -0.5 >= proj.dy >= -1:
                        self.rotation = 4

                except TypeError:
                    pass

                self.timer = 0

            except AttributeError:
                pass
        else:
            self.timer += 1

    def update(self):
        self.range = [100, 130, 165, 200][self.upgrades[0]]
        self.cooldown = [60, 35, 20, 10][self.upgrades[1]]

    def getImageFrame(self) -> int:
        return self.rotation


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
                        enemy.freezeTimer = max(enemy.freezeTimer, self.freezeDuration)

        def update(self):
            self.freezeDuration = [100, 150, 150, 199][self.parent.upgrades[2]]

    name = 'Ice Tower'
    imageName = 'ice_tower.png'
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
    range = 150
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
                Projectile(self, self.x, self.y, closest.x, closest.y, freezeDuration=self.freezeDuration)
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
        self.freezeDuration = [20, 45, 45, 75][self.upgrades[2]]


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
                        enemy.fireTicks = max(enemy.fireTicks, 300)
                        enemy.fireIgnitedBy = self.parent

                    color = enemyColors[str(enemy.tier)]
                    new = enemy

                    if self.parent.upgrades[2] == 0:
                        damage = 1
                    else:
                        damage = 2

                    for n in range(damage):
                        new = new.kill(coinMultiplier=getCoinMultiplier(self.parent), overrideRuneColor=color)
                        info.statistics['pops'] += 1
                        self.parent.hits += 1
                        self.ignore.append(new if type(enemy.tier) is int else enemy)

                        if new is None:
                            break

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
    imageName = 'spike_tower.png'
    color = (224, 17, 95)
    req = 2
    price = 125
    upgradePrices = [
        [50, 100, 150],
        [100, 400, 1000],
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
    imageName = 'bomb_tower.png'
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
                fireTicks = 200 if self.upgrades[2] >= 2 else 0
                impactDamage = 2 if self.upgrades[2] == 3 else 1

                closest = getTarget(self)

                Projectile(self, self.x, self.y, closest.x, closest.y, explosiveRadius=explosionRadius, impactDamage=impactDamage, fireTicks=fireTicks)
                if self.upgrades[1] == 3:
                    twin = Projectile(self, self.x, self.y, closest.x, closest.y, explosiveRadius=explosionRadius, impactDamage=impactDamage, fireTicks=fireTicks)
                    for n in range(5):
                        twin.move()

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
    imageName = 'banana_farm.png'
    color = (255, 255, 0)
    req = 4
    price = 150
    upgradePrices = [
        [30, 50, 65],
        [30, 45, 60],
        [50, 150, 300]
    ]
    upgradeNames = [
        ['Banana Cannon', 'More Banana Shots', 'Super Range'],
        ['Increased Income', 'Money Farm', 'Money Factory'],
        ['Double Coin Drop', '3x Coin Drop', '5x Coin Drop']
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
                    Projectile(self, self.x, self.y, closest.x, closest.y)
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
    imageName = 'bowler.png'
    color = (64, 64, 64)
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
                    PiercingProjectile(self, self.x, self.y, self.pierce, direction)
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
            self.t1 = getTarget(Towers(self.parent.x, self.parent.y, overrideCamoDetect=self.parent.upgrades[1] >= 2, overrideAddToTowers=True), overrideRange=1000)
            if type(self.t1) is Enemy:
                self.t1.kill(coinMultiplier=getCoinMultiplier(self.parent), bossDamage=25)
                self.parent.hits += 1
                info.statistics['pops'] += 1
                self.t2 = getTarget(Towers(self.t1.x, self.t1.y, overrideCamoDetect=self.parent.upgrades[1] >= 2, overrideAddToTowers=True), ignore=[self.t1], overrideRange=1000)

                if type(self.t2) is Enemy:
                    self.t2.kill(coinMultiplier=getCoinMultiplier(self.parent), bossDamage=25)
                    self.parent.hits += 1
                    info.statistics['pops'] += 1
                    self.t3 = getTarget(Towers(self.t2.x, self.t2.y, overrideCamoDetect=self.parent.upgrades[1] >= 2, overrideAddToTowers=True), ignore=[self.t1, self.t2], overrideRange=1000)

                    if type(self.t3) is Enemy:
                        self.t3.kill(coinMultiplier=getCoinMultiplier(self.parent), bossDamage=25)
                        self.parent.hits += 1
                        info.statistics['pops'] += 1
                        if self.parent.upgrades[1] == 3:
                            self.t4 = getTarget(Towers(self.t3.x, self.t3.y, overrideCamoDetect=self.parent.upgrades[1] >= 2, overrideAddToTowers=True), ignore=[self.t1, self.t2, self.t3], overrideRange=1000)

                            if type(self.t4) is Enemy:
                                self.t4.kill(coinMultiplier=getCoinMultiplier(self.parent), bossDamage=25)
                                self.parent.hits += 1
                                info.statistics['pops'] += 1
                                self.t5 = getTarget(Towers(self.t4.x, self.t4.y, overrideCamoDetect=self.parent.upgrades[1] >= 2, overrideAddToTowers=True), ignore=[self.t1, self.t2, self.t3, self.t4], overrideRange=1000)

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
    imageName = 'wizard.png'
    color = (128, 0, 128)
    req = 7
    price = 250
    upgradePrices = [
        [30, 60, 150],
        [75, 95, 150],
        [50, 65, 90]
    ]
    upgradeNames = [
        ['Longer Range', 'Extreme Range', 'Magic Healing'],
        ['Lighning Zap', 'Wisdom of Camo', '5-hit Lightning'],
        ['Big Blast Radius', 'Faster Reload', 'Hyper Reload']
    ]
    range = 125
    cooldown = 100

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.lightning = self.LightningBolt(self)
        self.lightningTimer = 0
        self.healTimer = 0

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
                Projectile(self, self.x, self.y, closest.x, closest.y, explosiveRadius=60 if self.upgrades[2] else 30)
                self.timer = 0
            except AttributeError:
                pass
        else:
            self.timer += 1

        if self.lightningTimer >= 500:
            self.lightning.attack()
        elif self.upgrades[1] >= 1:
            self.lightningTimer += 1

    def update(self):
        if self.upgrades[0] == 3:
            if self.healTimer >= 1000 and info.HP < 100:
                info.HP += 1
                self.healTimer = 0
            else:
                self.healTimer += 1

        self.range = [125, 150, 175, 175][self.upgrades[0]]
        self.cooldown = [50, 50, 33, 16][self.upgrades[2]]


class InfernoTower(Towers):
    class AttackRender:
        def __init__(self, parent, target):
            self.parent = parent
            self.target = target
            self.visibleTicks = 50

        def draw(self):
            pygame.draw.line(screen, (255, 69, 0), (self.parent.x, self.parent.y - 12), (self.target.x, self.target.y), 2)
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
                    enemy.fireTicks = max(enemy.fireTicks, (500 if self.parent.upgrades[2] else 300))
                    enemy.fireIgnitedBy = self.parent
                    if type(enemy.tier) is int:
                        enemy.freezeTimer = max(enemy.freezeTimer, [0, 0, 25, 75][self.parent.upgrades[1]])
                    self.renders.append(InfernoTower.AttackRender(self.parent, enemy))
                    found = True

            if not found:
                self.parent.timer = 500

        def draw(self):
            for render in self.renders:
                render.draw()

    name = 'Inferno'
    imageName = 'inferno.png'
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
        self.inferno.draw()
        super().draw()

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
        self.range = [100, 125, 160, 200][self.upgrades[0]]
        self.cooldown = [500, 375, 250, 200][self.upgrades[1]]

    def getImageFrame(self) -> int:
        if self.inferno.renders:
            return 0
        return 1


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
            closest = getTarget(Towers(self.x, self.y, overrideAddToTowers=True), overrideRange=self.parent.range)
            if closest is None:
                self.parent.timer = 100
            else:
                Projectile(self.parent, self.x, self.y, closest.x, closest.y, explosiveRadius=30 if self.parent.upgrades[0] >= 2 else 0)

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
                        closest = getTarget(Towers(self.x, self.y, overrideAddToTowers=True), overrideRange=self.parent.range, ignore=self.parent.targets)
                        if closest is None:
                            self.tx = self.parent.x
                            self.ty = self.parent.y
                        else:
                            self.tx = closest.x
                            self.ty = closest.y
                            self.target = closest
                            self.moveCooldown = 0
                            self.parent.targets = [villager.target for villager in self.parent.villagers]

                    elif getTarget(Towers(self.x, self.y, overrideAddToTowers=True), overrideRange=self.parent.range) is None or (self.x - self.parent.x) ** 2 + (self.y - self.parent.y) ** 2 < 625:
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
    imageName = 'village.png'
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
        for villager in self.villagers:
            villager.draw()
        super().draw()

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
    def __init__(self, parent: Towers, x: int, y: int, tx: int, ty: int, *, explosiveRadius: int = 0, freezeDuration: int = 0, bossDamage: int = 1, impactDamage: int = 1, fireTicks: int = 0, overrideAddToProjectiles: bool = False):
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

        if not overrideAddToProjectiles:
            info.projectiles.append(self)

        if self.explosiveRadius > 0:
            self.color = (0, 0, 0)
        elif self.freezeDuration > 0:
            self.color = (0, 0, 187)
        elif self.coinMultiplier > 1:
            self.color = (255, 255, 0)
        else:
            self.color = (187, 187, 187)

    def move(self, speed: int = 5):
        try:
            if self.dx is None:
                dx, dy = self.x - self.tx, self.y - self.ty
                self.dx = abs(dx / (abs(dx) + abs(dy))) * (-1 if self.tx < self.x else 1)
                self.dy = abs(dy / (abs(dx) + abs(dy))) * (-1 if self.ty < self.y else 1)

                self.x += self.dx * speed
                self.y += self.dy * speed
            else:
                self.x += self.dx * speed
                self.y += self.dy * speed

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
    def __init__(self, parent: Towers, x: int, y: int, pierceLimit: int, direction: str, *, speed: int = 2, overrideAddToPiercingProjectiles: bool = False):
        self.parent = parent
        self.coinMultiplier = getCoinMultiplier(self.parent)
        self.x = x
        self.y = y
        self.pierce = pierceLimit
        self.direction = direction
        self.ignore = []
        self.movement = 0
        self.speed = speed
        if not overrideAddToPiercingProjectiles:
            info.piercingProjectiles.append(self)

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
    def __init__(self, tier: str or int, spawn: List[int], lineIndex: int, *, camo: bool = False, regen: bool = False):
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
        self.regen = regen
        self.regenTimer = 0

        if self.tier in trueHP.keys():
            self.HP = self.MaxHP = trueHP[self.tier]
        else:
            self.HP = self.MaxHP = 1

    def move(self):
        if self.timer > 0:
            self.timer -= 1
        elif self.tier == 'B':
            self.timer = 250
            info.enemies.append(Enemy(3, [self.x, self.y], self.lineIndex))
        elif self.tier == 'D':
            self.timer = 100
            info.enemies.append(Enemy(7, [self.x, self.y], self.lineIndex))

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
                    self.freezeTimer = max(self.freezeTimer, projectile.freezeDuration // (5 if type(self.tier) is str else 1))
                else:
                    info.projectiles.remove(projectile)
                    if projectile.explosiveRadius > 0:
                        projectile.explode(self)
                        if self.tier in onlyExplosiveTiers:
                            color = enemyColors[str(self.tier)]
                            new = self

                            for n in range(projectile.impactDamage):
                                new = new.kill(coinMultiplier=projectile.coinMultiplier, bossDamage=projectile.bossDamage, overrideRuneColor=color)
                                projectile.parent.hits += 1
                                info.statistics['pops'] += 1

                                if new is None:
                                    break

                    if self.tier not in onlyExplosiveTiers:
                        color = enemyColors[str(self.tier)]
                        new = self

                        for n in range(projectile.impactDamage):
                            new = new.kill(coinMultiplier=projectile.coinMultiplier, bossDamage=projectile.bossDamage, overrideRuneColor=color)
                            projectile.parent.hits += 1
                            info.statistics['pops'] += 1

                            if new is None:
                                break

        if self.tier not in onlyExplosiveTiers:
            for projectile in info.piercingProjectiles:
                if abs(self.x - projectile.x) ** 2 + abs(self.y - projectile.y) ** 2 < (400 if type(self.tier) is str else 100):
                    if (self not in projectile.ignore) and (canSeeCamo(projectile.parent) or not self.camo):
                        color = enemyColors[str(self.tier)]
                        damage = 1
                        if type(projectile.parent) is Bowler:
                            if projectile.parent.upgrades[0] == 2:
                                damage = 2
                            elif projectile.parent.upgrades[0] == 3:
                                damage = 2 * (projectile.movement // 100 + 1)

                        new = self
                        for n in range(damage):
                            new = new.kill(coinMultiplier=projectile.coinMultiplier, overrideRuneColor=color)
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
            healthPercent = self.HP / trueHP[self.tier]

            if healthPercent >= 0.8:
                color = (191, 255, 0)
            elif healthPercent >= 0.6:
                color = (196, 211, 0)
            elif healthPercent >= 0.4:
                color = (255, 255, 0)
            elif healthPercent >= 0.2:
                color = (255, 69, 0)
            else:
                color = (255, 0, 0)

            pygame.draw.rect(screen, (128, 128, 128), (self.x - 50, self.y - 25, 100, 5))
            pygame.draw.rect(screen, color, (self.x - 50, self.y - 25, round(self.HP / self.MaxHP * 100), 5))
            pygame.draw.rect(screen, (0, 0, 0), (self.x - 50, self.y - 25, 100, 5), 1)
            centredPrint(font, f'{math.ceil(self.HP / self.MaxHP * 100)}%', (self.x, self.y - 35))

        pygame.draw.circle(screen, enemyColors[str(self.tier)], (self.x, self.y), 20 if type(self.tier) is str else 10)
        if self.camo:
            pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), 20 if type(self.tier) is str else 10, 2)
        if self.regen:
            pygame.draw.circle(screen, (255, 105, 180), (self.x, self.y), 20 if type(self.tier) is str else 10, 2)

    def kill(self, *, spawnNew: bool = True, coinMultiplier: int = 1, ignoreBoss: bool = False, burn: bool = False, bossDamage: int = 1, overrideRuneColor: Tuple[int] = None):
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
                    new = Enemy(self.tier - 1, (self.x, self.y), self.lineIndex, camo=self.camo, regen=self.regen)
                    new.fireTicks = self.fireTicks
                    new.fireIgnitedBy = self.fireIgnitedBy
                    info.enemies.append(new)

                    return new

            if not ignoreBoss:
                RuneEffects.createEffects(self, color=overrideRuneColor)

        elif type(self.tier) is str:
            self.HP -= 10 if burn else bossDamage
            if self.HP <= 0:
                self.kill(spawnNew=spawnNew, coinMultiplier=coinMultiplier, ignoreBoss=True)

                try:
                    self.fireIgnitedBy.hits += 1
                    info.statistics['pops'] += 1
                except AttributeError:
                    pass

                RuneEffects.createEffects(self, color=overrideRuneColor)

    def updateRegen(self):
        if not self.regen:
            return

        if self.regenTimer >= 100:
            if type(self.tier) is int:
                self.tier += 1
                if str(self.tier) not in enemyColors.keys():
                    self.tier -= 1
            else:
                self.HP = min(self.MaxHP, self.HP + 50)

            self.regenTimer = 0

        else:
            self.regenTimer += 1


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


def leftAlignPrint(font: pygame.font.Font, text: str, pos: Tuple[int], color: Tuple[int] = (0, 0, 0)) -> None:
    textObj = font.render(text, True, color)
    screen.blit(textObj, textObj.get_rect(center=[pos[0] + font.size(text)[0] / 2, pos[1]]))


def centredPrint(font: pygame.font.Font, text: str, pos: Tuple[int], color: Tuple[int] = (0, 0, 0)) -> None:
    textObj = font.render(text, True, color)
    screen.blit(textObj, textObj.get_rect(center=pos))


def rightAlignPrint(font: pygame.font.Font, text: str, pos: Tuple[int], color: Tuple[int] = (0, 0, 0)) -> None:
    textObj = font.render(text, True, color)
    screen.blit(textObj, textObj.get_rect(center=[pos[0] - font.size(text)[0] / 2, pos[1]]))


def centredBlit(image: pygame.Surface, pos: Tuple[int]):
    screen.blit(image, image.get_rect(center=pos))


def income() -> float:
    total = 0.001
    for tower in info.towers:
        if type(tower) is BananaFarm:
            total += [0.001, 0.005, 0.01, 0.025][tower.upgrades[1]]

    return total


def getCoinMultiplier(Tower: Towers) -> int:
    bananaFarms = [tower for tower in info.towers if type(tower) is BananaFarm]
    maxCoinMult = 1
    for bananaFarm in bananaFarms:
        if abs(Tower.x - bananaFarm.x) ** 2 + abs(Tower.y - bananaFarm.y) ** 2 < bananaFarm.range ** 2:
            maxCoinMult = max(maxCoinMult, [1, 2, 3, 5][bananaFarm.upgrades[2]])

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
        if not (0 <= enemy.x <= 800 and 0 <= enemy.y <= 450):
            continue

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


def getRune(name: str) -> Rune:
    for rune in Runes:
        if rune.name == name:
            return rune


def draw() -> None:
    mx, my = pygame.mouse.get_pos()

    screen.fill(info.Map.backgroundColor)

    for i in range(len(info.Map.path) - 1):
        pygame.draw.line(screen, info.Map.pathColor, info.Map.path[i], info.Map.path[i + 1], 10)
    pygame.draw.circle(screen, info.Map.pathColor, info.Map.path[0], 10)

    RuneEffects.draw()
    PowerUps.draw()

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
        centredPrint(font, f'Click anywhere on the map to place the {info.placing}!', (400, 400))
        centredPrint(font, f'Press [ESC] to cancel!', (400, 425))

        if 0 <= mx <= 800 and 0 <= my <= 450:
            if info.placing == 'spikes':
                screen.blit(powerUps['spikes'], (mx - 25, my - 25))

            else:
                classObj = None
                for tower in Towers.__subclasses__():
                    if tower.name == info.placing:
                        classObj = tower

                if info.placing in ['Village', 'Banana Farm']:
                    for tower in info.towers:
                        if tower == info.selected:
                            continue

                        if abs(tower.x - mx) ** 2 + abs(tower.y - my) ** 2 < classObj.range ** 2:
                            pygame.draw.circle(screen, classObj.color, (tower.x, tower.y), 17, 2)

                if towerImages[classObj.name] is not None:
                    try:
                        screen.blit(towerImages[classObj.name], (mx - 15, my - 15))
                    except TypeError:
                        screen.blit(towerImages[classObj.name][0], (mx - 15, my - 15))
                else:
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
            leftAlignPrint(font, f'{towerType.name} (${towerType.price})', (810, 20 + 80 * n + info.shopScroll))

            pygame.draw.rect(screen, (187, 187, 187), (945, 30 + 80 * n + info.shopScroll, 42, 42))
            if towerImages[towerType.name] is not None:
                try:
                    screen.blit(towerImages[towerType.name], (951, 36 + 80 * n + info.shopScroll))
                except TypeError:
                    screen.blit(towerImages[towerType.name][0], (951, 36 + 80 * n + info.shopScroll))
            else:
                pygame.draw.circle(screen, towerType.color, (966, 51 + 80 * n + info.shopScroll), 15)

            pygame.draw.line(screen, 0, (800, 80 + 80 * n + info.shopScroll), (1000, 80 + 80 * n + info.shopScroll), 3)
            pygame.draw.line(screen, 0, (800, 80 * n + info.shopScroll), (1000, 80 * n + info.shopScroll), 3)

            pygame.draw.rect(screen, (200, 200, 200), (810, 40 + 80 * n + info.shopScroll, 100, 30))
            centredPrint(font, 'Buy New', (860, 55 + 80 * n + info.shopScroll))

            if 810 <= mx <= 910 and 40 + 80 * n + info.shopScroll <= my <= 70 + 80 * n + info.shopScroll:
                pygame.draw.rect(screen, (128, 128, 128), (810, 40 + 80 * n + info.shopScroll, 100, 30), 3)
            else:
                pygame.draw.rect(screen, (0, 0, 0), (810, 40 + 80 * n + info.shopScroll, 100, 30), 3)

        n += 1

    pygame.draw.rect(screen, (170, 170, 170), (0, 450, 1000, 150))

    leftAlignPrint(font, f'FPS: {round(clock.get_fps(), 1)}', (10, 555))
    leftAlignPrint(font, str(info.HP), (10, 530))
    screen.blit(healthImage, (font.size(str(info.HP))[0] + 17, 523))
    leftAlignPrint(font, f'Coins: {math.floor(info.coins)}', (10, 580))
    leftAlignPrint(font, f'Wave {max(info.wave, 1)} of {len(waves)}', (825, 580))

    pygame.draw.rect(screen, (200, 200, 200), (810, 470, 50, 50))
    centredBlit(powerUps['spikes'], (835, 495))
    if 810 <= mx <= 860 and 470 <= my <= 520:
        pygame.draw.rect(screen, (128, 128, 128), (810, 470, 50, 50), 3)
    else:
        pygame.draw.rect(screen, (0, 0, 0), (810, 470, 50, 50), 3)
    if info.powerUps['spikes'] > 0:
        centredPrint(tinyFont, str(info.powerUps['spikes']), (835, 530))

    pygame.draw.rect(screen, (200, 200, 200), (875, 470, 50, 50))
    centredBlit(powerUps['lightning'], (900, 495))
    if 875 <= mx <= 925 and 470 <= my <= 520:
        pygame.draw.rect(screen, (128, 128, 128), (875, 470, 50, 50), 3)
    else:
        pygame.draw.rect(screen, (0, 0, 0), (875, 470, 50, 50), 3)
    if info.powerUps['lightning'] > 0:
        centredPrint(tinyFont, str(info.powerUps['lightning']), (900, 530))

    pygame.draw.rect(screen, (200, 200, 200), (940, 470, 50, 50))
    centredBlit(powerUps['antiCamo'], (965, 495))
    if 940 <= mx <= 990 and 470 <= my <= 520:
        pygame.draw.rect(screen, (128, 128, 128), (940, 470, 50, 50), 3)
    else:
        pygame.draw.rect(screen, (0, 0, 0), (940, 470, 50, 50), 3)
    if info.powerUps['antiCamo'] > 0:
        centredPrint(tinyFont, str(info.powerUps['antiCamo']), (965, 530))

    pygame.draw.rect(screen, (255, 0, 0), (0, 450, 20, 20))
    pygame.draw.line(screen, (0, 0, 0), (3, 453), (17, 467), 2)
    pygame.draw.line(screen, (0, 0, 0), (3, 467), (17, 453), 2)
    if mx <= 20 and 450 <= my <= 470:
        pygame.draw.rect(screen, (64, 64, 64), (0, 450, 20, 20), 3)
    else:
        pygame.draw.rect(screen, (0, 0, 0), (0, 450, 20, 20), 3)

    if issubclass(type(info.selected), Towers):
        leftAlignPrint(font, 'Upgrades:', (200, 497))
        leftAlignPrint(font, f'Pops: {info.selected.hits}', (200, 470))

        for n in range(3):
            if 295 <= mx <= 595 and 485 + 30 * n <= my <= 515 + 30 * n:
                pygame.draw.rect(screen, (200, 200, 200), (295, 485 + 30 * n, 300, 30))
            else:
                pygame.draw.rect(screen, (128, 128, 128), (295, 485 + 30 * n, 300, 30))

            if info.selected.upgrades[n] == 3:
                pygame.draw.rect(screen, (255, 255, 191), (295, 485 + 30 * n, 300, 30))
                pygame.draw.rect(screen, (0, 0, 0), (295, 485 + 30 * n, 300, 30), 3)
                centredPrint(font, 'MAX', (445, 500 + 30 * n))
            else:
                pygame.draw.rect(screen, (0, 0, 0), (295, 485 + 30 * n, 300, 30), 3)

                leftAlignPrint(font, f'{info.selected.upgradeNames[n][info.selected.upgrades[n]]} [${info.selected.upgradePrices[n][info.selected.upgrades[n]]}]', (300, 500 + n * 30), (32, 32, 32))

            for m in range(3):
                if info.selected.upgrades[n] > m:
                    pygame.draw.circle(screen, (0, 255, 0), (560 + 12 * m, 497 + 30 * n), 5)
                pygame.draw.circle(screen, (0, 0, 0), (560 + 12 * m, 497 + 30 * n), 5, 2)

        pygame.draw.rect(screen, (128, 128, 128), (620, 545, 150, 25))

        if 620 < mx < 820 and 545 < my < 570:
            pygame.draw.rect(screen, (200, 200, 200), (620, 545, 150, 25), 3)
        else:
            pygame.draw.rect(screen, (0, 0, 0), (620, 545, 150, 25), 3)

        centredPrint(font, f'Sell: ${round(getSellPrice(info.selected))}', (695, 557))

        if type(info.selected) is IceTower:
            pygame.draw.rect(screen, (0, 255, 0) if info.selected.enabled else (255, 0, 0), (620, 500, 150, 25))
            if 620 <= mx <= 770:
                pygame.draw.rect(screen, (200, 200, 200), (620, 500, 150, 25), 3)
            else:
                pygame.draw.rect(screen, (0, 0, 0), (620, 500, 150, 25), 3)
            centredPrint(font, 'ENABLED' if info.selected.enabled else 'DISABLED', (695, 512))

    pygame.display.update()


def move() -> None:
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


def hasAllUnlocked() -> bool:
    for score in info.PBs.values():
        if score is None or score == LOCKED:
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

        for attr, default in defaults['statistics'].items():
            try:
                info.statistics[attr] = info.statistics[attr]
            except KeyError:
                if attr == 'totalWins':
                    try:
                        info.statistics[attr] = sum([val for val in info.statistics['wins'].values()])
                    except KeyError:
                        info.statistics[attr] = 0
                else:
                    info.statistics[attr] = default

        for attr, default in defaults['achievements'].items():
            try:
                info.achievements[attr] = info.achievements[attr]
            except KeyError:
                info.achievements[attr] = default

        for powerUp, default in defaults['powerUps'].items():
            try:
                info.powerUps[powerUp] = info.powerUps[powerUp]
            except KeyError:
                info.powerUps[powerUp] = default

        info.PBs = updateDict(info.PBs, [Map.name for Map in Maps])

        info.statistics['mapsBeat'] = len([m for m in info.PBs.keys() if type(info.PBs[m]) is int])

        foundUnlocked = False
        for Map in Maps:
            if Map.name not in info.PBs.keys():
                info.PBs[Map.name] = LOCKED

            if info.PBs[Map.name] != LOCKED:
                foundUnlocked = True

            elif not foundUnlocked:
                info.PBs[Map.name] = None

        Maps.reverse()

        foundCompleted = False
        for Map in Maps:
            if foundCompleted and info.PBs[Map.name] == LOCKED:
                info.PBs[Map.name] = None

            elif type(info.PBs[Map.name]) is int:
                foundCompleted = True

        Maps.reverse()

        if info.totalWaves != len(waves):
            info.totalWaves = len(waves)
            if info.totalWaves < len(waves):
                for name, PB in info.PBs.items():
                    if type(PB) is int:
                        info.PBs[name] = None

        if not hasAllUnlocked():
            info.sandboxMode = False

    except FileNotFoundError:
        open('save.txt', 'w')

    except AttributeError as e:
        print(f'tower-defense.core: Fatal - There seems to be something wrong with your save-file.\n\nSee details: {e}')

    except UnpicklingError as e:
        print(f'tower-defense.core: Fatal - Your save-file seems to be corrupt and it has been reset!\n\nSee details: {e}')

    except (EOFError, ValueError):
        pass


def app() -> None:
    load()

    if info.Map is not None and info.status == 'game':
        cont = False

        while True:
            mx, my = pygame.mouse.get_pos()

            screen.fill((64, 64, 64))
            pygame.draw.rect(screen, (255, 0, 0), (225, 375, 175, 50))
            pygame.draw.rect(screen, (124, 252, 0), (600, 375, 175, 50))
            centredPrint(mediumFont, 'Do you want to load saved game?', (500, 150))
            centredPrint(font, 'If you encounter an error, you should choose \"No\" because', (500, 200))
            centredPrint(font, 'tower-defense might not be compatible with earlier versions.', (500, 230))
            centredPrint(mediumFont, 'Yes', (687, 400))
            centredPrint(mediumFont, 'No', (313, 400))
            pygame.draw.rect(screen, (0, 0, 0), (225, 375, 175, 50), 5)
            pygame.draw.rect(screen, (0, 0, 0), (600, 375, 175, 50), 5)

            if 375 < my < 425:
                if 225 < mx < 400:
                    pygame.draw.rect(screen, (128, 128, 128), (225, 375, 175, 50), 5)

                if 600 < mx < 775:
                    pygame.draw.rect(screen, (128, 128, 128), (600, 375, 175, 50), 5)

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
        global mouseTrail

        if info.status == 'mapSelect':
            scroll = 0

            while True:
                clock.tick(MaxFPS)

                mx, my = pygame.mouse.get_pos()

                screen.fill((68, 68, 68))

                n = 0
                for Map in Maps:
                    if info.PBs[Map.name] != LOCKED or info.sandboxMode:
                        pygame.draw.rect(screen, Map.displayColor, (10, 40 * n + 60 - scroll, 825, 30))
                        if 10 <= mx <= 835 and 40 * n + 60 - scroll <= my <= 40 * n + 90 - scroll:
                            pygame.draw.rect(screen, (128, 128, 128), (10, 40 * n + 60 - scroll, 825, 30), 5)
                        else:
                            pygame.draw.rect(screen, (0, 0, 0), (10, 40 * n + 60 - scroll, 825, 30), 3)

                        leftAlignPrint(font, Map.name.upper(), (20, 74 + n * 40 - scroll))
                        if info.PBs[Map.name] == 100:
                            centredPrint(font, f'[Best: 100]', (900, 74 + n * 40 - scroll), (225, 225, 0))
                        else:
                            centredPrint(font, f'[Best: {info.PBs[Map.name]}]', (900, 74 + n * 40 - scroll))

                    else:
                        pygame.draw.rect(screen, (32, 32, 32), (10, 40 * n + 60 - scroll, 825, 30))
                        pygame.draw.rect(screen, (0, 0, 0), (10, 40 * n + 60 - scroll, 825, 30), 3)
                        leftAlignPrint(font, Map.name.upper(), (20, 74 + n * 40 - scroll))
                        centredPrint(font, LOCKED, (900, 74 + n * 40 - scroll))

                    n += 1

                pygame.draw.rect(screen, (68, 68, 68), (0, 0, 1000, 50))
                centredPrint(font, 'Map Select', (500, 30), (255, 255, 255))

                pygame.draw.rect(screen, (200, 200, 200), (10, 40 * n + 60 - scroll, 825, 30))
                if 10 <= mx <= 835 and 40 * n + 60 <= my + scroll <= 40 * n + 90:
                    pygame.draw.rect(screen, (128, 128, 128), (10, 40 * n + 60 - scroll, 825, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (10, 40 * n + 60 - scroll, 825, 30), 3)
                centredPrint(font, 'Random Map', (413, 40 * n + 75 - scroll))

                pygame.draw.rect(screen, (68, 68, 68), (0, 500, 1000, 100))

                pygame.draw.rect(screen, (200, 200, 200), (25, 550, 125, 30))
                centredPrint(font, 'Map Maker', (87, 565))
                if 25 <= mx <= 150 and 550 < my <= 580:
                    pygame.draw.rect(screen, (128, 128, 128), (25, 550, 125, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (25, 550, 125, 30), 3)

                if hasAllUnlocked():
                    pygame.draw.rect(screen, (0, 225, 0) if info.sandboxMode else (255, 0, 0), (200, 550, 200, 30))
                    centredPrint(font, 'Sandbox Mode: ' + ('ON' if info.sandboxMode else 'OFF'), (300, 565))
                    if 200 <= mx <= 400 and 550 <= my <= 580:
                        pygame.draw.rect(screen, (128, 128, 128), (200, 550, 200, 30), 5)
                    else:
                        pygame.draw.rect(screen, (0, 0, 0), (200, 550, 200, 30), 3)

                pygame.draw.rect(screen, (200, 200, 200), (675, 550, 125, 30))
                centredPrint(font, 'Stats', (737, 565))
                if 675 <= mx <= 800 and 550 < my <= 580:
                    pygame.draw.rect(screen, (128, 128, 128), (675, 550, 125, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (675, 550, 125, 30), 3)

                pygame.draw.rect(screen, (200, 200, 200), (825, 550, 150, 30))
                centredPrint(font, 'Achievements', (900, 565))
                if 825 <= mx <= 975 and 550 < my <= 580:
                    pygame.draw.rect(screen, (128, 128, 128), (825, 550, 150, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (825, 550, 150, 30), 3)

                pygame.draw.rect(screen, (200, 200, 200), (825, 510, 150, 30))
                centredPrint(font, 'Cosmetics', (900, 525))
                if 825 <= mx <= 975 and 510 < my <= 540:
                    pygame.draw.rect(screen, (128, 128, 128), (825, 510, 150, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (825, 510, 150, 30), 3)

                if info.newRunes > 0:
                    pygame.draw.circle(screen, (255, 0, 0), (975, 510), 10)
                    pygame.draw.circle(screen, (0, 0, 0), (975, 510), 10, 2)
                    centredPrint(font, str(info.newRunes), (975, 508), (255, 255, 255))

                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_UP]:
                    scroll = max(0, scroll - 2)
                if pressed[pygame.K_DOWN]:
                    scroll = min(scroll + 2, max(40 * n + 90 - 490, 0))

                pygame.display.update()

                cont = True
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        save()
                        quit()

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if 10 <= mx <= 835:
                                for n in range(len(Maps)):
                                    if 50 <= 40 * n + 60 - scroll <= my <= 40 * n + 90 - scroll <= 500 and list(info.PBs.values())[n] != LOCKED:
                                        info.Map = Maps[n]
                                        info.status = 'game'
                                        info.coins = 100000 if info.sandboxMode else 50
                                        mouseTrail.clear()
                                        cont = False

                            if 10 <= mx <= 935 and 40 * len(Maps) + 60 <= my + scroll <= 40 * len(Maps) + 90 and my <= 500:
                                info.Map = random.choice([Map for Map in Maps if info.PBs[Map.name] != LOCKED])
                                info.status = 'game'
                                info.coins = 100000 if info.sandboxMode else 50
                                mouseTrail.clear()
                                cont = False

                            if 25 <= mx <= 150 and 550 <= my <= 580:
                                info.status = 'mapMaker'
                                cont = False

                            if 675 <= mx <= 800 and 550 <= my <= 580:
                                info.status = 'statistics'
                                info.statistics['wins'] = updateDict(info.statistics['wins'], [Map.name for Map in Maps])
                                cont = False

                            if 825 <= mx <= 975 and 550 <= my <= 580:
                                info.status = 'achievements'
                                cont = False

                            if 825 <= mx <= 975 and 510 <= my <= 540:
                                info.status = 'cosmetics'
                                info.newRunes = 0
                                cont = False

                            if 200 <= mx <= 400 and 550 <= my <= 580:
                                if hasAllUnlocked():
                                    info.sandboxMode = not info.sandboxMode

                        elif event.button == 4:
                            scroll = max(scroll - 5, 0)

                        elif event.button == 5:
                            scroll = min(scroll + 5, max(40 * n + 90 - 490, 0))

                if not cont:
                    break

        elif info.status == 'achievements':
            for achievement, requirement in achievementRequirements.items():
                stat = info.statistics[requirement['attr']]
                highest = 0
                for tier in requirement['tiers']:
                    if stat >= tier:
                        highest += 1

                info.achievements[achievement] = highest

            while True:
                mx, my = pygame.mouse.get_pos()

                screen.fill((200, 200, 200))

                centredPrint(mediumFont, 'Achievements', (500, 50))

                n = 0
                for achievement, information in achievements.items():
                    pygame.draw.rect(screen, (100, 100, 100), (10, 80 + 110 * n, 980, 100))
                    leftAlignPrint(font, information['names'][min(info.achievements[achievement], 2)], (20, 93 + 110 * n))
                    leftAlignPrint(tinyFont, information['lore'].replace('[%]', str(achievementRequirements[achievement]['tiers'][min(info.achievements[achievement], 2)])), (20, 120 + 110 * n))

                    for m in range(3):
                        if info.achievements[achievement] > m:
                            pygame.draw.circle(screen, (255, 255, 0), (900 + m * 20, 100 + 110 * n), 7)
                        pygame.draw.circle(screen, (0, 0, 0), (900 + m * 20, 100 + 110 * n), 7, 2)

                    if info.achievements[achievement] < len(achievementRequirements[achievement]['tiers']):
                        current = info.statistics[achievementRequirements[achievement]['attr']]
                        target = achievementRequirements[achievement]['tiers'][info.achievements[achievement]]
                        percent = current / target * 100
                        pygame.draw.rect(screen, (0, 255, 0), (40, 140 + 110 * n, percent * 8, 20))
                        txt = f'{round(percent, 1)}%'
                        if 10 <= mx <= 990 and 80 + 110 * n <= my <= 180 + 110 * n:
                            txt += f' ({current} / {target})'

                        centredPrint(font, txt, (440, 150 + 110 * n))
                    else:
                        current = info.statistics[achievementRequirements[achievement]['attr']]
                        target = achievementRequirements[achievement]['tiers'][info.achievements[achievement] - 1]
                        txt = '100.0%'
                        if 10 <= mx <= 990 and 80 + 110 * n <= my <= 180 + 110 * n:
                            txt += f' ({current} / {target})'

                        pygame.draw.rect(screen, (0, 255, 0), (40, 140 + 110 * n, 800, 20))
                        centredPrint(font, txt, (440, 150 + 110 * n))

                    pygame.draw.rect(screen, (0, 0, 0), (40, 140 + 110 * n, 800, 20), 3)

                    n += 1

                pygame.draw.rect(screen, (255, 0, 0), (20, 550, 100, 30))
                centredPrint(font, 'Close', (70, 565))
                if 20 <= mx <= 120 and 550 <= my <= 580:
                    pygame.draw.rect(screen, (0, 0, 0), (20, 550, 100, 30), 3)
                else:
                    pygame.draw.rect(screen, (128, 128, 128), (20, 550, 100, 30), 5)

                pygame.display.update()

                cont = True
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        save()
                        quit()

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if 20 <= mx <= 120 and 550 <= my <= 580:
                                info.status = 'mapSelect'
                                cont = False

                if not cont:
                    break

        elif info.status == 'win':
            while True:
                screen.fill((32, 32, 32))
                centredPrint(largeFont, 'You Win!', (500, 125), (255, 255, 255))
                centredPrint(font, f'Your Final Score: {info.FinalHP}', (500, 250), (255, 255, 255))
                centredPrint(font, f'Press [SPACE] to continue!', (500, 280), (255, 255, 255))

                if info.sandboxMode:
                    centredPrint(font, 'You were playing on Sandbox Mode!', (500, 350), (255, 255, 255))

                pygame.display.update()

                cont = True
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            info.status = 'mapSelect'
                            cont = False
                    elif event.type == pygame.QUIT:
                        save()
                        quit()

                clock.tick(MaxFPS)
                if not cont:
                    break

        elif info.status == 'lose':
            cont = False
            info.reset()
            save()

            while True:
                screen.fill((32, 32, 32))
                centredPrint(largeFont, 'You Lost!', (500, 125), (255, 255, 255))
                centredPrint(font, 'Press [SPACE] to continue!', (500, 250), (255, 255, 255))
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

                    centredPrint(mediumFont, 'Map Maker', (500, 75))
                    n = 0
                    for txt in ['Map name:', 'Background Color:', 'Path Color:']:
                        rightAlignPrint(font, txt, (200, 160 + n * 100))
                        n += 1

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
                        centredPrint(font, 'Next Step', (850, 465))

                        if 800 < mx < 900 and 450 < my < 480:
                            pygame.draw.rect(screen, (128, 128, 128), (800, 450, 100, 30), 3)
                        else:
                            pygame.draw.rect(screen, (0, 0, 0), (800, 450, 100, 30), 3)

                    pygame.draw.rect(screen, (255, 0, 0), (30, 550, 100, 30))
                    centredPrint(font, 'Cancel', (80, 565))

                    if 30 < mx < 130 and 550 < my < 580:
                        pygame.draw.rect(screen, (128, 128, 128), (30, 550, 100, 30), 3)
                    else:
                        pygame.draw.rect(screen, (0, 0, 0), (30, 550, 100, 30), 3)

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
                                    try:
                                        if event.key == pygame.K_UP:
                                            info.mapMakerData['field'] = fields[(fields.index(field) - 1)]
                                        if event.key == pygame.K_DOWN:
                                            info.mapMakerData['field'] = fields[(fields.index(field) + 1)]

                                    except IndexError:
                                        pass

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
                            length = font.size(txt[:charInsertIndex])[0]
                            pygame.draw.line(screen, (0, 0, 0), (length + 230, y), (length + 230, y + 20))

                        leftAlignPrint(font, txt, (230, y + 10))

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
                    centredPrint(mediumFont, 'Map Maker', (500, 75))
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
                    centredPrint(font, 'Clear', (30, 585))

                    if mx <= 60 and 570 <= my:
                        pygame.draw.rect(screen, (128, 128, 128), (0, 570, 60, 30), 3)
                    else:
                        pygame.draw.rect(screen, (0, 0, 0), (0, 570, 60, 30), 3)

                    if len(info.mapMakerData['path']) >= 2:
                        pygame.draw.rect(screen, (44, 255, 44), (940, 570, 60, 30))
                        centredPrint(font, 'Done', (970, 585))

                        if mx >= 940 and my >= 570:
                            pygame.draw.rect(screen, (128, 128, 128), (940, 570, 60, 30), 3)
                        else:
                            pygame.draw.rect(screen, (0, 0, 0), (940, 570, 60, 30), 3)

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
                                    mapShiftedPath = [[point[0] - 100, point[1] - 125] for point in info.mapMakerData['path']]

                                    print(f'This is the map code for your map!\n\nMap({mapShiftedPath}, \"{info.mapMakerData["name"]}\", {tuple(info.mapMakerData["backgroundColor"])}, {tuple(info.mapMakerData["pathColor"])})')
                                    info.status = 'mapSelect'
                                    info.mapMakerData = defaults['mapMakerData'].copy()
                                    cont = False

                    if not cont:
                        break

                    clock.tick(100)

        elif info.status == 'cosmetics':
            while True:
                mx, my = pygame.mouse.get_pos()

                screen.fill((200, 200, 200))

                pygame.draw.rect(screen, (255, 0, 0), (30, 550, 100, 30))
                centredPrint(font, 'Close', (80, 565))
                if 30 <= mx <= 130 and 550 <= my <= 580:
                    pygame.draw.rect(screen, (64, 64, 64), (30, 550, 100, 30), 3)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (30, 550, 100, 30), 3)

                pygame.draw.rect(screen, (160, 160, 160), (440, 100, 120, 120))
                centredPrint(font, 'Click on a Rune to equip!' if info.equippedRune is None else 'Equipped Rune:',
                             (500, 75))

                pygame.draw.rect(screen, (160, 160, 160), (50, 250, 900, 225))
                if len(info.runes) == 0:
                    centredPrint(font, 'You have no runes!', (500, 362))
                    centredPrint(tinyFont, 'Win some battles to earn some runes!', (500, 390))

                x = 0
                y = 0
                for rune in info.runes:
                    try:
                        pygame.draw.rect(screen, (64, 64, 64), (x * 75 + 52, y * 75 + 252, 70, 70))
                        getRune(rune).draw(x * 75 + 87, y * 75 + 287, 66)

                        if rune == info.equippedRune:
                            pygame.draw.rect(screen, (128, 128, 128), (x * 75 + 52, y * 75 + 252, 70, 70), 5)

                        x += 1
                        if x == 12:
                            x = 0
                            y += 1

                    except AttributeError:
                        print('tower-defense.core: There seems to be a removed rune in your inventory and it has been deleted!')
                        info.runes.remove(rune)

                if info.equippedRune is not None:
                    try:
                        getRune(info.equippedRune).draw(500, 160)
                        leftAlignPrint(font, info.equippedRune, (600, 120))
                        leftAlignPrint(tinyFont, getRune(info.equippedRune).lore, (600, 150))

                    except AttributeError:
                        print('tower-defense.core: You seem to have a removed rune equipped and it has been deleted!')
                        info.equippedRune = None

                cont = True
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        save()
                        quit()

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if 30 <= mx <= 130 and 550 <= my <= 580:
                                info.status = 'mapSelect'
                                cont = False

                            elif 440 <= mx <= 560 and 100 <= my <= 220:
                                info.equippedRune = None

                            elif 50 <= mx <= 950 and 250 <= my <= 475:
                                try:
                                    info.equippedRune = info.runes[(mx - 50) // 75 + 12 * ((my - 250) // 75)]

                                except IndexError:
                                    pass

                    elif event.type == pygame.KEYDOWN:
                        if info.equippedRune is not None:
                            if event.key == pygame.K_RETURN:
                                info.status = 'mapSelect'
                                cont = False

                            try:
                                if event.key == pygame.K_UP:
                                    info.equippedRune = info.runes[max(info.runes.index(info.equippedRune) - 12, 0)]
                                elif event.key == pygame.K_DOWN:
                                    info.equippedRune = info.runes[min(info.runes.index(info.equippedRune) + 12, len(info.runes) - 1)]
                                elif event.key == pygame.K_LEFT:
                                    info.equippedRune = info.runes[max(info.runes.index(info.equippedRune) - 1, 0)]
                                elif event.key == pygame.K_RIGHT:
                                    info.equippedRune = info.runes[min(info.runes.index(info.equippedRune) + 1, len(info.runes) - 1)]

                            except ValueError:
                                print('tower-defense.core: Fatal - There seems to be a problem with your equipped rune.')

                if not cont:
                    break

                pygame.display.update()

        elif info.status == 'game':
            global rainbowShiftCount, rainbowShiftIndex

            mx, my = pygame.mouse.get_pos()

            mouseTrail.append([mx, my])
            if len(mouseTrail) >= 10:
                mouseTrail = mouseTrail[:-10]

            if info.spawndelay == 0 and len(info.spawnleft) > 0:
                info.enemies.append(Enemy(info.spawnleft[1], info.Map.path[0], 0, camo=info.spawnleft[0] == '1', regen=info.spawnleft[0] == '2'))

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
                            info.statistics['totalWins'] += 1

                            for rune in Runes:
                                if rune.roll():
                                    info.runes.append(rune.name)
                                    info.newRunes += 1

                            for powerUp in defaults['powerUps'].keys():
                                if random.randint(0, 1) == 0:
                                    info.powerUps[powerUp] += 1

                            try:
                                nextMap = Maps[[m.name for m in Maps].index(info.Map.name) + 1].name
                                if info.PBs[nextMap] == LOCKED:
                                    info.PBs[nextMap] = None

                            except IndexError:
                                pass

                            if not info.sandboxMode:
                                if info.PBs[info.Map.name] is None or info.PBs[info.Map.name] == LOCKED:
                                    info.PBs[info.Map.name] = info.HP
                                elif info.PBs[info.Map.name] < info.HP:
                                    info.PBs[info.Map.name] = info.HP

                            info.statistics['mapsBeat'] = len([m for m in info.PBs.keys() if type(info.PBs[m]) is int])

                            info.FinalHP = info.HP
                            info.reset()
                            save()

                    else:
                        info.spawndelay = 20
                        info.nextWave = 300

                else:
                    if info.nextWave == 300:
                        info.wave += 1
                        info.statistics['wavesPlayed'] += 1

                    info.nextWave -= 1

            clock.tick(MaxFPS)
            info.coins += income()

            for enemy in info.enemies:
                enemy.updateRegen()

            draw()
            move()

            if info.equippedRune == 'Rainbow Rune':
                rainbowShiftCount += 1
                if rainbowShiftCount > 1000:
                    rainbowShiftIndex = (rainbowShiftIndex + 1) % 7
                    rainbowShiftCount = 0

                for n in range(len(mouseTrail) - 1):
                    pygame.draw.line(screen, [rainbowColors[rainbowShiftIndex][n] + rainbowShift[rainbowShiftIndex][n] * rainbowShiftCount for n in range(3)], mouseTrail[n], mouseTrail[n + 1], 5)

            pygame.display.update()

            RuneEffects.update()
            PowerUps.update()

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
                            if info.placing == 'spikes':
                                for n in range(25):
                                    PowerUps.objects.append(PhysicalPowerUp.Spike(mx + random.randint(-25, 25), my + random.randint(-25, 25), PowerUps))
                                info.placing = ''

                            else:
                                for towerType in Towers.__subclasses__():
                                    if towerType.name == info.placing:
                                        info.placing = ''
                                        towerType(mx, my)
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
                                if 40 + n * 80 + info.shopScroll <= my <= 70 + n * 80 + info.shopScroll and my <= 450 and info.coins >= tower.price and info.placing == '' and (info.wave >= tower.req or info.sandboxMode):
                                    info.coins -= tower.price
                                    info.placing = tower.name
                                    info.selected = None
                                    info.statistics['coinsSpent'] += tower.price
                                n += 1

                        if mx <= 20 and 450 <= my <= 470:
                            info.reset()
                            info.status = 'mapSelect'

                        if 470 <= my <= 520:
                            if 810 <= mx <= 860 and info.powerUps['spikes'] > 0:
                                if not info.sandboxMode:
                                    info.powerUps['spikes'] -= 1
                                info.placing = 'spikes'

                            if 875 <= mx <= 925 and info.powerUps['lightning'] > 0:
                                if not info.sandboxMode:
                                    info.powerUps['lightning'] -= 1

                                n = 0
                                for enemy in info.enemies:
                                    if not enemy.camo:
                                        PowerUps.objects.append(PhysicalPowerUp.Lightning(enemy.x, enemy.y, PowerUps))
                                        enemy.kill(bossDamage=25)

                                        n += 1
                                        if n == 10:
                                            break

                            if 940 <= mx <= 990 and info.powerUps['antiCamo'] > 0:
                                if not info.sandboxMode:
                                    info.powerUps['antiCamo'] -= 1
                                for enemy in info.enemies:
                                    if enemy.camo:
                                        enemy.camo = False

                        if issubclass(type(info.selected), Towers):
                            if 295 <= mx <= 595 and 485 <= my <= 570:
                                n = (my - 485) // 30
                                if info.selected.upgrades[n] < 3:
                                    cost = type(info.selected).upgradePrices[n][info.selected.upgrades[n]]
                                    if info.coins >= cost and (info.wave >= info.selected.req or info.sandboxMode):
                                        info.coins -= cost
                                        info.statistics['coinsSpent'] += cost
                                        info.selected.upgrades[n] += 1

                            elif 620 <= mx < 770 and 545 <= my < 570:
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

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        price = {t.name: t.price for t in Towers.__subclasses__()}[info.placing]
                        info.coins += price
                        info.statistics['coinsSpent'] -= price
                        info.placing = ''

            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_UP]:
                info.shopScroll = min(0, info.shopScroll + 5)
            elif pressed[pygame.K_DOWN]:
                maxScroll = len([tower for tower in Towers.__subclasses__() if (info.wave >= tower.req or info.sandboxMode)]) * 80 - 450
                if maxScroll > 0:
                    info.shopScroll = max(-maxScroll, info.shopScroll - 5)

        elif info.status == 'statistics':
            scroll = 0

            while True:
                clock.tick(MaxFPS)

                mx, my = pygame.mouse.get_pos()

                screen.fill((200, 200, 200))

                centredPrint(mediumFont, 'General Statistics', (500, 20 - scroll))
                leftAlignPrint(font, f'Total Pops: {info.statistics["pops"]}', (20, 80 - scroll))
                leftAlignPrint(font, f'Towers Placed: {info.statistics["towersPlaced"]}', (20, 110 - scroll))
                leftAlignPrint(font, f'Towers Sold: {info.statistics["towersSold"]}', (20, 140 - scroll))
                leftAlignPrint(font, f'Enemies Missed: {info.statistics["enemiesMissed"]}', (20, 170 - scroll))
                leftAlignPrint(font, f'Coins Spent: {info.statistics["coinsSpent"]}', (20, 200 - scroll))

                centredPrint(mediumFont, 'Wins and Losses', (500, 240 - scroll))

                leftAlignPrint(font, f'Total Losses: {info.statistics["losses"]}', (20, 330 - scroll))

                numMaps = 0
                totalWins = 0
                for mapName, wins in info.statistics['wins'].items():
                    numMaps += 1
                    totalWins += wins

                    leftAlignPrint(font, f'{mapName}: {wins} ' + ('win' if wins == 1 else 'wins'),
                                   (20, 400 + 30 * numMaps - scroll))

                leftAlignPrint(font, f'Total Wins: {totalWins}', (20, 300 - scroll))
                if totalWins > 0:
                    centredPrint(mediumFont, 'Wins by map', (500, 370 - scroll))

                pygame.draw.rect(screen, (200, 200, 200), (0, 525, 1000, 75))

                pygame.draw.rect(screen, (255, 0, 0), (25, 550, 100, 30))
                centredPrint(font, 'Close', (75, 565))
                if 25 <= mx <= 125 and 550 <= my <= 580:
                    pygame.draw.rect(screen, (128, 128, 128), (25, 550, 100, 30), 3)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (25, 550, 100, 30), 3)

                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_UP]:
                    scroll = max(0, scroll - 2)
                if pressed[pygame.K_DOWN]:
                    scroll = min(scroll + 2, max(30 * numMaps - 85, 0))

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

fontType = 'Ubuntu Mono'
tinyFont = pygame.font.SysFont(fontType, 17)
font = pygame.font.SysFont(fontType, 20)
mediumFont = pygame.font.SysFont(fontType, 30)
largeFont = pygame.font.SysFont(fontType, 75)

pygame.display.set_caption('Tower Defense')
pygame.display.set_icon(pygame.image.load(os.path.join(resource_path, 'icon.png')))

screen.fill((200, 200, 200))
centredPrint(largeFont, f'Tower Defense v{__version__}', (500, 200), (100, 100, 100))
centredPrint(mediumFont, 'Loading...', (500, 300), (100, 100, 100))
pygame.display.update()

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
    '10' * 3,
    '16' * 25,
    '17' * 25,
    '18' * 25,
    '1A' * 2,
    '18' * 50,
    '18' * 75,
    '0A' * 3,
    '0A' * 5,
    '0A' * 8,
    '21' * 3,
    '25' * 25,
    '26' * 25,
    '27' * 25,
    '28' * 25,
    '0C',
    '0C' * 2,
    '0C' * 3,
    '0C' * 5,
    '0D'
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
    'C': (211, 47, 47),
    'D': (64, 64, 64)
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
    'A': 20,
    'B': 40,
    'C': 30,
    'D': 69
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
    'A': 1,     # True Speed: 1/3 (0.333...)
    'B': 1,     # True Speed: 1/5 (0.2)
    'C': 1,
    'D': 1      # True Speed: 1/2 (0.5)
}

onlyExplosiveTiers = [7, 8, 'D']

trueHP = {
    'A': 500,
    'B': 2000,
    'C': 1000,
    'D': 10000
}

bossCoins = {
    'A': 150,
    'B': 250,
    'C': 100,
    'D': 500
}

bossFreeze = {
    'A': 3,
    'B': 5,
    'C': 0,
    'D': 2
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
        'backgroundColor': '',
        'pathColor': '',
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
        'losses': 0,
        'coinsSpent': 0,
        'totalWins': 0,
        'mapsBeat': 0
    },
    'ticksSinceNoEnemies': 1,
    'achievements': {
        'pops': 0,
        'wins': 0,
        'spendCoins': 0,
        'beatMaps': 0
    },
    'mapsBeat': 0,
    'runes': [],
    'equippedRune': None,
    'newRunes': 0,
    'powerUps': {
        'lightning': 0,
        'spikes': 0,
        'antiCamo': 0
    }
}

achievementRequirements = {
    'beatMaps': {
        'attr': 'mapsBeat',
        'tiers': [1, math.floor(len(Maps) / 2), len(Maps)]
    },
    'pops': {
        'attr': 'pops',
        'tiers': [10000, 100000, 1000000]
    },
    'wins': {
        'attr': 'totalWins',
        'tiers': [5, 20, 50]
    },
    'spendCoins': {
        'attr': 'coinsSpent',
        'tiers': [10000, 100000, 1000000]
    }
}

achievements = {
    'beatMaps': {
        'names': ['First Map!', 'Map Conqueror', 'Master of The End'],
        'lore': 'Beat [%] unique maps!'
    },
    'pops': {
        'names': ['Balloon Popper', 'Balloon Fighter', 'Balloon Exterminator'],
        'lore': 'Pop [%] balloons!'
    },
    'wins': {
        'names': ['Tower-defense Rookie', 'Tower-defense Pro', 'Tower-defense Legend'],
        'lore': 'Win [%] games!'
    },
    'spendCoins': {
        'names': ['Money Spender', 'Rich Player', 'Millionaire!'],
        'lore': 'Spend [%] coins!'
    }
}

powerUps = {
    'lightning': pygame.image.load('resources/lightning_power_up.png'),
    'spikes': pygame.image.load('resources/spikes_power_up.png'),
    'antiCamo': pygame.image.load('resources/anti_camo_power_up.png')
}

LOCKED = 'LOCKED'

IceCircle = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'ice_circle.png')), (250, 250)).copy()
IceCircle.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)

rangeImages = []
possibleRanges = [0, 50, 100, 125, 130, 150, 160, 165, 175, 180, 200, 250, 400]
for possibleRange in possibleRanges:
    rangeImage = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'range.png')), (possibleRange * 2,) * 2)
    alphaImage = rangeImage.copy()
    alphaImage.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
    rangeImages.append(alphaImage)

towerImages = {}
for towerType in Towers.__subclasses__():
    try:
        split = towerType.imageName.split('.')
        section1 = '.'.join(split[:-1])
        section2 = split[-1]

        original = pygame.image.load(os.path.join(resource_path, towerType.imageName))
        try:
            original45 = pygame.image.load(os.path.join(resource_path, f'{section1}_45.{section2}'))

        except FileNotFoundError:
            if towerType.name == 'Inferno':
                towerImages[towerType.name] = [pygame.image.load(os.path.join(resource_path, towerType.imageName)), pygame.image.load(os.path.join(resource_path, 'inactive_' + towerType.imageName))]
            else:
                towerImages[towerType.name] = pygame.image.load(os.path.join(resource_path, towerType.imageName))

        else:
            towerImages[towerType.name] = []
            for n in range(4):
                towerImages[towerType.name].append(pygame.transform.rotate(original, 90 * n))
                towerImages[towerType.name].append(pygame.transform.rotate(original45, 90 * n))

    except FileNotFoundError:
        towerImages[towerType.name] = None

healthImage = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'heart.png')), (16, 16))

SIN45 = COS45 = math.sqrt(2) / 2

info = data()
RuneEffects = RuneEffect()
PowerUps = PhysicalPowerUp()
mouseTrail = []

rainbowColors = [[255, 0, 0], [0, 127, 0], [255, 255, 0], [0, 255, 0], [0, 0, 255], [46, 43, 95], [139, 0, 255]]
rainbowShift = [[0, 0.127, 0], [0.255, 0.127, 0], [-0.255, 0, 0], [0, -0.255, 0.255], [0.046, 0.043, -0.16], [0.093, -0.043, 0.16], [0.116, 0, -0.255]]
rainbowShiftCount = random.randint(0, 999)
rainbowShiftIndex = random.randint(0, 6)

if __name__ == '__main__':
    app()
    print('tower-defense.core: An unexpected error occured.')
