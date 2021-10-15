# Imports
import os
import glob
import math
import pytz
import time
import pickle
import pygame
import random

from typing import *
from _pickle import UnpicklingError

from tower_defense import __version__

curr_path = os.path.dirname(__file__)
resource_path = os.path.join(curr_path, 'resources')

screen = pygame.display.set_mode((1000, 600))
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()

tinyFont = pygame.font.Font(os.path.join(resource_path, 'fonts', 'UbuntuMono-Regular.ttf'), 17)
font = pygame.font.Font(os.path.join(resource_path, 'fonts', 'UbuntuMono-Regular.ttf'), 20)
mediumFont = pygame.font.Font(os.path.join(resource_path, 'fonts', 'UbuntuMono-Regular.ttf'), 30)
largeFont = pygame.font.Font(os.path.join(resource_path, 'fonts', 'UbuntuMono-Regular.ttf'), 75)


# Screen Printing Functions
def leftAlignPrint(font: pygame.font.Font, text: str, pos: Tuple[int], color: Tuple[int] = (0, 0, 0)) -> None:
    textObj = font.render(text, True, color)
    screen.blit(textObj, textObj.get_rect(center=[pos[0] + font.size(text)[0] / 2, pos[1]]))


def centredPrint(font: pygame.font.Font, text: str, pos: Tuple[int], color: Tuple[int] = (0, 0, 0)) -> None:
    textObj = font.render(text, True, color)
    screen.blit(textObj, textObj.get_rect(center=pos))


def rightAlignPrint(font: pygame.font.Font, text: str, pos: Tuple[int], color: Tuple[int] = (0, 0, 0)) -> None:
    textObj = font.render(text, True, color)
    screen.blit(textObj, textObj.get_rect(center=[pos[0] - font.size(text)[0] / 2, pos[1]]))


# Loading Screen
pygame.display.set_caption('Tower Defense')
pygame.display.set_icon(pygame.image.load(os.path.join(resource_path, 'icon.png')))

screen.fill((200, 200, 200))
centredPrint(largeFont, f'Tower Defense v{__version__}', (500, 200), (100, 100, 100))
centredPrint(mediumFont, 'Loading...', (500, 300), (100, 100, 100))
pygame.display.update()


# Sub-imports
from tower_defense.maps import *
from tower_defense.skins import *
from tower_defense.runes import *
from tower_defense.update import *
from tower_defense.powerups import *
from tower_defense.constants import *
from tower_defense.functions import *


# Classes
class data:
    def __init__(self):
        self.reset()

    def reset(self):
        for attr in playerAttrs:
            default = defaults[attr]

            if type(default) in [dict, list]:
                setattr(self, attr, default.copy())
            else:
                setattr(self, attr, default)

    def update(self):
        for attr in playerAttrs:
            default = defaults[attr]

            if not hasattr(self, attr):
                if type(default) in [dict, list]:
                    setattr(self, attr, default.copy())
                else:
                    setattr(self, attr, default)


class gameData:
    def __init__(self):
        for attr in gameAttrs:
            default = defaults[attr]
            if type(default) in [dict, list]:
                setattr(self, attr, default.copy())
            else:
                setattr(self, attr, default)

    def reset(self):
        for attr in gameAttrs:
            if attr in ['Map', 'FinalHP']:
                continue

            default = defaults[attr]
            if type(default) in [dict, list]:
                setattr(self, attr, default.copy())
            else:
                setattr(self, attr, default)

    def update(self):
        for attr in gameAttrs:
            default = defaults[attr]

            if not hasattr(self, attr):
                if type(default) in [dict, list]:
                    setattr(self, attr, default.copy())
                else:
                    setattr(self, attr, default)


class Towers:
    def __init__(self, x: int, y: int, *, overrideCamoDetect: bool = False, overrideAddToTowers: bool = False):
        global info

        self.x = x
        self.y = y
        self.timer = 0
        self.upgrades = [0, 0, 0, False]
        self.stun = 0
        self.hits = 0
        self.camoDetectionOverride = overrideCamoDetect
        self.ID = gameInfo.towersPlaced
        self.targeting = targetingCycle[0]

        if not overrideAddToTowers:
            gameInfo.towers.append(self)

    def draw(self):
        try:
            if towerImages[self.name] is not None:
                try:
                    screen.blit(towerImages[self.name], (self.x - 15, self.y - 15))
                except TypeError:
                    screen.blit(towerImages[self.name][self.getImageFrame()], (self.x - 15, self.y - 15))
            else:
                pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

        except AttributeError:
            pygame.draw.circle(screen, (200, 200, 200), (self.x, self.y), 15)

    def attack(self):
        pass

    def update(self):
        pass

    def getImageFrame(self):
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
        [75, 125, 175],
        1000
    ]
    upgradeNames = [
        ['Longer Range', 'Extreme Range', 'Ultra Range'],
        ['More Bullets', 'Bullet Rain', 'Double Bullets'],
        ['Explosive Shots', 'Camo Detection', 'Boss Shred'],
        'Spinning Shots'
    ]
    range = 100
    cooldown = 75
    bossDamage = 1
    explosiveRadius = 0
    totalAbilityCooldown = 3000

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.rotation = 0
        self.abilityData = {
            'tick': 0,
            'rotation': 0,
            'active': False
        }
        self.abilityCooldown = 0

    def attack(self):
        if self.abilityData['active']:
            if self.abilityData['tick'] <= 5:
                self.abilityData['tick'] += 1
            else:
                self.abilityData['tick'] = 0

                for n in range(2):
                    tx = self.x + 1000 * SINDEGREES[(self.abilityData['rotation'] + n * 180) % 360]
                    ty = self.y + 1000 * COSDEGREES[(self.abilityData['rotation'] + n * 180) % 360]
                    Projectile(self, self.x, self.y, tx, ty, bossDamage=self.bossDamage, explosiveRadius=self.explosiveRadius, removeRegen=canRemoveRegen(self))

                self.abilityData['rotation'] += 30
                if self.abilityData['rotation'] == 1800:
                    self.abilityData['rotation'] = 0
                    self.abilityData['active'] = False

        if self.stun > 0:
            self.stun -= 1
            return

        if self.timer >= getActualCooldown(self.x, self.y, self.cooldown):
            try:
                closest = getTarget(self, targeting=self.targeting)
                proj = Projectile(self, self.x, self.y, closest.x, closest.y, bossDamage=self.bossDamage, explosiveRadius=self.explosiveRadius, removeRegen=canRemoveRegen(self))
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
        if self.abilityCooldown < self.totalAbilityCooldown:
            self.abilityCooldown += 1

        self.range = [100, 130, 165, 200][self.upgrades[0]]
        self.cooldown = [60, 35, 20, 10][self.upgrades[1]]
        self.bossDamage = 20 if self.upgrades[2] == 3 else 1
        self.explosiveRadius = 30 if self.upgrades[2] >= 1 else 0

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
                screen.blit(IceCircle, (self.x - 37.5, self.y - 37.5))

        def freeze(self):
            self.visibleTicks = 50

            for enemy in gameInfo.enemies:
                if abs(enemy.x - self.x) ** 2 + abs(enemy.y - self.y) ** 2 <= 8100:
                    if enemy.tier not in freezeImmune:
                        enemy.freezeTimer = max(enemy.freezeTimer, self.freezeDuration)
                        enemy.kill(coinMultiplier=getCoinMultiplier(self.parent))
                        self.parent.hits += 1

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
        [30, 125, 50],
        250
    ]
    upgradeNames = [
        ['Longer Range', 'Extreme Range', 'Ultra Range'],
        ['Lesser Cooldown', 'Snowball Shower', 'Heavy Snowfall'],
        ['Longer Freeze', 'Snowstorm Circle', 'Ultra Freeze'],
        'Blizzard'
    ]
    range = 150
    cooldown = 100
    freezeDuration = 20
    snowCircleTimer = 0
    totalAbilityCooldown = 3000

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.snowCircle = self.SnowStormCircle(self, self.x, self.y)
        self.enabled = True
        self.abilityData = {
            'active': False
        }
        self.abilityCooldown = 0

    def draw(self):
        super().draw()
        self.snowCircle.draw()

    def attack(self):
        if self.abilityData['active']:
            for enemy in gameInfo.enemies:
                enemy.freezeTimer = max(300, enemy.freezeTimer)
            self.abilityData['active'] = False

        if self.stun > 0:
            self.stun -= 1
            return

        if self.timer >= getActualCooldown(self.x, self.y, self.cooldown):
            if not self.enabled:
                return

            try:
                closest = getTarget(self, targeting=self.targeting)
                Projectile(self, self.x, self.y, closest.x, closest.y, freezeDuration=self.freezeDuration, removeRegen=canRemoveRegen(self))
                self.timer = 0

            except AttributeError:
                pass

        else:
            self.timer += 1

            if not self.enabled:
                return

        if self.upgrades[2] >= 2:
            if self.snowCircleTimer >= self.cooldown * 2.5:
                self.snowCircle.freeze()
                self.snowCircleTimer = 0
            else:
                self.snowCircleTimer += 1

    def update(self):
        if self.abilityCooldown < self.totalAbilityCooldown:
            self.abilityCooldown += 1

        self.snowCircle.update()
        self.range = [150, 180, 200, 250][self.upgrades[0]]
        self.cooldown = [50, 38, 27, 20][self.upgrades[1]]
        self.freezeDuration = [20, 45, 45, 75][self.upgrades[2]]


class SpikeTower(Towers):
    class Spike:
        def __init__(self, parent, angle: int, pierce: int = 1):
            self.parent = parent
            self.x = self.parent.x
            self.y = self.parent.y
            self.angle = angle
            self.dx = SINDEGREES[angle]
            self.dy = COSDEGREES[angle]
            self.visible = False
            self.ignore = []
            self.pierce = pierce
            self.maxPierce = pierce

        def move(self):
            if not self.visible or (getTarget(self.parent) is None and [self.x, self.y] == [self.parent.x, self.parent.y]):
                return

            self.x += self.dx * self.parent.projectileSpeed
            self.y += self.dy * self.parent.projectileSpeed

            for enemy in gameInfo.enemies:
                if enemy in self.ignore:
                    continue

                if enemy.tier in resistant:
                    continue

                if enemy.tier in onlyExplosiveTiers and self.parent.upgrades[2] < 2:
                    continue

                if abs(enemy.x - self.x) ** 2 + abs(enemy.y - self.y) ** 2 < (729 if enemy.isBoss else 196):
                    self.pierce -= 1
                    if self.pierce <= 0:
                        self.visible = False
                        self.pierce = self.maxPierce

                    if self.parent.upgrades[2] == 3:
                        enemy.fireTicks = max(enemy.fireTicks, 300)
                        enemy.fireIgnitedBy = self.parent

                    color = enemyColors[str(enemy.tier)]

                    if self.parent.upgrades[2] == 0:
                        damage = 1
                    else:
                        damage = 2

                    toDamage = [enemy]
                    for n in range(damage):
                        newToDamage = []

                        for e in toDamage:
                            newToDamage += e.kill(coinMultiplier=getCoinMultiplier(self.parent), overrideRuneColor=color)

                            if not info.sandboxMode:
                                info.statistics['pops'] += 1
                            self.parent.hits += 1

                            for eTD in newToDamage:
                                self.ignore.append(eTD)

                        toDamage = newToDamage

        def draw(self):
            if not self.visible:
                return

            pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), 2)

        def update(self):
            self.maxPierce = self.parent.pierce

    class Spikes:
        def __init__(self, parent):
            self.parent = parent
            self.spikes = []

            for n in range(8):
                self.spikes.append(SpikeTower.Spike(self.parent, n * 45))

        def moveSpikes(self, overrideRange: int = None):
            if overrideRange is None:
                towerRange = self.parent.range
            else:
                towerRange = overrideRange

            for spike in self.spikes:
                spike.move()

                if abs(spike.x - self.parent.x) ** 2 + abs(spike.y - self.parent.y) ** 2 >= towerRange ** 2:
                    spike.visible = False

        def drawSpikes(self):
            for spike in self.spikes:
                spike.draw()

        def update(self):
            for spike in self.spikes:
                spike.update()

    name = 'Spike Tower'
    imageName = 'spike_tower.png'
    color = (224, 17, 95)
    req = 2
    price = 125
    upgradePrices = [
        [50, 150, 250],
        [100, 500, 2500],
        [100, 125, 200],
        5000
    ]
    upgradeNames = [
        ['Fast Spikes', 'Hyperspeed Spikes', 'Bullet-like Speed'],
        ['Shorter Cooldown', 'Super Reloading', 'Hyper Reloading'],
        ['Double Damage', 'Lead-pierce', 'Burning Spikes'],
        'Sharper Spikes'
    ]
    range = 50
    projectileSpeed = 1
    cooldown = 100
    pierce = 1
    totalAbilityCooldown = 3000

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.spikes = SpikeTower.Spikes(self)
        self.abilityData = {
            'active': True,
            'ticks': 0
        }
        self.abilityCooldown = 0

    def draw(self):
        self.spikes.drawSpikes()
        super().draw()

    def attack(self):
        if self.stun > 0:
            self.stun -= 1
            return

        if True in [s.visible for s in self.spikes.spikes]:
            self.spikes.moveSpikes()

        elif self.timer >= getActualCooldown(self.x, self.y, self.cooldown):
            for spike in self.spikes.spikes:
                spike.visible = True
                spike.x = self.x
                spike.y = self.y
                spike.ignore = []
            self.timer = 0

        else:
            self.timer += 1

    def update(self):
        if self.abilityCooldown < self.totalAbilityCooldown:
            self.abilityCooldown += 1

        if self.abilityData['active']:
            if self.abilityData['ticks'] <= 750:
                self.abilityData['ticks'] += 1
                self.pierce = 3
            else:
                self.abilityData['ticks'] = 0
                self.abilityData['active'] = False
                self.pierce = 1

        self.projectileSpeed = [1, 1.5, 2.2, 3][self.upgrades[0]]
        self.cooldown = [100, 35, 10, 5][self.upgrades[1]]


class BombTower(Towers):
    name = 'Bomb Tower'
    imageName = 'bomb_tower.png'
    color = (0, 0, 0)
    req = 4
    price = 100
    upgradePrices = [
        [30, 50, 75],
        [20, 35, 50],
        [75, 425, 50],
        1000
    ]
    upgradeNames = [
        ['Longer Range', 'Extra Range', 'Ultra Range'],
        ['More Bombs', 'Heavy Fire', 'Twin-Fire'],
        ['Larger Explosions', 'Anti-Regen Grenade', '2x Impact Damage'],
        'Enemy Incineration'
    ]
    range = 50
    cooldown = 200
    explosionRadius = 30
    fireTicks = 0
    impactDamage = 1
    totalAbilityCooldown = 4500

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.abilityData = {
            'active': False,
            'ticks': 0
        }
        self.abilityCooldown = 0

    def attack(self):
        if self.abilityData['active']:
            if self.abilityData['ticks'] == 0:
                for enemy in gameInfo.enemies:
                    if abs(enemy.x - self.x) ** 2 + abs(enemy.y - self.y) ** 2 <= self.range ** 2:
                        enemy.kill(coinMultiplier=getCoinMultiplier(self), bossDamage=50, ignoreRegularEnemyHealth=True)
                for enemy in gameInfo.enemies:
                    if abs(enemy.x - self.x) ** 2 + abs(enemy.y - self.y) ** 2 <= self.range ** 2:
                        enemy.kill(coinMultiplier=getCoinMultiplier(self), bossDamage=50, ignoreRegularEnemyHealth=True)
                for enemy in gameInfo.enemies:
                    if abs(enemy.x - self.x) ** 2 + abs(enemy.y - self.y) ** 2 <= self.range ** 2:
                        enemy.kill(coinMultiplier=getCoinMultiplier(self), bossDamage=50, ignoreRegularEnemyHealth=True)

                self.abilityData['ticks'] = 1

            elif self.abilityData['ticks'] <= 100:
                self.abilityData['ticks'] += 1

            else:
                self.abilityData['ticks'] = 0
                self.abilityData['active'] = False

        if self.stun > 0:
            self.stun -= 1
            return

        if self.timer >= getActualCooldown(self.x, self.y, self.cooldown):
            try:
                closest = getTarget(self, targeting=self.targeting)

                Projectile(self, self.x, self.y, closest.x, closest.y, removeRegen=self.removeRegen, impactDamage=self.impactDamage, explosiveRadius=self.explosionRadius)
                if self.upgrades[1] == 3:
                    twin = Projectile(self, self.x, self.y, closest.x, closest.y, removeRegen=self.removeRegen, impactDamage=self.impactDamage, explosiveRadius=self.explosionRadius)
                    for n in range(5):
                        twin.move()

                self.timer = 0

            except AttributeError:
                pass
        else:
            self.timer += 1

    def update(self):
        if self.abilityCooldown < self.totalAbilityCooldown:
            self.abilityCooldown += 1

        self.range = [50, 100, 150, 200][self.upgrades[0]]
        self.cooldown = [100, 50, 25, 25][self.upgrades[1]]
        self.explosionRadius = [30, 60, 75, 75][self.upgrades[2]]
        self.impactDamage = 2 if self.upgrades[2] == 3 else 1
        self.removeRegen = self.upgrades[2] >= 2 or canRemoveRegen(self)

    def draw(self):
        super().draw()
        if self.abilityData['active']:
            centredBlit(explosionImages[possibleRanges.index(self.range)], (self.x, self.y))


class BananaFarm(Towers):
    name = 'Banana Farm'
    imageName = 'banana_farm.png'
    color = (255, 255, 0)
    req = 4
    price = 150
    upgradePrices = [
        [30, 50, 65],
        [30, 45, 60],
        [50, 150, 300],
        1000
    ]
    upgradeNames = [
        ['Banana Cannon', 'More Banana Shots', 'Super Range'],
        ['Increased Income', 'Money Farm', 'Money Factory'],
        ['25% More Coins', '50% More Coins', 'Double Coins'],
        'Backup Cash'
    ]
    range = 100
    cooldown = 0
    totalAbilityCooldown = 4500

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.abilityData = {
            'active': False
        }
        self.abilityCooldown = 0

    def attack(self):
        if self.stun > 0:
            self.stun -= 1
            return

        if self.upgrades[0] >= 1:
            if self.timer >= getActualCooldown(self.x, self.y, self.cooldown):
                try:
                    closest = getTarget(self, targeting=self.targeting)
                    Projectile(self, self.x, self.y, closest.x, closest.y, removeRegen=canRemoveRegen(self))
                    self.timer = 0

                except AttributeError:
                    pass
            else:
                self.timer += 1

    def update(self):
        if self.abilityCooldown < self.totalAbilityCooldown:
            self.abilityCooldown += 1

        if self.abilityData['active']:
            profit = random.randint(1000, 5000)
            gameInfo.coins += profit
            self.abilityData['active'] = False

        self.cooldown = [0, 50, 25, 25][self.upgrades[0]]
        if self.upgrades[0] == 3:
            self.range = 150


class Bowler(Towers):
    name = 'Bowler'
    imageName = 'bowler.png'
    color = (64, 64, 64)
    req = 5
    price = 100
    upgradePrices = [
        [20, 40, 60],
        [20, 45, 80],
        [25, 50, 100],
        225
    ]
    upgradeNames = [
        ['Faster Rocks', 'Double Damage', 'Snipe'],
        ['More Rocks', 'Double Rocks', 'Infini-Rocks'],
        ['5 Enemies Pierce', '20 Enemies Pierce', '50 Enemies Pierce'],
        'Damage Buff'
    ]
    range = 0
    cooldown = 300
    pierce = 3
    totalAbilityCooldown = 4500

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.abilityData = {
            'active': False,
            'ticks': 0
        }
        self.abilityCooldown = 0

    def attack(self):
        if self.abilityData['active']:
            if self.abilityData['ticks'] <= 500:
                self.abilityData['ticks'] += 1
            else:
                self.abilityData['active'] = False
                self.abilityData['ticks'] = 0

        if self.stun > 0:
            self.stun -= 1
            return

        if self.timer >= getActualCooldown(self.x, self.y, self.cooldown):
            try:
                for direction in ['left', 'right', 'up', 'down']:
                    PiercingProjectile(self, self.x, self.y, self.pierce, direction)
                self.timer = 0

            except AttributeError:
                pass
        else:
            self.timer += 1

    def update(self):
        if self.abilityCooldown < self.totalAbilityCooldown:
            self.abilityCooldown += 1

        self.cooldown = [300, 200, 150, 100][self.upgrades[1]]
        self.pierce = [3, 5, 20, 50][self.upgrades[2]]


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

        def attack(self, bossDamage: int = 25):
            pops = 0
            self.visibleTicks = 50
            self.t1 = getTarget(Towers(self.parent.x, self.parent.y, overrideCamoDetect=self.parent.upgrades[1] >= 2, overrideAddToTowers=True), targeting=self.parent.targeting, overrideRange=1000)
            if type(self.t1) is Enemy:
                self.t1.kill(coinMultiplier=getCoinMultiplier(self.parent), bossDamage=bossDamage)
                self.parent.hits += 1
                pops += 1
                self.t2 = getTarget(Towers(self.t1.x, self.t1.y, overrideCamoDetect=self.parent.upgrades[1] >= 2, overrideAddToTowers=True), ignore=[self.t1], targeting=self.parent.targeting, overrideRange=1000)

                if type(self.t2) is Enemy:
                    self.t2.kill(coinMultiplier=getCoinMultiplier(self.parent), bossDamage=bossDamage)
                    self.parent.hits += 1
                    pops += 1
                    self.t3 = getTarget(Towers(self.t2.x, self.t2.y, overrideCamoDetect=self.parent.upgrades[1] >= 2, overrideAddToTowers=True), ignore=[self.t1, self.t2], targeting=self.parent.targeting, overrideRange=1000)

                    if type(self.t3) is Enemy:
                        self.t3.kill(coinMultiplier=getCoinMultiplier(self.parent), bossDamage=bossDamage)
                        self.parent.hits += 1
                        pops += 1
                        if self.parent.upgrades[1] == 3:
                            self.t4 = getTarget(Towers(self.t3.x, self.t3.y, overrideCamoDetect=self.parent.upgrades[1] >= 2, overrideAddToTowers=True), ignore=[self.t1, self.t2, self.t3], targeting=self.parent.targeting, overrideRange=1000)

                            if type(self.t4) is Enemy:
                                self.t4.kill(coinMultiplier=getCoinMultiplier(self.parent), bossDamage=bossDamage)
                                self.parent.hits += 1
                                pops += 1
                                self.t5 = getTarget(Towers(self.t4.x, self.t4.y, overrideCamoDetect=self.parent.upgrades[1] >= 2, overrideAddToTowers=True), ignore=[self.t1, self.t2, self.t3, self.t4], targeting=self.parent.targeting, overrideRange=1000)

                                if type(self.t5) is Enemy:
                                    self.t5.kill(coinMultiplier=getCoinMultiplier(self.parent), bossDamage=bossDamage)
                                    self.parent.hits += 1
                                    pops += 1
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

            info.statistics['pops'] += pops

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
        [50, 65, 90],
        500
    ]
    upgradeNames = [
        ['Longer Range', 'Extreme Range', 'Magic Healing'],
        ['Lighning Zap', 'Wisdom of Camo', '5-hit Lightning'],
        ['Big Blast Radius', 'Faster Reload', 'Hyper Reload'],
        'Mega Heal'
    ]
    range = 125
    cooldown = 100
    totalAbilityCooldown = 7500

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.lightning = self.LightningBolt(self)
        self.lightningTimer = 0
        self.healTimer = 0
        self.abilityData = {
            'active': False
        }
        self.abilityCooldown = 0

    def draw(self):
        super().draw()
        self.lightning.draw()

    def attack(self):
        if self.stun > 0:
            self.stun -= 1
            return

        if self.timer >= getActualCooldown(self.x, self.y, self.cooldown):
            try:
                closest = getTarget(self, targeting=self.targeting)
                Projectile(self, self.x, self.y, closest.x, closest.y, explosiveRadius=60 if self.upgrades[2] else 30, removeRegen=canRemoveRegen(self))
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
        if self.abilityCooldown < self.totalAbilityCooldown:
            self.abilityCooldown += 1

        if self.upgrades[0] == 3:
            if self.healTimer >= 1000 and gameInfo.HP < 250:
                gameInfo.HP += 1
                self.healTimer = 0
            else:
                self.healTimer += 1

        if self.abilityData['active']:
            self.abilityData['active'] = False
            gameInfo.HP = min(300, gameInfo.HP + 25)

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
            for enemy in gameInfo.enemies:
                if (abs(enemy.x - self.parent.x) ** 2 + abs(enemy.y - self.parent.y) ** 2 <= self.parent.range ** 2) and (not enemy.camo or canSeeCamo(self.parent)):
                    enemy.fireTicks = max(enemy.fireTicks, (500 if self.parent.upgrades[2] else 300))
                    enemy.fireIgnitedBy = self.parent
                    if not enemy.isBoss:
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
        [150, 200, 275],
        1000
    ]
    upgradeNames = [
        ['Longer Range', 'Extreme Range', 'Ultra Range'],
        ['Shortened Cooldown', 'More Infernoes', 'Hyper Infernoes'],
        ['Longer Burning', 'Firey Stun', 'Longer Stun'],
        'Strong Shock Wave'
    ]
    range = 100
    cooldown = 500
    totalAbilityCooldown = 6000

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.inferno = self.Inferno(self)
        self.abilityData = {
            'active': False
        }
        self.abilityCooldown = 0

    def draw(self):
        self.inferno.draw()
        super().draw()

    def attack(self):
        if self.abilityData['active']:
            for enemy in gameInfo.enemies:
                enemy.freezeTimer = max(enemy.freezeTimer, 1000)
                self.inferno.renders.append(self.AttackRender(self, enemy))
                enemy.fireTicks = max(enemy.fireTicks, 500)
                enemy.fireIgnitedBy = self

            self.abilityData['active'] = False

        if self.stun > 0:
            self.stun -= 1
            return

        if self.timer >= getActualCooldown(self.x, self.y, self.cooldown):
            self.inferno.attack()
            self.timer = 0
        else:
            self.timer += 1

    def update(self):
        if self.abilityCooldown < self.totalAbilityCooldown:
            self.abilityCooldown += 1

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

        def attack(self, overrideExplosiveRadius: int = None):
            closest = getTarget(Towers(self.x, self.y, overrideAddToTowers=True), targeting=self.parent.targeting, overrideRange=self.parent.range)
            if closest is None:
                self.parent.timer = 100
            else:
                if overrideExplosiveRadius is not None:
                    explosiveRadius = overrideExplosiveRadius
                else:
                    explosiveRadius = 30 if self.parent.upgrades[0] >= 2 else 0

                Projectile(self.parent, self.x, self.y, closest.x, closest.y, explosiveRadius=explosiveRadius, removeRegen=canRemoveRegen(self.parent))

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
                        closest = getTarget(Towers(self.x, self.y, overrideAddToTowers=True), targeting=self.parent.targeting, overrideRange=self.parent.range, ignore=self.parent.targets)
                        if closest is None:
                            self.tx = self.parent.x
                            self.ty = self.parent.y
                        else:
                            self.tx = closest.x
                            self.ty = closest.y
                            self.target = closest
                            self.moveCooldown = 0
                            self.parent.targets = [villager.target for villager in self.parent.villagers]

                    elif getTarget(Towers(self.x, self.y, overrideAddToTowers=True), targeting=self.parent.targeting, overrideRange=self.parent.range) is None or (self.x - self.parent.x) ** 2 + (self.y - self.parent.y) ** 2 < 625:
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
        [100, 125, 775],
        [50, 75, 100],
        5000
    ]
    upgradeNames = [
        ['Anti-Camo', 'Bomber Villagers', 'Turret Villagers'],
        ['Longer Range', 'Extreme Range', 'Anti-Regen'],
        ['Two Villagers', 'Three Villagers', 'Four Villagers'],
        'Elemental'
    ]
    range = 100
    cooldown = 100
    totalAbilityCooldown = 0

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.villagers = [self.Villager(self)]
        self.targets = []
        self.abilityData = {
            'active': False,
            'ticks': 0
        }
        self.abilityCooldown = 0

    def draw(self):
        for villager in self.villagers:
            villager.draw()
        super().draw()

    def attack(self):
        for villager in self.villagers:
            if villager.timer >= getActualCooldown(self.x, self.y, self.cooldown):
                villager.attack()
                villager.timer = 0
            else:
                villager.timer += 1

    def update(self):
        if self.abilityCooldown < self.totalAbilityCooldown:
            self.abilityCooldown += 1

        if self.abilityData['active']:
            if self.abilityData['ticks'] <= 1000:
                self.abilityData['ticks'] += 1
            else:
                self.abilityData['ticks'] = 0
                self.abilityData['active'] = False

        self.cooldown = [50, 50, 50, 20][self.upgrades[0]]
        self.range = [100, 125, 150, 150][self.upgrades[1]]
        self.targets = [villager.target for villager in self.villagers]

        for villager in self.villagers:
            villager.move()

        if len(self.villagers) <= self.upgrades[2]:
            self.villagers.append(self.Villager(self))


class Sniper(Towers):
    name = 'Sniper'
    imageName = 'sniper.png'
    color = (64, 255, 64)
    req = 15
    price = 250
    upgradePrices = [
        [150, 400, 1000],
        [100, 200, 450],
        [125, 250, 400],
        5000
    ]
    upgradeNames = [
        ['Faster Reload', 'Semi-automatic Gun', 'Super Sniper'],
        ['Anti-boss Rifle', 'Boss Shredder', 'Ultimate Slayer'],
        ['Radar Goggles', 'Lead-Pierce', 'Ceramic Destroyer'],
        'Elite Sniper'
    ]
    range = 0
    cooldown = 50
    bossDamage = 2
    ceramDamage = 1
    totalAbilityCooldown = 6000

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.rotation = 0
        self.abilityData = {
            'tick': 0,
            'active': False
        }
        self.abilityCooldown = 0
        self.rifleFireTicks = 0

    def attack(self):
        if self.stun > 0:
            self.stun -= 1
            return

        if self.timer >= getActualCooldown(self.x, self.y, self.cooldown):
            try:
                target = getTarget(self, targeting=self.targeting, overrideRange=1000)
                if (target.tier in onlyExplosiveTiers and self.upgrades[2] >= 2) or target.tier not in onlyExplosiveTiers:
                    if self.abilityData['active']:
                        if target.isBoss:
                            target.kill(coinMultiplier=getCoinMultiplier(self), bossDamage=self.bossDamage * 3)
                            self.hits += self.bossDamage * 3

                        else:
                            try:
                                gameInfo.enemies.remove(target)
                                gameInfo.coins += getCoinMultiplier(self)
                                info.statistics['pops'] += 1
                                self.hits += 1

                            except ValueError:
                                pass

                    else:
                        HP = 1
                        if target.isBoss:
                            HP = target.HP

                        spawn = target.kill(coinMultiplier=getCoinMultiplier(self), bossDamage=self.bossDamage, ceramDamage=self.ceramDamage)
                        self.hits += min(HP, self.bossDamage)

                    self.rifleFireTicks = 10

                proj = Projectile(self, self.x, self.y, target.x, target.y, overrideAddToProjectiles=True)
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
        if self.abilityData['active']:
            if self.abilityData['tick'] <= 500:
                self.abilityData['tick'] += 1
            else:
                self.abilityData['active'] = False
                self.abilityData['tick'] = 0

        if self.abilityCooldown < self.totalAbilityCooldown:
            self.abilityCooldown += 1

        self.cooldown = [50, 25, 10, 5][self.upgrades[0]]
        self.bossDamage = [2, 4, 8, 12][self.upgrades[1]]
        self.ceramDamage = 20 if self.upgrades[2] == 3 else 1

    def draw(self):
        super().draw()
        if self.rifleFireTicks > 0:
            dx = [0, 7, 14, 7, 0, -7, -14, -7][self.rotation]
            dy = [14, 7, 0, -7, -14, -7, 0, 7][self.rotation]

            pygame.draw.circle(screen, (255, 128, 0), (self.x + dx, self.y + dy), 3)

            self.rifleFireTicks -= 1

    def getImageFrame(self) -> int:
        return self.rotation


class Elemental(Towers):
    name = 'Elemental'
    imageName = 'elemental.png'
    color = (255, 150, 0)
    req = math.inf
    range = 250
    totalAbilityCooldown = 7500
    price = 10000
    upgradeNames = [None, None, None, 'ELEMENTS ASSEMBLE']

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.inferno = InfernoTower.Inferno(self)
        self.lightning = Wizard.LightningBolt(self)
        self.abilityCooldown = 7500
        self.abilityData = {
            'tick': 0,
            'rotation': 0,
            'active': True
        }
        self.infernoTimer = 0
        self.lightningTimer = 0

        self.upgrades = [3, 3, 3, True]

    def draw(self):
        self.inferno.draw()
        self.lightning.draw()

        super().draw()

    def attack(self):
        if self.abilityData['active']:
            if self.abilityData['tick'] <= 5:
                self.abilityData['tick'] += 1
            else:
                self.abilityData['tick'] = 0

                tx = self.x + 1000 * SINDEGREES[self.abilityData['rotation'] % 360]
                ty = self.y + 1000 * COSDEGREES[self.abilityData['rotation'] % 360]
                Projectile(self, self.x, self.y, tx, ty, freezeDuration=100, removeRegen=canRemoveRegen(self))

                tx = self.x + 1000 * SINDEGREES[(self.abilityData['rotation'] + 180) % 360]
                ty = self.y + 1000 * COSDEGREES[(self.abilityData['rotation'] + 180) % 360]
                Projectile(self, self.x, self.y, tx, ty, bossDamage=100, explosiveRadius=50, removeRegen=canRemoveRegen(self))

                self.abilityData['rotation'] += 30
                if self.abilityData['rotation'] == 1800:
                    self.abilityData['rotation'] = 0
                    self.abilityData['active'] = False

        if self.stun > 0:
            self.stun -= 1
            return

        if self.timer >= getActualCooldown(self.x, self.y, 1):
            closest = getTarget(self, targeting=self.targeting)
            try:
                Projectile(self, self.x, self.y, closest.x, closest.y, explosiveRadius=50, bossDamage=25, fireTicks=300, removeRegen=canRemoveRegen(self))
                twin = Projectile(self, self.x, self.y, closest.x, closest.y, bossDamage=100, freezeDuration=100, removeRegen=canRemoveRegen(self))
                twin.move(7)
                self.timer = 0
            except AttributeError:
                pass
        else:
            self.timer += 1

        if self.lightningTimer >= getActualCooldown(self.x, self.y, 100):
            self.lightning.attack(250)
            self.lightningTimer = 0
        else:
            self.lightningTimer += 1

        if self.infernoTimer >= getActualCooldown(self.x, self.y, 250):
            found = False
            for enemy in gameInfo.enemies:
                if abs(enemy.x - self.x) ** 2 + abs(enemy.y - self.y) ** 2 <= self.range ** 2:
                    enemy.fireTicks = max(enemy.fireTicks, 200)
                    enemy.fireIgnitedBy = self
                    if not enemy.isBoss:
                        enemy.freezeTimer = max(enemy.freezeTimer, 75)

                    self.inferno.renders.append(InfernoTower.AttackRender(self, enemy))
                    found = True

            if found:
                self.infernoTimer = 0
        else:
            self.infernoTimer += 1

    def update(self):
        if self.abilityCooldown < self.totalAbilityCooldown:
            self.abilityCooldown += 1


class Projectile:
    def __init__(self, parent: Towers, x: int, y: int, tx: int, ty: int, *, explosiveRadius: int = 0, freezeDuration: int = 0, bossDamage: int = 1, impactDamage: int = 1, fireTicks: int = 0, overrideAddToProjectiles: bool = False, removeRegen: bool = False):
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
        self.removeRegen = removeRegen

        if not overrideAddToProjectiles:
            gameInfo.projectiles.append(self)

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
                gameInfo.projectiles.remove(self)
            except ValueError:
                pass

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 3)

    def explode(self, centre):
        for enemy in gameInfo.enemies:
            if enemy == centre:
                continue

            if abs(enemy.x - self.x) ** 2 + abs(enemy.y - self.y) ** 2 < self.explosiveRadius ** 2:
                if self.fireTicks > 0:
                    enemy.fireTicks = self.fireTicks
                    enemy.fireIgnitedBy = self.parent

                if self.removeRegen:
                    enemy.regen = False

                enemy.kill(coinMultiplier=getCoinMultiplier(self.parent))
                self.parent.hits += 1
                if not info.sandboxMode:
                    info.statistics['pops'] += 1


class PiercingProjectile:
    def __init__(self, parent: Towers, x: int, y: int, pierceLimit: int, direction: str, *, speed: int = 2, overrideAddToPiercingProjectiles: bool = False):
        if not overrideAddToPiercingProjectiles:
            gameInfo.piercingProjectiles.append(self)

        self.parent = parent
        self.coinMultiplier = getCoinMultiplier(self.parent)
        self.x = x
        self.y = y
        self.pierce = pierceLimit
        self.direction = direction
        self.ignore = []
        self.movement = 0
        self.speed = speed

        self.damageMultiplier = 1
        if type(parent) is Bowler:
            if parent.abilityData['active']:
                self.damageMultipler = 2 * self.damageMultiplier

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
            gameInfo.piercingProjectiles.remove(self)

    def draw(self):
        pygame.draw.circle(screen, (16, 16, 16), (self.x, self.y), 5)


class Enemy:
    def __init__(self, tier: str or int, lineIndex: int, maxRegenTier: str or int, *, spawn: List[int] = None, mapPath: int = 0, camo: bool = False, regen: bool = False, fortified: bool = False):
        self.tier = tier

        self.lineIndex = lineIndex

        self.mapPath = mapPath
        self.totalMovement = 0
        self.totalPathLength = gameInfo.Map.pathLengths[self.mapPath]
        if spawn is None:
            self.x, self.y = gameInfo.Map.path[self.mapPath][0]
        else:
            self.x, self.y = spawn

        self.maxRegenTier = str(maxRegenTier)

        self.freezeTimer = 0
        self.bossFreeze = 0
        self.fireTicks = 0
        self.fireIgnitedBy = None
        self.isBoss = self.tier in bosses
        self.reachedEnd = False

        self.camo = camo
        self.regen = regen
        self.regenTimer = 0
        self.fortified = fortified

        if str(self.tier) in trueHP.keys():
            self.HP = self.MaxHP = trueHP[str(self.tier)]
        else:
            self.HP = self.MaxHP = 1

        if self.fortified:
            self.HP = 3 * self.HP
            self.MaxHP = 3 * self.MaxHP

        self.direction = None
        self.move(1)

        if self.tier in forceCamo:
            self.camo = True

        gameInfo.enemies.append(self)

    def move(self, speed: int):
        self.update()

        if self.freezeTimer > 0 and not str(self.tier) in freezeImmune:
            self.freezeTimer -= 1
        elif self.bossFreeze > 0:
            self.bossFreeze -= 1
        else:
            for n in range(speed):
                if len(gameInfo.Map.path[self.mapPath]) - 1 == self.lineIndex:
                    if not self.reachedEnd:
                        self.kill(coinMultiplier=0, spawnNew=False, ignoreBoss=True, ignoreRegularEnemyHealth=True)
                        info.statistics['enemiesMissed'] += 1
                        gameInfo.HP -= damages[str(self.tier)]
                        self.reachedEnd = True
                        break

                else:
                    current = gameInfo.Map.path[self.mapPath][self.lineIndex]
                    new = gameInfo.Map.path[self.mapPath][self.lineIndex + 1]
                    foundMove = False
                    newLineIndex = self.lineIndex + 1

                    right = current[0] < new[0]
                    left = current[0] > new[0]
                    up = current[1] < new[1]
                    down = current[1] > new[1]

                    if current != new:
                        if current[0] == new[0] or current[1] == new[1]:
                            s = 1
                        else:
                            s = RECIPROCALSQRT2

                        if right:
                            self.x += s
                            if self.x >= new[0]:
                                self.lineIndex = newLineIndex
                                self.x, self.y = gameInfo.Map.path[self.mapPath][newLineIndex]

                            foundMove = True

                        if left:
                            self.x -= s
                            if self.x <= new[0]:
                                self.lineIndex = newLineIndex
                                self.x, self.y = gameInfo.Map.path[self.mapPath][newLineIndex]

                            foundMove = True

                        if up:
                            self.y += s
                            if self.y >= new[1]:
                                self.lineIndex = newLineIndex
                                self.x, self.y = gameInfo.Map.path[self.mapPath][newLineIndex]

                            foundMove = True

                        if down:
                            self.y -= s
                            if self.y <= new[1]:
                                self.lineIndex = newLineIndex
                                self.x, self.y = gameInfo.Map.path[self.mapPath][newLineIndex]

                            foundMove = True

                    if up and right:
                        self.direction = 7
                    elif up and left:
                        self.direction = 5
                    elif down and right:
                        self.direction = 1
                    elif down and left:
                        self.direction = 3
                    elif up:
                        self.direction = 6
                    elif down:
                        self.direction = 2
                    elif left:
                        self.direction = 4
                    elif right:
                        self.direction = 0

                    if foundMove:
                        self.totalMovement += s
                    else:
                        self.kill(coinMultiplier=0, spawnNew=False, ignoreBoss=True, ignoreRegularEnemyHealth=True)
                        info.statistics['enemiesMissed'] += 1

                self.update()

            try:
                self.bossFreeze = bossFreezes[self.tier]
            except KeyError:
                pass

    def update(self):
        if self.reachedEnd:
            self.kill(coinMultiplier=0, spawnNew=False, ignoreBoss=True, ignoreRegularEnemyHealth=True)
            info.statistics['enemiesMissed'] += 1

        if self.fireTicks > 0:
            if self.fireTicks % 100 == 0:
                new = self.kill(burn=True, reduceFireTicks=True)
                self.fireIgnitedBy.hits += 1

                if not info.sandboxMode:
                    info.statistics['pops'] += 1

                if new:
                    for e in new:
                        e.fireTicks -= 1

            else:
                self.fireTicks -= 1

        for projectile in gameInfo.projectiles:
            if abs(self.x - projectile.x) ** 2 + abs(self.y - projectile.y) ** 2 < (784 if self.isBoss else 289):
                if projectile.removeRegen:
                    self.regen = False

                if projectile.freezeDuration > 0:
                    gameInfo.projectiles.remove(projectile)
                    self.freezeTimer = max(self.freezeTimer, projectile.freezeDuration // (5 if self.isBoss else 1))
                else:
                    gameInfo.projectiles.remove(projectile)
                    if projectile.explosiveRadius > 0:
                        projectile.explode(self)
                        if self.tier in onlyExplosiveTiers:
                            color = enemyColors[str(self.tier)]
                            toDamage = [self]

                            for n in range(projectile.impactDamage):
                                newToDamage = []

                                for e in toDamage:
                                    if projectile.removeRegen:
                                        e.regen = False

                                    newToDamage += e.kill(coinMultiplier=projectile.coinMultiplier, bossDamage=projectile.bossDamage, overrideRuneColor=color)

                                    projectile.parent.hits += 1
                                    if not info.sandboxMode:
                                        info.statistics['pops'] += 1

                                toDamage = newToDamage

                                if not toDamage:
                                    break

                    if self.tier not in onlyExplosiveTiers:
                        color = enemyColors[str(self.tier)]
                        toDamage = [self]

                        for n in range(projectile.impactDamage):
                            newToDamage = []

                            for e in toDamage:
                                newToDamage += e.kill(coinMultiplier=projectile.coinMultiplier, bossDamage=projectile.bossDamage, overrideRuneColor=color)

                                projectile.parent.hits += 1
                                if not info.sandboxMode:
                                    info.statistics['pops'] += 1

                            if not toDamage:
                                break

        if not(self.tier in onlyExplosiveTiers or self.tier in resistant):
            for projectile in gameInfo.piercingProjectiles:
                if abs(self.x - projectile.x) ** 2 + abs(self.y - projectile.y) ** 2 < (900 if self.isBoss else 289):
                    if (self not in projectile.ignore) and (canSeeCamo(projectile.parent) or not self.camo):
                        color = enemyColors[str(self.tier)]
                        damage = 1
                        if type(projectile.parent) is Bowler:
                            if projectile.parent.upgrades[0] == 2:
                                damage = round(2 * projectile.damageMultiplier)
                            elif projectile.parent.upgrades[0] == 3:
                                damage = round(2 * (projectile.movement / 50 + 1) * projectile.damageMultiplier)

                        toDamage = [self]

                        for n in range(damage):
                            newToDamage = []

                            for e in toDamage:
                                newToDamage += e.kill(coinMultiplier=projectile.coinMultiplier, overrideRuneColor=color)

                            projectile.parent.hits += 1
                            if not info.sandboxMode:
                                info.statistics['pops'] += 1

                            toDamage = newToDamage
                            if not toDamage:
                                break

                        for e in toDamage:
                            projectile.ignore.append(e)

                        if projectile.pierce <= 1:
                            try:
                                gameInfo.piercingProjectiles.remove(projectile)
                            except ValueError:
                                pass

                        else:
                            projectile.pierce -= 1

    def draw(self, *, sx: int = 0, sy: int = 0):
        if self.isBoss:
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

            pygame.draw.rect(screen, (128, 128, 128), (self.x - 50 + sx, self.y - 25 + sy, 100, 5))
            pygame.draw.rect(screen, color, (self.x - 50 + sx, self.y - 25 + sy, round(self.HP / self.MaxHP * 100), 5))
            pygame.draw.rect(screen, (0, 0, 0), (self.x - 50 + sx, self.y - 25 + sy, 100, 5), 1)
            centredPrint(font, f'{math.ceil(self.HP / self.MaxHP * 100)}%', (self.x + sx, self.y - 35 + sy))

        if skinsEquipped[0] is not None:
            if ('Enemy', str(self.tier)) in skinsEquipped[0].skins.keys():
                centredBlit(skinsEquipped[0].skins[('Enemy', str(self.tier))][self.direction], (self.x + sx, self.y + sy))
                return

        pygame.draw.circle(screen, enemyColors[str(self.tier)], (self.x + sx, self.y + sy), 20 if self.isBoss else 12)

        if not self.isBoss:
            propertiesID = 0
            if self.camo:
                propertiesID += 1
            if self.regen:
                propertiesID += 2
            if self.fortified:
                propertiesID += 4

            color = {
                '0': None,
                '1': (0, 0, 0),
                '2': (255, 105, 180),
                '3': (187, 11, 255),
                '4': (152, 118, 84),
                '5': (165, 42, 42),
                '7': (200, 200, 0)
            }[str(propertiesID)]

            if color is not None:
                pygame.draw.circle(screen, color, (self.x + sx, self.y + sy), 12, 2)

    def kill(self, *, spawnNew: bool = True, coinMultiplier: int = 1, ignoreBoss: bool = False, burn: bool = False, bossDamage: int = 1, overrideRuneColor: Tuple[int] = None, ignoreRegularEnemyHealth: bool = False, reduceFireTicks: bool = False, ceramDamage: int = 1) -> list:
        if reduceFireTicks:
            self.fireTicks -= 1

        if self.isBoss:
            if ignoreBoss:
                try:
                    gameInfo.enemies.remove(self)
                except ValueError:
                    pass
                return

            else:
                self.HP -= 10 if burn else bossDamage
                if self.HP <= 0:
                    self.kill(spawnNew=spawnNew, coinMultiplier=coinMultiplier, ignoreBoss=True)

                    try:
                        self.fireIgnitedBy.hits += 1
                        if not info.sandboxMode:
                            info.statistics['pops'] += 1
                    except AttributeError:
                        pass

                    RuneEffects.createEffects(self, color=overrideRuneColor)
                    if not info.sandboxMode:
                        info.statistics['bossesKilled'] += 1

                else:
                    return [self]

        else:
            if not ignoreRegularEnemyHealth:
                if not str(self.tier) == '8':
                    if self.HP > 1:
                        self.HP -= 1
                        return [self]
                else:
                    if self.HP > ceramDamage:
                        self.HP -= ceramDamage
                        return [self]

            try:
                gameInfo.enemies.remove(self)
            except ValueError:
                pass

            if str(self.tier) == '0':
                RuneEffects.createEffects(self, color=overrideRuneColor)
                gameInfo.coins += coinMultiplier * 0.25

        if spawnNew:
            propertiesID = 0
            if self.camo:
                propertiesID += 1
            if self.regen:
                propertiesID += 2
            if self.fortified:
                propertiesID += 4

            newSpawn = enemiesSpawnNew[f'{propertiesID}{self.tier}']

            if self.tier in bossCoins.keys():
                if self.fortified:
                    gameInfo.coins += bossCoins[self.tier] * max(1, coinMultiplier / 4) * 2.5
                else:
                    gameInfo.coins += bossCoins[self.tier] * max(1, coinMultiplier / 4)

            if newSpawn is not None:
                spawned = []
                for n in range(len(newSpawn) // 2):
                    newSpawnType = newSpawn[2 * n]
                    newSpawnTier = newSpawn[2 * n + 1]

                    new = Enemy(str(newSpawnTier), self.lineIndex, self.maxRegenTier, mapPath=self.mapPath, spawn=[self.x, self.y], camo=newSpawnType in ['1', '3', '5', '7'], regen=newSpawnType in ['2', '3', '6', '7'], fortified=newSpawnType in ['4', '5', '6', '7'])
                    new.fireTicks = self.fireTicks
                    new.fireIgnitedBy = self.fireIgnitedBy
                    new.totalMovement = self.totalMovement
                    new.regenTimer = self.regenTimer
                    new.move(n)

                    spawned.append(new)

                return spawned

        return []

    def updateRegen(self):
        if not self.regen:
            return

        if self.regenTimer >= regenUpdateTimer:
            oldTier = self.tier

            if self.isBoss:
                self.HP = min(self.MaxHP, self.HP + 50)
            elif self.tier in regenPath:
                try:
                    self.tier = regenPath[regenPath.index(self.tier) + 1]
                except IndexError:
                    pass

            if strengthPath.index(self.maxRegenTier) < strengthPath.index(self.tier):
                self.tier = oldTier

            self.regenTimer = 0

        else:
            self.regenTimer += 1

# Functions
def reset() -> None:
    try:
        open(os.path.join(curr_path, os.pardir, 'save.txt'), 'r')

    except FileNotFoundError:
        print('tower-defense.core: No save file detected')

    else:
        try:
            open(os.path.join(curr_path, os.pardir, 'game.txt'), 'r')

        except FileNotFoundError:
            pass

    finally:
        with open(os.path.join(curr_path, os.pardir, 'save.txt'), 'w') as saveFile:
            saveFile.write('')

        with open(os.path.join(curr_path, os.pardir, 'game.txt'), 'w') as gameFile:
            gameFile.write('')

        print('tower-defense.core: Save file cleared!')


def fileSelection(path: str) -> str:
    textfiles = glob.glob(os.path.join(path, '*.txt'))
    subdirectories = glob.glob(os.path.join(path, '*', ''))
    displayedFiles = textfiles + subdirectories

    scroll = 0
    while True:
        screen.fill((200, 200, 200))

        mx, my = pygame.mouse.get_pos()
        maxScroll = max(30 * len(displayedFiles) - 490, 0)

        if len(displayedFiles) == 0:
            centredPrint(font, 'No suitable files detected!', (500, 260))
        else:
            n = 0
            for pathToFile in displayedFiles:
                pygame.draw.rect(screen, (100, 100, 100), (25, 60 + 30 * n - scroll, 950, 25))
                if 25 <= mx <= 975 and 60 + 30 * n - scroll <= my <= 85 + 30 * n - scroll and 60 <= my <= 550:
                    pygame.draw.rect(screen, (128, 128, 128), (25, 60 + 30 * n - scroll, 950, 25), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (25, 60 + 30 * n - scroll, 950, 25), 3)

                if len(pathToFile) > 85:
                    pathToFileText = '...' + pathToFile[-82:]
                else:
                    pathToFileText = pathToFile
                leftAlignPrint(font, pathToFileText, (30, 72 + 30 * n - scroll))

                if pathToFile in textfiles:
                    size = os.path.getsize(pathToFile)
                    byteUnits = ['B', 'KB', 'MB', 'GB', 'TB']

                    m = 0
                    while True:
                        size = size / 1000
                        if size < 1:
                            size = size * 1000
                            break

                        if m == len(byteUnits):
                            m -= 1
                            size = size * 1000
                            break

                        m += 1

                    rightAlignPrint(font, f'{round(size, 1)} {byteUnits[m]}', (970, 72 + 30 * n - scroll))

                n += 1

        pygame.draw.rect(screen, (200, 200, 200), (0, 0, 1000, 60))
        centredPrint(mediumFont, 'File Selection', (500, 30))

        pygame.draw.rect(screen, (200, 200, 200), (0, 550, 1000, 50))

        pygame.draw.rect(screen, (255, 0, 0), (30, 560, 100, 30))
        centredPrint(font, 'Cancel', (80, 575))
        if 30 <= mx <= 130 and 560 <= my <= 590:
            pygame.draw.rect(screen, (128, 128, 128), (30, 560, 100, 30), 5)
        else:
            pygame.draw.rect(screen, (0, 0, 0), (30, 560, 100, 30), 3)

        pygame.draw.rect(screen, (100, 100, 100), (150, 560, 200, 30))
        centredPrint(font, 'Parent Folder', (250, 575))
        if 150 <= mx <= 350 and 560 <= my <= 590:
            pygame.draw.rect(screen, (128, 128, 128), (150, 560, 200, 30), 5)
        else:
            pygame.draw.rect(screen, (0, 0, 0), (150, 560, 200, 30), 3)

        if len(path) > 60:
            pathText = '...' + path[-57:]
        else:
            pathText = path
        rightAlignPrint(tinyFont, pathText, (1000, 590))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save()
                quit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if 30 <= mx <= 130 and 560 <= my <= 590:
                        return ''

                    if 150 <= mx <= 350 and 560 <= my <= 590:
                        oldpath = path
                        path = os.path.dirname(path)

                        if oldpath == os.path.join(path, ''):
                            path = os.path.dirname(path)

                        scroll = 0
                        textfiles = glob.glob(os.path.join(path, '*.txt'))
                        subdirectories = glob.glob(os.path.join(path, '*', ''))
                        displayedFiles = textfiles + subdirectories

                    n = 0
                    for pathToFile in displayedFiles:
                        if 25 <= mx <= 975 and 60 + 30 * n - scroll <= my <= 85 + 30 * n - scroll and 60 <= my <= 550:
                            if pathToFile in subdirectories:
                                scroll = 0
                                path = pathToFile

                                textfiles = glob.glob(os.path.join(path, '*.txt'))
                                subdirectories = glob.glob(os.path.join(path, '*', ''))
                                displayedFiles = textfiles + subdirectories

                            if pathToFile in textfiles:
                                return pathToFile

                        n += 1

                if event.button == 4:
                    scroll = max(0, scroll - 5)

                if event.button == 5:
                    scroll = min(maxScroll, scroll + 5)

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]:
            scroll = max(0, scroll - 3)
        if pressed[pygame.K_DOWN]:
            scroll = min(maxScroll, scroll - 3)

        clock.tick(MaxFPS)
        pygame.display.update()


def getSellPrice(tower: Towers, *, pricePercent: SupportsFloat = 80) -> float:
    price = tower.price

    if type(tower) is not Elemental:
        for n in range(3):
            for m in range(tower.upgrades[n]):
                price += tower.upgradePrices[n][m]

        if tower.upgrades[3]:
            price += tower.upgradePrices[3]

    return price * pricePercent / 100


def centredBlit(image: pygame.Surface, pos: Tuple[int]) -> None:
    screen.blit(image, image.get_rect(center=pos))


def income() -> float:
    total = 0.01
    for tower in gameInfo.towers:
        if type(tower) is BananaFarm:
            total += [0.002, 0.01, 0.02, 0.05][tower.upgrades[1]]

    return total


def getCoinMultiplier(Tower: Towers) -> int:
    bananaFarms = [tower for tower in gameInfo.towers if type(tower) is BananaFarm]
    maxCoinMult = 1
    for bananaFarm in bananaFarms:
        if abs(Tower.x - bananaFarm.x) ** 2 + abs(Tower.y - bananaFarm.y) ** 2 < bananaFarm.range ** 2:
            maxCoinMult = max(maxCoinMult, [1, 1.25, 1.5, 2][bananaFarm.upgrades[2]])

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

    if type(Tower) is Sniper and Tower.upgrades[2] >= 1:
        return True

    if type(Tower) is Elemental:
        return True

    camoTowers = [tower for tower in gameInfo.towers if (type(tower) is Village or type(tower) is Elemental) and tower.upgrades[0] >= 1]
    for tower in camoTowers:
        if abs(Tower.x - tower.x) ** 2 + abs(Tower.y - tower.y) ** 2 < tower.range ** 2:
            return True
    return False


def canRemoveRegen(Tower: Towers) -> bool:
    if type(Tower) is Village and Tower.upgrades[1] == 3:
        return True

    regenDetectVillages = [tower for tower in gameInfo.towers if type(tower) is Village and tower.upgrades[1] == 3]
    for tower in regenDetectVillages:
        if abs(Tower.x - tower.x) ** 2 + abs(Tower.y - tower.y) ** 2 < tower.range ** 2:
            return True
    return False


def getTarget(tower: Towers, *, targeting: str = FIRST, ignore: [Enemy] = None, overrideRange: int = None, ignoreBosses: bool = False) -> Enemy:
    if ignore is None:
        ignore = []

    if overrideRange is None:
        rangeRadius = tower.range
    else:
        rangeRadius = overrideRange

    target = None

    if targeting == STRONG:
        maxStrength = None

        for enemy in gameInfo.enemies:
            if not (0 <= enemy.x <= 800 and 0 <= enemy.y <= 450) and overrideRange is None:
                continue

            if enemy in ignore:
                continue

            if ignoreBosses and enemy.isBoss:
                continue

            strength = strengthPath.index(str(enemy.tier))
            if abs(enemy.x - tower.x) ** 2 + abs(enemy.y - tower.y) ** 2 <= rangeRadius ** 2:
                if (enemy.camo and canSeeCamo(tower)) or (not enemy.camo):
                    try:
                        if strength > maxStrength:
                            maxStrength = strength
                            target = enemy

                    except TypeError:
                        maxStrength = strength
                        target = enemy

    if targeting == CLOSE:
        minDistance = None

        for enemy in gameInfo.enemies:
            if not (0 <= enemy.x <= 800 and 0 <= enemy.y <= 450) and overrideRange is None:
                continue

            if enemy in ignore:
                continue

            if ignoreBosses and enemy.isBoss:
                continue

            pythagoreanDistance = abs(enemy.x - tower.x) ** 2 + abs(enemy.y - tower.y) ** 2
            if pythagoreanDistance <= rangeRadius ** 2:
                if (enemy.camo and canSeeCamo(tower)) or (not enemy.camo):
                    try:
                        if pythagoreanDistance < minDistance:
                            minDistance = pythagoreanDistance
                            target = enemy

                    except TypeError:
                        minDistance = pythagoreanDistance
                        target = enemy

    if targeting == LAST:
        minDistance = None

        for enemy in gameInfo.enemies:
            if not (0 <= enemy.x <= 800 and 0 <= enemy.y <= 450) and overrideRange is None:
                continue

            if enemy in ignore:
                continue

            if ignoreBosses and enemy.isBoss:
                continue

            if abs(enemy.x - tower.x) ** 2 + abs(enemy.y - tower.y) ** 2 <= rangeRadius ** 2:
                if (enemy.camo and canSeeCamo(tower)) or (not enemy.camo):
                    try:
                        if enemy.totalMovement / enemy.totalPathLength < minDistance:
                            minDistance = enemy.totalMovement / enemy.totalPathLength
                            target = enemy

                    except TypeError:
                        minDistance = enemy.totalMovement / enemy.totalPathLength
                        target = enemy

    if targeting == FIRST:
        maxDistance = None

        for enemy in gameInfo.enemies:
            if not (0 <= enemy.x <= 800 and 0 <= enemy.y <= 450) and overrideRange is None:
                continue

            if enemy in ignore:
                continue

            if ignoreBosses and enemy.isBoss:
                continue

            if abs(enemy.x - tower.x) ** 2 + abs(enemy.y - tower.y) ** 2 <= rangeRadius ** 2:
                if (enemy.camo and canSeeCamo(tower)) or (not enemy.camo):
                    try:
                        if enemy.totalMovement / enemy.totalPathLength > maxDistance:
                            maxDistance = enemy.totalMovement / enemy.totalPathLength
                            target = enemy

                    except TypeError:
                        maxDistance = enemy.totalMovement / enemy.totalPathLength
                        target = enemy

    return target


def getRune(name: str) -> Rune:
    for rune in Runes:
        if rune.name == name:
            return rune


def getNotObtainedRune(ignore: List[str] = None) -> dict:
    if ignore is None:
        ignore = ['null']
    else:
        ignore.append('null')

    notObtainedRunes = []
    for rune in Runes:
        if rune.name not in info.runes and rune.name not in ignore:
            notObtainedRunes.append(rune.name)
    shopOfferedRune = random.choice(notObtainedRunes)

    return {'count': 1, 'item': shopOfferedRune, 'price': getRune(shopOfferedRune).shopPrice, 'bought': False, 'type': 'rune'}


def getRandomPowerUp() -> dict:
    powerUpPrices = {
        'lightning': 25,
        'spikes': 12,
        'antiCamo': 12,
        'heal': 15,
        'freeze': 10,
        'reload': 16
    }

    powerUp = random.choice([p for p in powerUpPrices.keys()])

    return {'item': powerUp, 'price': powerUpPrices[powerUp]}


def refreshShop() -> None:
    global info

    if not info.shopData:
        info.shopData = [None, None, None, None, None, None]

    k = 1
    notUnlockedSkin = getNotUnlockedSkin(info)
    if notUnlockedSkin is None:
        if len(info.runes) + 1 < len(Runes):
            info.shopData[0] = getNotObtainedRune()
            if len(info.runes) + 2 < len(Runes):
                info.shopData[1] = getNotObtainedRune([info.shopData[0]['item']])
            else:
                powerUp = getRandomPowerUp()
                info.shopData[1] = {'count': 5 * k, 'item': powerUp['item'], 'price': powerUp['price'] * 5 * k, 'bought': False, 'type': 'powerUp'}
                k += 1

        else:
            for n in range(2):
                powerUp = getRandomPowerUp()
                info.shopData[n] = {'count': 5 * k, 'item': powerUp['item'], 'price': powerUp['price'] * 5 * k, 'bought': False, 'type': 'powerUp'}
                k += 1

    else:
        info.shopData[0] = {'count': 1, 'item': notUnlockedSkin.name, 'price': notUnlockedSkin.price, 'bought': False, 'type': 'skin'}
        if len(info.runes) + 1 < len(Runes):
            info.shopData[1] = getNotObtainedRune()
        else:
            powerUp = getRandomPowerUp()
            info.shopData[1] = {'count': 5 * k, 'item': powerUp['item'], 'price': powerUp['price'] * 5 * k, 'bought': False, 'type': 'powerUp'}
            k += 1

    for n in range(4):
        powerUp = getRandomPowerUp()
        info.shopData[2 + n] = {'count': 5 * k, 'item': powerUp['item'], 'price': powerUp['price'] * 5 * k, 'bought': False, 'type': 'powerUp'}
        k += 1


def draw() -> None:
    if gameInfo.Map is None:
        return

    mx, my = pygame.mouse.get_pos()

    screen.fill(gameInfo.Map.backgroundColor)
    for i in range(len(gameInfo.Map.path)):
        for j in range(len(gameInfo.Map.path[i]) - 1):
            lineWidth = 14 if gameInfo.Map.path[i][j][0] != gameInfo.Map.path[i][j + 1][0] and gameInfo.Map.path[i][j][1] != gameInfo.Map.path[i][j + 1][1] else 10
            pygame.draw.line(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][j], gameInfo.Map.path[i][j + 1], lineWidth)
            pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][j + 1], lineWidth // 2)
        pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][0], 10)
        pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][-1], 10)

    RuneEffects.draw(screen)
    PowerUps.draw(screen)

    if gameInfo.selected is not None:
        if gameInfo.selected.range in possibleRanges:
            modified = rangeImages[possibleRanges.index(gameInfo.selected.range)]
        else:
            original = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'range.png')), (gameInfo.selected.range * 2, gameInfo.selected.range * 2))
            modified = original.copy()
            modified.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)

        if type(gameInfo.selected) in [Village, BananaFarm]:
            for tower in gameInfo.towers:
                if abs(tower.x - gameInfo.selected.x) ** 2 + abs(tower.y - gameInfo.selected.y) ** 2 < gameInfo.selected.range ** 2:
                    pygame.draw.circle(screen, gameInfo.selected.color, (tower.x, tower.y), 17, 5)

        screen.blit(modified, (gameInfo.selected.x - gameInfo.selected.range, gameInfo.selected.y - gameInfo.selected.range))

    if gameInfo.placing != '':
        centredPrint(font, f'Click anywhere on the map to place the {gameInfo.placing.capitalize()}!', (400, 400))
        centredPrint(font, f'Press [ESC] to cancel!', (400, 425))

        if 0 <= mx <= 800 and 0 <= my <= 450:
            if gameInfo.placing == 'spikes':
                screen.blit(powerUps['spikes'][0], (mx - 25, my - 25))

            else:
                classObj = None
                for tower in Towers.__subclasses__():
                    if tower.name == gameInfo.placing:
                        classObj = tower

                if gameInfo.placing in ['Village', 'Banana Farm']:
                    for tower in gameInfo.towers:
                        if abs(tower.x - mx) ** 2 + abs(tower.y - my) ** 2 < classObj.range ** 2:
                            pygame.draw.circle(screen, classObj.color, (tower.x, tower.y), 17, 5)

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

    for tower in gameInfo.towers:
        tower.draw()

    for enemy in gameInfo.enemies:
        enemy.draw()

    for projectile in gameInfo.projectiles:
        projectile.draw()

    for projectile in gameInfo.piercingProjectiles:
        projectile.draw()

    pygame.draw.rect(screen, (221, 221, 221), (800, 0, 200, 450))

    n = 0
    for towerType in Towers.__subclasses__():
        if towerType is Elemental:
            continue

        if gameInfo.wave >= towerType.req or info.sandboxMode:
            leftAlignPrint(font, f'{towerType.name} (${towerType.price})', (810, 20 + 80 * n + gameInfo.shopScroll))

            pygame.draw.rect(screen, (187, 187, 187), (945, 30 + 80 * n + gameInfo.shopScroll, 42, 42))
            if towerImages[towerType.name] is not None:
                try:
                    screen.blit(towerImages[towerType.name], (951, 36 + 80 * n + gameInfo.shopScroll))
                except TypeError:
                    screen.blit(towerImages[towerType.name][0], (951, 36 + 80 * n + gameInfo.shopScroll))
            else:
                pygame.draw.circle(screen, towerType.color, (966, 51 + 80 * n + gameInfo.shopScroll), 15)

            pygame.draw.line(screen, (0, 0, 0), (800, 80 * n + gameInfo.shopScroll), (1000, 80 * n + gameInfo.shopScroll), 3)
            pygame.draw.line(screen, (0, 0, 0), (800, 80 + 80 * n + gameInfo.shopScroll), (1000, 80 + 80 * n + gameInfo.shopScroll), 3)

            if gameInfo.coins >= towerType.price:
                color = (200, 200, 200)
            else:
                color = (255, 100, 100)
            pygame.draw.rect(screen, color, (810, 40 + 80 * n + gameInfo.shopScroll, 100, 30))

            centredPrint(font, 'Buy New', (860, 55 + 80 * n + gameInfo.shopScroll))
            if 810 <= mx <= 910 and 40 + 80 * n + gameInfo.shopScroll <= my <= 70 + 80 * n + gameInfo.shopScroll:
                pygame.draw.rect(screen, (128, 128, 128), (810, 40 + 80 * n + gameInfo.shopScroll, 100, 30), 5)
            else:
                pygame.draw.rect(screen, (0, 0, 0), (810, 40 + 80 * n + gameInfo.shopScroll, 100, 30), 3)

        n += 1

    pygame.draw.rect(screen, (170, 170, 170), (0, 450, 1000, 150))

    fps = clock.get_fps()
    if fps < 1:
        try:
            leftAlignPrint(font, f'SPF: {round(1 / fps, 1)}', (10, 525))
        except ZeroDivisionError:
            pass
    else:
        leftAlignPrint(font, f'FPS: {round(fps, 1)}', (10, 525))

    if info.sandboxMode:
        txt = INFINITYSTR
    else:
        txt = str(gameInfo.HP)

    leftAlignPrint(font, txt, (10, 500))
    screen.blit(healthImage if gameInfo.HP <= 250 else goldenHealthImage, (font.size(txt)[0] + 17, 493))

    if info.sandboxMode:
        leftAlignPrint(font, f'Coins: {INFINITYSTR}', (10, 550))
    else:
        try:
            leftAlignPrint(font, f'Coins: {math.floor(gameInfo.coins)}', (10, 550))
        except OverflowError:
            info.sandboxMode = True

    leftAlignPrint(font, f'Wave {max(gameInfo.wave, 1)} of {len(waves)}', (10, 575))

    pygame.draw.rect(screen, (200, 200, 200), (810, 460, 50, 50))
    centredBlit(powerUps['spikes'][0], (835, 485))
    if 810 <= mx <= 860 and 460 <= my <= 510:
        pygame.draw.rect(screen, (128, 128, 128), (810, 460, 50, 50), 5)
    else:
        pygame.draw.rect(screen, (0, 0, 0), (810, 460, 50, 50), 3)
    centredPrint(tinyFont, str(info.powerUps['spikes']), (835, 518))

    pygame.draw.rect(screen, (200, 200, 200), (875, 460, 50, 50))
    centredBlit(powerUps['lightning'][0], (900, 485))
    if 875 <= mx <= 925 and 460 <= my <= 510:
        pygame.draw.rect(screen, (128, 128, 128), (875, 460, 50, 50), 5)
    else:
        pygame.draw.rect(screen, (0, 0, 0), (875, 460, 50, 50), 3)
    centredPrint(tinyFont, str(info.powerUps['lightning']), (900, 518))

    pygame.draw.rect(screen, (200, 200, 200), (940, 460, 50, 50))
    centredBlit(powerUps['antiCamo'][0], (965, 485))
    if 940 <= mx <= 990 and 440 <= my <= 510:
        pygame.draw.rect(screen, (128, 128, 128), (940, 460, 50, 50), 5)
    else:
        pygame.draw.rect(screen, (0, 0, 0), (940, 460, 50, 50), 3)
    centredPrint(tinyFont, str(info.powerUps['antiCamo']), (965, 518))

    pygame.draw.rect(screen, (200, 200, 200), (810, 530, 50, 50))
    centredBlit(powerUps['heal'][0], (835, 555))
    if 810 <= mx <= 860 and 530 <= my <= 580:
        pygame.draw.rect(screen, (128, 128, 128), (810, 530, 50, 50), 5)
    else:
        pygame.draw.rect(screen, (0, 0, 0), (810, 530, 50, 50), 3)
    centredPrint(tinyFont, str(info.powerUps['heal']), (835, 588))

    pygame.draw.rect(screen, (200, 200, 200), (875, 530, 50, 50))
    centredBlit(powerUps['freeze'][0], (900, 555))
    if 875 <= mx <= 925 and 530 <= my <= 580:
        pygame.draw.rect(screen, (128, 128, 128), (875, 530, 50, 50), 5)
    else:
        pygame.draw.rect(screen, (0, 0, 0), (875, 530, 50, 50), 3)
    centredPrint(tinyFont, str(info.powerUps['freeze']), (900, 588))

    pygame.draw.rect(screen, (200, 200, 200), (940, 530, 50, 50))
    centredBlit(powerUps['reload'][0], (965, 555))
    if 940 <= mx <= 990 and 530 <= my <= 580:
        pygame.draw.rect(screen, (128, 128, 128), (940, 530, 50, 50), 5)
    else:
        pygame.draw.rect(screen, (0, 0, 0), (940, 530, 50, 50), 3)
    centredPrint(tinyFont, str(info.powerUps['reload']), (965, 588))

    pygame.draw.rect(screen, (255, 0, 0), (0, 450, 20, 20))
    pygame.draw.line(screen, (0, 0, 0), (3, 453), (17, 467), 2)
    pygame.draw.line(screen, (0, 0, 0), (3, 467), (17, 453), 2)
    if mx <= 20 and 450 <= my <= 470:
        pygame.draw.rect(screen, (128, 128, 128), (0, 450, 20, 20), 3)
    else:
        pygame.draw.rect(screen, (0, 0, 0), (0, 450, 20, 20), 3)

    if issubclass(type(gameInfo.selected), Towers):
        if type(gameInfo.selected) is not Elemental:
            leftAlignPrint(font, 'Upgrades:', (200, 497))
        leftAlignPrint(font, f'Pops: {gameInfo.selected.hits}', (200, 470))

        if gameInfo.selected.upgrades[0] == gameInfo.selected.upgrades[1] == gameInfo.selected.upgrades[2] == 3 or type(gameInfo.selected) is Elemental:
            if gameInfo.selected.upgrades[3] or type(gameInfo.selected) is Elemental:
                if 295 <= mx <= 595 and 485 <= my <= 575:
                    pygame.draw.rect(screen, (255, 255, 225), (295, 485, 300, 90))
                else:
                    pygame.draw.rect(screen, (255, 255, 191), (295, 485, 300, 90))
                pygame.draw.rect(screen, (0, 0, 0), (295, 485, 300, 90), 3)

                leftAlignPrint(font, f'{gameInfo.selected.upgradeNames[3]}', (300, 500))
                if gameInfo.selected.abilityCooldown >= gameInfo.selected.totalAbilityCooldown:
                    centredPrint(font, 'Click to use!', (445, 530))
                else:
                    centredPrint(font, f'On cooldown for {math.ceil((gameInfo.selected.totalAbilityCooldown - gameInfo.selected.abilityCooldown) / 100)}s', (445, 530))
            else:
                if 295 <= mx <= 595 and 485 <= my <= 605:
                    if gameInfo.coins >= gameInfo.selected.upgradePrices[3]:
                        color = (200, 200, 200)
                    else:
                        color = (255, 180, 180)
                else:
                    if gameInfo.coins >= gameInfo.selected.upgradePrices[3]:
                        color = (100, 100, 100)
                    else:
                        color = (255, 100, 100)

                pygame.draw.rect(screen, color, (295, 485, 300, 90))
                pygame.draw.rect(screen, (0, 0, 0), (295, 485, 300, 90), 3)

                if type(gameInfo.selected) is Village:
                    price = 0
                    for tower in gameInfo.towers:
                        if tower == gameInfo.selected:
                            continue

                        if type(tower) is Elemental:
                            continue

                        if abs(tower.x - gameInfo.selected.x) ** 2 + abs(tower.y - gameInfo.selected.y) ** 2 <= gameInfo.selected.range ** 2:
                            price += getSellPrice(tower, pricePercent=100)

                    if price >= 10000:
                        leftAlignPrint(font, f'{gameInfo.selected.upgradeNames[3]} [${gameInfo.selected.upgradePrices[3]}]', (300, 500))
                    else:
                        centredPrint(font, 'The Elemental demands', (445, 515))
                        centredPrint(font, 'powerful sacrifices!', (445, 540))

                else:
                    leftAlignPrint(font, f'{gameInfo.selected.upgradeNames[3]} [${gameInfo.selected.upgradePrices[3]}]', (300, 500))

        else:
            for n in range(3):
                if gameInfo.selected.upgrades[n] == 3:
                    pygame.draw.rect(screen, (255, 255, 191), (295, 485 + 30 * n, 300, 30))
                    centredPrint(font, 'MAX', (445, 500 + 30 * n))
                else:
                    if 295 <= mx <= 595 and 485 + 30 * n < my <= 515 + 30 * n:
                        if gameInfo.selected.upgradePrices[n][gameInfo.selected.upgrades[n]] <= gameInfo.coins:
                            color = (200, 200, 200)
                        else:
                            color = (255, 180, 180)
                            pygame.draw.rect(screen, (200, 200, 200), (295, 485 + 30 * n, 300, 30))
                    else:
                        if gameInfo.selected.upgradePrices[n][gameInfo.selected.upgrades[n]] <= gameInfo.coins:
                            color = (100, 100, 100)
                        else:
                            color = (255, 100, 100)

                    pygame.draw.rect(screen, color, (295, 485 + 30 * n, 300, 30))
                    leftAlignPrint(font, f'{gameInfo.selected.upgradeNames[n][gameInfo.selected.upgrades[n]]} [${gameInfo.selected.upgradePrices[n][gameInfo.selected.upgrades[n]]}]', (300, 500 + n * 30), (32, 32, 32))

                pygame.draw.rect(screen, (0, 0, 0), (295, 485 + 30 * n, 300, 30), 3)

                for m in range(3):
                    if gameInfo.selected.upgrades[n] > m:
                        pygame.draw.circle(screen, (0, 255, 0), (560 + 12 * m, 497 + 30 * n), 5)
                    pygame.draw.circle(screen, (0, 0, 0), (560 + 12 * m, 497 + 30 * n), 5, 2)

        pygame.draw.rect(screen, (100, 100, 100), (620, 545, 150, 25))
        if 620 < mx < 820 and 545 < my < 570:
            pygame.draw.rect(screen, (128, 128, 128), (620, 545, 150, 25), 5)
        else:
            pygame.draw.rect(screen, (0, 0, 0), (620, 545, 150, 25), 3)
        centredPrint(font, f'Sell: ${round(getSellPrice(gameInfo.selected))}', (695, 557))

        if type(gameInfo.selected) not in [Bowler, InfernoTower]:
            pygame.draw.rect(screen, (100, 100, 100), (620, 515, 150, 25))
            if 620 < mx < 820 and 515 < my < 540:
                pygame.draw.rect(screen, (128, 128, 128), (620, 515, 150, 25), 5)
            else:
                pygame.draw.rect(screen, (0, 0, 0), (620, 515, 150, 25), 3)
            centredPrint(font, f'Target: {gameInfo.selected.targeting.capitalize()}', (695, 527))

        if type(gameInfo.selected) is IceTower:
            pygame.draw.rect(screen, (0, 255, 0) if gameInfo.selected.enabled else (255, 0, 0), (620, 485, 150, 25))
            if 620 <= mx <= 770 and 485 <= my <= 510:
                pygame.draw.rect(screen, (128, 128, 128), (620, 485, 150, 25), 5)
            else:
                pygame.draw.rect(screen, (0, 0, 0), (620, 485, 150, 25), 3)
            centredPrint(font, 'ENABLED' if gameInfo.selected.enabled else 'DISABLED', (695, 497))

    if mx <= 800 and my <= 450:
        pygame.display.update((0, 0, 800, 450))
    else:
        pygame.display.update()


def move() -> None:
    for enemy in gameInfo.enemies:
        enemy.move(speed[str(enemy.tier)])

    for tower in gameInfo.towers:
        tower.update()
        tower.attack()

    for projectile in gameInfo.projectiles:
        projectile.move()

    for projectile in gameInfo.piercingProjectiles:
        projectile.move()


def getClosestPoint(mx: int, my: int, *, sx: int = None, sy: int = None) -> Tuple[int, int]:
    if sx is None and sy is None:
        return [round((mx - 100) / 25) * 25 + 100, round((my - 125) / 25) * 25 + 125]

    closestDistance = 100000000
    closestTuple = (0, 0)

    for x in range(33):
        for y in range(19):
            tx = None
            ty = None

            if x * 25 + 100 == sx:
                tx = sx
                ty = y * 25 + 125

            if y * 25 + 125 == sy:
                tx = x * 25 + 100
                ty = sy

            if abs(x * 25 + 100 - sx) == abs(y * 25 + 125 - sy):
                tx = x * 25 + 100
                ty = y * 25 + 125

            if tx is not None and ty is not None:
                distance = abs(tx - mx) ** 2 + abs(ty - my) ** 2

                if distance < closestDistance:
                    closestDistance = distance
                    closestTuple = [tx, ty]

    return closestTuple


def getActualCooldown(x: int, y: int, originalCooldown: int) -> int:
    cooldown = originalCooldown

    if gameInfo.doubleReloadTicks > 0:
        cooldown /= 2

    foundVillageWithAbility = False
    for tower in gameInfo.towers:
        if type(tower) is Village and abs(tower.x - x) ** 2 + abs(tower.y - y) ** 2 <= tower.range ** 2:
            if tower.abilityData['active']:
                foundVillageWithAbility = True

    if foundVillageWithAbility:
        cooldown /= 2

    return math.floor(cooldown)


def save() -> None:
    info.powerUpData = PowerUps
    pickle.dump(info, open(os.path.join(curr_path, os.pardir, 'save.txt'), 'wb'))
    pickle.dump(gameInfo, open(os.path.join(curr_path, os.pardir, 'game.txt'), 'wb'))


def load() -> None:
    global info, gameInfo, PowerUps, towerImages

    if os.path.exists(os.path.join(curr_path, 'save.txt')):         # Update 3.7 (Relocate Data to Local Storage)
        print('Detected save.txt from version pre-3.7.2: Attempting to relocate save.txt...')

        open(os.path.join(curr_path, '..', 'save.txt'), 'w')

        saveFileData = pickle.load(open(os.path.join(curr_path, 'save.txt'), 'rb'))
        pickle.dump(saveFileData, open(os.path.join(curr_path, '..', 'save.txt'), 'wb'))

        os.remove(os.path.join(curr_path, 'save.txt'))

        print(f'Relocated save.txt to {os.path.join(os.path.dirname(curr_path), "save.txt")}\n')

        if os.path.exists(os.path.join(curr_path, 'game.txt')):
            print('Detected game.txt from version pre-3.7.2: Attempting to relocate game.txt...')

            open(os.path.join(curr_path, '..', 'game.txt'), 'w')

            gameFileData = pickle.load(open(os.path.join(curr_path, 'game.txt'), 'rb'))
            pickle.dump(gameFileData, open(os.path.join(curr_path, '..', 'game.txt'), 'wb'))

            os.remove(os.path.join(curr_path, 'game.txt'))

            print(f'Relocated game.txt to {os.path.join(os.path.dirname(curr_path), "game.txt")}\n')

            if os.path.exists(os.path.join(curr_path, 'replay-files')):
                print('Detected replay-files/ from version pre-3.7.2: Attempting to relocate replay-files/...')

                try:
                    os.mkdir(os.path.join(curr_path, '..', 'replay-files'))

                except FileExistsError:
                    print(f'Detected replay-files/ in {os.path.dirname(curr_path)}: Attempting to merge replay-files/...')

                    replayFiles = [p for p in os.listdir(os.path.join(curr_path, 'replay-files')) if p.endswith('.txt')]

                    for replayFile in replayFiles:
                        replayFileData = pickle.load(open(os.path.join(curr_path, 'replay-files', replayFile), 'rb'))

                        open(os.path.join(curr_path, '..', 'replay-files', replayFile), 'w')
                        pickle.dump(replayFileData, open(os.path.join(curr_path, '..', 'replay-files', replayFile), 'wb'))

                    print(f'Merged {os.path.join(os.path.dirname(curr_path), "replay-files")} with {os.path.join(curr_path, "replay-files")} successfully!\n')

                else:
                    replayFiles = [p for p in os.listdir(os.path.join(curr_path, 'replay-files')) if p.endswith('.txt')]

                    for replayFile in replayFiles:
                        replayFileData = pickle.load(open(os.path.join(curr_path, 'replay-files', replayFile), 'rb'))

                        open(os.path.join(curr_path, '..', 'replay-files', replayFile), 'w')
                        pickle.dump(replayFileData, open(os.path.join(curr_path, '..', 'replay-files', replayFile), 'wb'))

                        os.remove(os.path.join(curr_path, 'replay-files', replayFile))

                finally:
                    os.rmdir(os.path.join(curr_path, 'replay-files'))
                    print(f'Relocated your replay files to {os.path.join(os.path.dirname(curr_path), "replay-files", "")}\n')

        info = pickle.load(open(os.path.join(curr_path, os.pardir, 'save.txt'), 'rb'))
        gameInfo = pickle.load(open(os.path.join(curr_path, os.pardir, 'game.txt'), 'rb'))

        info, gameInfo, PowerUps = update(info, gameInfo, PowerUps)

        skinLoaded = loadSkin(info.skinsEquipped[1], Towers.__subclasses__())
        if skinLoaded is not None:
            towerImages = skinLoaded

        print(f'Loaded save.txt and game.txt from {os.path.join(os.path.dirname(curr_path), "")}')

    else:
        try:
            open(os.path.join(curr_path, os.pardir, 'save.txt'), 'r')
            info = pickle.load(open(os.path.join(curr_path, os.pardir, 'save.txt'), 'rb'))
            try:
                gameInfo = pickle.load(open(os.path.join(curr_path, os.pardir, 'game.txt'), 'rb'))

            except FileNotFoundError:   # Update pre-2.6 (Relocate gamefile)
                for attr in playerAttrs:
                    resetTo = getattr(info, attr)
                    if type(resetTo) in [dict, list]:
                        setattr(gameInfo, attr, resetTo.copy())
                    else:
                        setattr(gameInfo, attr, resetTo)

                pickle.dump(gameInfo, open(os.path.join(curr_path, os.pardir, 'game.txt'), 'wb'))
                print(f'Created file {os.path.join(curr_path, os.pardir, "game.txt")}')

            info.update()
            gameInfo.update()

            info, gameInfo, PowerUps = update(info, gameInfo, PowerUps)

            skinLoaded = loadSkin(info.skinsEquipped[1], Towers.__subclasses__())
            if skinLoaded is not None:
                towerImages = skinLoaded

        except FileNotFoundError as e:
            open(os.path.join(curr_path, os.pardir, 'save.txt'), 'w')
            print(f'Created file {os.path.join(curr_path, os.pardir, "save.txt")}')

        except AttributeError as e:
            print(f'tower-defense.core: Fatal - There seems to be something wrong with your save-file.\n\nSee details: {e}')

        except UnpicklingError as e:
            print(f'tower-defense.core: Fatal - Your save-file seems to be corrupt and it has been reset!\n\nSee details: {e}')

        except (EOFError, ValueError):
            pass

        else:
            print(f'Loaded save.txt and game.txt from {os.path.join(os.path.dirname(curr_path), "")}')

        finally:
            try:
                os.mkdir(os.path.join(curr_path, os.pardir, 'replay-files'))
                print(f'Created folder {os.path.join(os.path.dirname(curr_path), "replay-files")}')

            except FileExistsError:
                pass

            except OSError as e:
                print(f'Something happened when trying to create replay-files/ folder. See details: {e}')


# Main
def app() -> None:
    global skinsEquipped

    load()

    if info.status == 'game':
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
                                gameInfo.reset()
                                info.status = 'mapSelect'
                                cont = True
                            elif 600 < mx < 775:
                                cont = True
                                skinsEquipped = [getSkin(s) for s in info.skinsEquipped]

            if cont:
                break

    while True:
        global mouseTrail, towerImages

        if info.status == 'tutorial':
            if info.tutorialPhase == 0:
                while True:
                    screen.fill((200, 200, 200))
                    centredPrint(mediumFont, f'Hi! Welcome to Tower Defense Version {__version__}!', (500, 150))

                    rightAlignPrint(tinyFont, 'Press [ESC] to skip tutorial!', (990, 20))
                    centredPrint(font, 'Press [SPACE] to continue!', (500, 400))

                    cont = True
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            save()
                            quit()

                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                info.status = 'mapSelect'
                                cont = False

                                gameInfo.reset()

                            elif event.key == pygame.K_SPACE:
                                info.tutorialPhase = 1
                                cont = False

                                gameInfo.reset()

                    if not cont:
                        break

                    pygame.display.update()

                    gameInfo.Map = Maps[5]

            elif info.tutorialPhase == 1:
                while True:
                    mx, my = pygame.mouse.get_pos()

                    if len(gameInfo.enemies) == 0:
                        Enemy('0', 0, '0')

                    screen.fill(gameInfo.Map.backgroundColor)
                    for i in range(len(gameInfo.Map.path)):
                        for j in range(len(gameInfo.Map.path[i]) - 1):
                            lineWidth = 14 if gameInfo.Map.path[i][j][0] != gameInfo.Map.path[i][j + 1][0] and gameInfo.Map.path[i][j][1] != gameInfo.Map.path[i][j + 1][1] else 10
                            pygame.draw.line(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][j], gameInfo.Map.path[i][j + 1], lineWidth)
                            pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][j + 1], lineWidth // 2)
                        pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][0], 10)
                        pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][-1], 10)

                    if gameInfo.enemies[0].totalMovement > 500:
                        centredPrint(font, 'Oh no! An enemy is approaching! You should place down a turret.', (500, 500))

                        pygame.draw.rect(screen, (221, 221, 221), (800, 0, 200, 80))
                        pygame.draw.rect(screen, (187, 187, 187), (945, 30, 42, 42))

                        leftAlignPrint(font, f'{Turret.name} (FREE)', (810, 20))

                        if towerImages[Turret.name] is not None:
                            try:
                                screen.blit(towerImages[Turret.name], (951, 36))
                            except TypeError:
                                screen.blit(towerImages[Turret.name][0], (951, 36))
                        else:
                            pygame.draw.circle(screen, Turret.color, (966, 51), 15)

                        pygame.draw.rect(screen, (200, 200, 200), (810, 40, 100, 30))

                        centredPrint(font, 'Buy New', (860, 55))
                        if 810 <= mx <= 910 and 40 <= my <= 70:
                            pygame.draw.rect(screen, (128, 128, 128), (810, 40, 100, 30), 5)
                        else:
                            pygame.draw.rect(screen, (0, 0, 0), (810, 40, 100, 30), 3)

                    else:
                        for enemy in gameInfo.enemies:
                            enemy.move(speed[enemy.tier])

                    for enemy in gameInfo.enemies:
                        enemy.draw()

                    cont = True
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            save()
                            quit()

                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                info.status = 'mapSelect'
                                cont = False

                                gameInfo.reset()

                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                if 810 <= mx <= 910 and 40 <= my <= 70:
                                    info.tutorialPhase = 2
                                    cont = False

                    if not cont:
                        break

                    pygame.display.update()
                    clock.tick(MaxFPS)

            elif info.tutorialPhase == 2:
                while True:
                    mx, my = pygame.mouse.get_pos()

                    if len(gameInfo.enemies) == 0:
                        Enemy('0', 0, '0')

                    gameInfo.Map = Maps[5]

                    screen.fill(gameInfo.Map.backgroundColor)
                    for i in range(len(gameInfo.Map.path)):
                        for j in range(len(gameInfo.Map.path[i]) - 1):
                            lineWidth = 14 if gameInfo.Map.path[i][j][0] != gameInfo.Map.path[i][j + 1][0] and gameInfo.Map.path[i][j][1] != gameInfo.Map.path[i][j + 1][1] else 10
                            pygame.draw.line(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][j], gameInfo.Map.path[i][j + 1], lineWidth)
                            pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][j + 1], lineWidth // 2)
                        pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][0], 10)
                        pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][-1], 10)

                    centredPrint(font, 'Place the Turret near the enemy!', (500, 400))

                    pygame.draw.rect(screen, (221, 221, 221), (800, 0, 200, 80))
                    pygame.draw.rect(screen, (187, 187, 187), (945, 30, 42, 42))

                    leftAlignPrint(font, f'{Turret.name} (FREE)', (810, 20))

                    if towerImages[Turret.name] is not None:
                        try:
                            screen.blit(towerImages[Turret.name], (951, 36))
                        except TypeError:
                            screen.blit(towerImages[Turret.name][0], (951, 36))
                    else:
                        pygame.draw.circle(screen, Turret.color, (966, 51), 15)

                    pygame.draw.rect(screen, (200, 200, 200), (810, 40, 100, 30))

                    centredPrint(font, 'Buy New', (860, 55))
                    pygame.draw.rect(screen, (0, 0, 0), (810, 40, 100, 30), 3)

                    for enemy in gameInfo.enemies:
                        enemy.draw()
                        centredBlit(rangeImages[possibleRanges.index(30)], (enemy.x, enemy.y))

                    cont = True
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            save()
                            quit()

                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                info.status = 'mapSelect'
                                cont = False

                                gameInfo.reset()

                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                print(abs(gameInfo.enemies[0].x - mx) ** 2 + abs(gameInfo.enemies[0].y - my) ** 2)
                                if abs(gameInfo.enemies[0].x - mx) ** 2 + abs(gameInfo.enemies[0].y - my) ** 2 <= 900:
                                    Turret(mx, my)
                                    info.tutorialPhase = 3
                                    cont = False

                    if not cont:
                        break

                    pygame.display.update()

            elif info.tutorialPhase == 3:
                while True:
                    gameInfo.Map = Maps[5]

                    screen.fill(gameInfo.Map.backgroundColor)
                    for i in range(len(gameInfo.Map.path)):
                        for j in range(len(gameInfo.Map.path[i]) - 1):
                            lineWidth = 14 if gameInfo.Map.path[i][j][0] != gameInfo.Map.path[i][j + 1][0] and gameInfo.Map.path[i][j][1] != gameInfo.Map.path[i][j + 1][1] else 10
                            pygame.draw.line(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][j], gameInfo.Map.path[i][j + 1], lineWidth)
                            pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][j + 1], lineWidth // 2)
                        pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][0], 10)
                        pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][-1], 10)

                    cont = True
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            save()
                            quit()

                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                info.status = 'mapSelect'
                                cont = False

                                gameInfo.reset()

                    if not cont:
                        break

                    if len(gameInfo.enemies) == 0:
                        info.tutorialPhase = 4
                        break

                    move()

                    for obj in gameInfo.projectiles + gameInfo.towers + gameInfo.enemies:
                        obj.draw()

                    pygame.display.update()
                    clock.tick(MaxFPS)

            elif info.tutorialPhase == 4:
                n = 0
                while True:
                    mx, my = pygame.mouse.get_pos()

                    if len(gameInfo.enemies) == 0:
                        Enemy('0', 0, '0', regen=True)

                    gameInfo.Map = Maps[5]

                    screen.fill(gameInfo.Map.backgroundColor)
                    for i in range(len(gameInfo.Map.path)):
                        for j in range(len(gameInfo.Map.path[i]) - 1):
                            lineWidth = 14 if gameInfo.Map.path[i][j][0] != gameInfo.Map.path[i][j + 1][0] and gameInfo.Map.path[i][j][1] != gameInfo.Map.path[i][j + 1][1] else 10
                            pygame.draw.line(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][j], gameInfo.Map.path[i][j + 1], lineWidth)
                            pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][j + 1], lineWidth // 2)
                        pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][0], 10)
                        pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][-1], 10)

                    cont = True
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            save()
                            quit()

                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                info.status = 'mapSelect'
                                cont = False

                                gameInfo.reset()

                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                if 295 <= mx <= 595 and 515 < my <= 545:
                                    gameInfo.towers[0].upgrades[1] = min(gameInfo.towers[0].upgrades[1] + 1, 3)

                    if not cont:
                        break

                    if gameInfo.enemies[0].totalMovement > 250 and gameInfo.towers[0].upgrades[1] < 3:
                        centredPrint(font, 'Is that a regen balloon? Look, it\'s regenerating its layers!', (500, 375))
                        centredPrint(font, 'Quick, upgrade your turret!', (500, 400))

                        for n in range(3):
                            if gameInfo.towers[0].upgrades[n] == 3:
                                pygame.draw.rect(screen, (255, 255, 191), (295, 485 + 30 * n, 300, 30))
                                centredPrint(font, 'MAX', (445, 500 + 30 * n))
                            else:
                                if 295 <= mx <= 595 and 485 + 30 * n < my <= 515 + 30 * n:
                                    if n == 1:
                                        color = (200, 200, 200)
                                    else:
                                        color = (255, 180, 180)

                                else:
                                    if n == 1:
                                        color = (100, 100, 100)
                                    else:
                                        color = (255, 100, 100)

                                pygame.draw.rect(screen, color, (295, 485 + 30 * n, 300, 30))
                                if n == 1:
                                    leftAlignPrint(font, f'{gameInfo.towers[0].upgradeNames[1][gameInfo.towers[0].upgrades[1]]} [FREE]', (300, 500 + n * 30), (32, 32, 32))
                                else:
                                    leftAlignPrint(font, f'{gameInfo.towers[0].upgradeNames[n][gameInfo.towers[0].upgrades[n]]} [${gameInfo.towers[0].upgradePrices[n][gameInfo.towers[0].upgrades[n]]}]', (300, 500 + n * 30), (32, 32, 32))

                            pygame.draw.rect(screen, (0, 0, 0), (295, 485 + 30 * n, 300, 30), 3)

                            for m in range(3):
                                if gameInfo.towers[0].upgrades[n] > m:
                                    pygame.draw.circle(screen, (0, 255, 0), (560 + 12 * m, 497 + 30 * n), 5)
                                pygame.draw.circle(screen, (0, 0, 0), (560 + 12 * m, 497 + 30 * n), 5, 2)

                    else:
                        move()

                        if n == 0:
                            for enemy in gameInfo.enemies:
                                enemy.updateRegen()
                            n = 1
                        else:
                            n = 0

                    if len(gameInfo.enemies) == 0:
                        info.tutorialPhase = 5
                        break

                    for obj in gameInfo.projectiles + gameInfo.towers + gameInfo.enemies:
                        obj.draw()

                    pygame.display.update()
                    clock.tick(MaxFPS)

            elif info.tutorialPhase == 5:
                while True:
                    mx, my = pygame.mouse.get_pos()

                    if len(gameInfo.enemies) == 0:
                        Enemy('0', 0, '0', camo=True)

                    gameInfo.Map = Maps[5]

                    screen.fill(gameInfo.Map.backgroundColor)
                    for i in range(len(gameInfo.Map.path)):
                        for j in range(len(gameInfo.Map.path[i]) - 1):
                            lineWidth = 14 if gameInfo.Map.path[i][j][0] != gameInfo.Map.path[i][j + 1][0] and gameInfo.Map.path[i][j][1] != gameInfo.Map.path[i][j + 1][1] else 10
                            pygame.draw.line(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][j], gameInfo.Map.path[i][j + 1], lineWidth)
                            pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][j + 1], lineWidth // 2)
                        pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][0], 10)
                        pygame.draw.circle(screen, gameInfo.Map.pathColor, gameInfo.Map.path[i][-1], 10)

                    cont = True
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            save()
                            quit()

                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                info.status = 'mapSelect'
                                cont = False

                                gameInfo.reset()

                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                if 295 <= mx <= 595 and 545 < my <= 575:
                                    gameInfo.towers[0].upgrades[2] = min(gameInfo.towers[0].upgrades[2] + 1, 3)

                    if not cont:
                        break

                    if gameInfo.enemies[0].totalMovement > 250 and gameInfo.towers[0].upgrades[2] < 3:
                        centredPrint(font, 'Oh no... Now a Camo balloon? Upgrade your turret again...', (500, 375))

                        for n in range(3):
                            if gameInfo.towers[0].upgrades[n] == 3:
                                pygame.draw.rect(screen, (255, 255, 191), (295, 485 + 30 * n, 300, 30))
                                centredPrint(font, 'MAX', (445, 500 + 30 * n))
                            else:
                                if 295 <= mx <= 595 and 485 + 30 * n < my <= 515 + 30 * n:
                                    if n == 2:
                                        color = (200, 200, 200)
                                    else:
                                        color = (255, 180, 180)

                                else:
                                    if n == 2:
                                        color = (100, 100, 100)
                                    else:
                                        color = (255, 100, 100)

                                pygame.draw.rect(screen, color, (295, 485 + 30 * n, 300, 30))
                                if n == 2:
                                    leftAlignPrint(font, f'{gameInfo.towers[0].upgradeNames[2][gameInfo.towers[0].upgrades[2]]} [FREE]', (300, 500 + n * 30), (32, 32, 32))
                                else:
                                    leftAlignPrint(font, f'{gameInfo.towers[0].upgradeNames[n][gameInfo.towers[0].upgrades[n]]} [${gameInfo.towers[0].upgradePrices[n][gameInfo.towers[0].upgrades[n]]}]', (300, 500 + n * 30), (32, 32, 32))

                            pygame.draw.rect(screen, (0, 0, 0), (295, 485 + 30 * n, 300, 30), 3)

                            for m in range(3):
                                if gameInfo.towers[0].upgrades[n] > m:
                                    pygame.draw.circle(screen, (0, 255, 0), (560 + 12 * m, 497 + 30 * n), 5)
                                pygame.draw.circle(screen, (0, 0, 0), (560 + 12 * m, 497 + 30 * n), 5, 2)

                    else:
                        move()

                    if len(gameInfo.enemies) == 0:
                        info.tutorialPhase = 6
                        break

                    for obj in gameInfo.projectiles + gameInfo.towers + gameInfo.enemies:
                        obj.draw()

                    pygame.display.update()
                    clock.tick(MaxFPS)

            elif info.tutorialPhase == 6:
                while True:
                    screen.fill((200, 200, 200))

                    centredPrint(mediumFont, 'Find out more as you continue playing the game!', (500, 150))
                    centredPrint(font, 'Press [SPACE] to continue!', (500, 400))

                    cont = True
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            save()
                            quit()

                        elif event.type == pygame.KEYDOWN:
                            if event.key in [pygame.K_ESCAPE, pygame.K_SPACE]:
                                info.status = 'mapSelect'
                                cont = False

                                gameInfo.reset()

                    if not cont:
                        break

                    pygame.display.update()

        elif info.status == 'mapSelect':
            scroll = 0

            while True:
                clock.tick(MaxFPS)

                mx, my = pygame.mouse.get_pos()

                screen.fill((68, 68, 68))

                n = 0
                for Map in Maps:
                    if info.PBs[Map.name] == None and info.sandboxMode:
                        pygame.draw.rect(screen, (32, 32, 32), (10, 40 * n + 60 - scroll, 825, 30))
                        pygame.draw.rect(screen, (0, 0, 0), (10, 40 * n + 60 - scroll, 825, 30), 3)
                        leftAlignPrint(font, Map.name.upper(), (20, 74 + n * 40 - scroll))
                        centredPrint(font, LOCKED, (900, 74 + n * 40 - scroll))

                    elif info.PBs[Map.name] != LOCKED:
                        pygame.draw.rect(screen, Map.displayColor, (10, 40 * n + 60 - scroll, 825, 30))
                        if 10 <= mx <= 835 and 40 * n + 60 - scroll <= my <= 40 * n + 90 - scroll and 50 <= my <= 500:
                            pygame.draw.rect(screen, (128, 128, 128), (10, 40 * n + 60 - scroll, 825, 30), 5)
                        else:
                            pygame.draw.rect(screen, (0, 0, 0), (10, 40 * n + 60 - scroll, 825, 30), 3)

                        leftAlignPrint(font, Map.name.upper(), (20, 74 + n * 40 - scroll))
                        try:
                            if info.PBs[Map.name] >= 300:
                                centredPrint(font, '[Best: 300]', (900, 74 + n * 40 - scroll), (100, 0, 0))
                            elif info.PBs[Map.name] >= 250:
                                centredPrint(font, f'[Best: {info.PBs[Map.name]}]', (900, 74 + n * 40 - scroll), (225, 225, 0))
                            else:
                                centredPrint(font, f'[Best: {info.PBs[Map.name]}]', (900, 74 + n * 40 - scroll))

                        except TypeError:
                            pass

                    else:
                        pygame.draw.rect(screen, (32, 32, 32), (10, 40 * n + 60 - scroll, 825, 30))
                        pygame.draw.rect(screen, (0, 0, 0), (10, 40 * n + 60 - scroll, 825, 30), 3)
                        leftAlignPrint(font, Map.name.upper(), (20, 74 + n * 40 - scroll))
                        centredPrint(font, LOCKED, (900, 74 + n * 40 - scroll))

                    n += 1

                pygame.draw.rect(screen, (68, 68, 68), (0, 0, 1000, 50))
                centredPrint(font, 'Map Select', (500, 30), (255, 255, 255))

                centredBlit(tokenImage, (830, 30))
                pygame.draw.rect(screen, (128, 128, 128), (850, 15, 100, 30))
                pygame.draw.rect(screen, (0, 0, 0), (850, 15, 100, 30), 2)
                leftAlignPrint(font, str(info.tokens), (860, 30))

                pygame.draw.rect(screen, (200, 200, 200), (10, 40 * n + 60 - scroll, 825, 30))
                if 10 <= mx <= 835 and 40 * n + 60 <= my + scroll <= 40 * n + 90 and 50 <= my <= 500:
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

                pygame.draw.rect(screen, (0, 225, 0) if info.sandboxMode else (255, 0, 0), (200, 550, 200, 30))
                centredPrint(font, 'Sandbox Mode: ' + ('ON' if info.sandboxMode else 'OFF'), (300, 565))
                if 200 <= mx <= 400 and 550 <= my <= 580:
                    pygame.draw.rect(screen, (128, 128, 128), (200, 550, 200, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (200, 550, 200, 30), 3)

                pygame.draw.rect(screen, (200, 200, 200), (525, 510, 125, 30))
                centredPrint(font, 'Replay', (587, 525))
                if 525 <= mx <= 650 and 510 <= my <= 540:
                    pygame.draw.rect(screen, (128, 128, 128), (525, 510, 125, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (525, 510, 125, 30), 3)

                pygame.draw.rect(screen, (200, 200, 200), (675, 510, 125, 30))
                centredPrint(font, 'Shop', (737, 525))
                if 675 <= mx <= 800 and 510 <= my <= 540:
                    pygame.draw.rect(screen, (128, 128, 128), (675, 510, 125, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (675, 510, 125, 30), 3)

                pygame.draw.rect(screen, (200, 200, 200), (825, 510, 150, 30))
                centredPrint(font, 'Cosmetics', (900, 525))
                if 825 <= mx <= 975 and 510 <= my <= 540:
                    pygame.draw.rect(screen, (128, 128, 128), (825, 510, 150, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (825, 510, 150, 30), 3)

                if info.newRunes > 0:
                    pygame.draw.circle(screen, (255, 0, 0), (975, 510), 10)
                    pygame.draw.circle(screen, (0, 0, 0), (975, 510), 10, 2)
                    centredPrint(font, str(info.newRunes), (975, 508), (255, 255, 255))

                pygame.draw.rect(screen, (200, 200, 200), (675, 550, 125, 30))
                centredPrint(font, 'Stats', (737, 565))
                if 675 <= mx <= 800 and 550 <= my <= 580:
                    pygame.draw.rect(screen, (128, 128, 128), (675, 550, 125, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (675, 550, 125, 30), 3)

                pygame.draw.rect(screen, (200, 200, 200), (825, 550, 150, 30))
                centredPrint(font, 'Achievements', (900, 565))
                if 825 <= mx <= 975 and 550 <= my <= 580:
                    pygame.draw.rect(screen, (128, 128, 128), (825, 550, 150, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (825, 550, 150, 30), 3)

                tiersNotClaimed = 0
                for achievement, requirement in achievementRequirements.items():
                    stat = info.statistics[requirement['attr']]
                    highest = 0
                    for tier in requirement['tiers']:
                        if stat >= tier:
                            highest += 1

                    tiersNotClaimed += highest - info.claimedAchievementRewards[achievement]

                if tiersNotClaimed > 0:
                    pygame.draw.circle(screen, (255, 0, 0), (975, 550), 10)
                    pygame.draw.circle(screen, (0, 0, 0), (975, 550), 10, 2)
                    centredPrint(font, str(tiersNotClaimed), (975, 548), (255, 255, 255))

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
                                    if 40 * n + 60 - scroll <= my <= 40 * n + 90 - scroll and 50 <= my <= 500 and list(info.PBs.values())[n] != LOCKED and (list(info.PBs.values())[n] is not None or not info.sandboxMode):
                                        gameInfo.Map = Maps[n]
                                        info.status = 'game'
                                        gameInfo.coins = math.inf if info.sandboxMode else defaults['coins']
                                        gameInfo.HP = math.inf if info.sandboxMode else defaults['HP']
                                        info.gameReplayData.clear()
                                        skinsEquipped = [getSkin(s) for s in info.skinsEquipped]
                                        skinLoaded = loadSkin(info.skinsEquipped[1], Towers.__subclasses__())
                                        if skinLoaded is not None:
                                            towerImages = skinLoaded

                                        try:
                                            PowerUps.objects.clear()
                                        except AttributeError:
                                            pass

                                        try:
                                            RuneEffects.effects.clear()
                                        except AttributeError:
                                            pass

                                        mouseTrail.clear()
                                        cont = False

                            if 10 <= mx <= 935 and 40 * len(Maps) + 60 <= my + scroll <= 40 * len(Maps) + 90 and my <= 500:
                                gameInfo.Map = random.choice([Map for Map in Maps if info.PBs[Map.name] != LOCKED])
                                info.status = 'game'
                                gameInfo.coins = math.inf if info.sandboxMode else defaults['coins']
                                gameInfo.HP = math.inf if info.sandboxMode else defaults['HP']
                                info.gameReplayData.clear()
                                skinsEquipped = [getSkin(s) for s in info.skinsEquipped]
                                skinLoaded = loadSkin(info.skinsEquipped[1], Towers.__subclasses__())
                                if skinLoaded is not None:
                                    towerImages = skinLoaded

                                try:
                                    PowerUps.objects.clear()
                                except AttributeError:
                                    pass

                                try:
                                    RuneEffects.effects.clear()
                                except AttributeError:
                                    pass

                                mouseTrail.clear()
                                cont = False

                            if 25 <= mx <= 150 and 550 <= my <= 580:
                                info.status = 'mapMaker'
                                cont = False

                            if 525 <= mx <= 650 and 510 <= my <= 540:
                                path = fileSelection(os.path.join(os.path.dirname(curr_path), 'replay-files'))
                                if type(path) is str and removeCharset(path, ' ') != '':
                                    try:
                                        screen.fill((200, 200, 200))
                                        centredPrint(largeFont, f'Tower Defense v{__version__}', (500, 200), (100, 100, 100))
                                        centredPrint(mediumFont, 'Loading...', (500, 300), (100, 100, 100))
                                        pygame.display.update()

                                        info.gameReplayData, gameInfo.Map = pickle.load(open(path, 'rb'))
                                        gameInfo.ticks = 0
                                        info.status = 'replay'
                                        cont = False
                                        print(f'Replaying replay file {path}!')

                                    except FileNotFoundError:
                                        print(f'File \"{path}\" not found!')

                                    except (EOFError, ValueError, TypeError, UnpicklingError) as e:
                                        print(f'Error loading Replay File \"{path}\"! See details: {e}')

                            if 675 <= mx <= 800 and 510 <= my <= 540:
                                now = datetime.datetime.now(tz=pytz.timezone('Singapore'))
                                info.status = 'shop'
                                if [now.year, now.month, now.day] != info.lastOpenShop:
                                    refreshShop()
                                    info.lastOpenShop = [now.year, now.month, now.day]
                                cont = False

                            if 825 <= mx <= 975 and 510 <= my <= 540:
                                info.status = 'cosmetics'
                                info.newRunes = 0
                                cont = False

                            if 675 <= mx <= 800 and 550 <= my <= 580:
                                info.status = 'statistics'
                                info.statistics['wins'] = updateDict(info.statistics['wins'], [Map.name for Map in Maps])
                                cont = False

                            if 825 <= mx <= 975 and 550 <= my <= 580:
                                info.status = 'achievements'
                                cont = False

                            if 200 <= mx <= 400 and 550 <= my <= 580:
                                info.sandboxMode = not info.sandboxMode

                        elif event.button == 4:
                            scroll = max(scroll - 5, 0)

                        elif event.button == 5:
                            scroll = min(scroll + 5, max(40 * n + 90 - 490, 0))

                if not cont:
                    break

        elif info.status == 'win':
            saved = False
            while True:
                mx, my = pygame.mouse.get_pos()

                screen.fill((32, 32, 32))

                centredPrint(largeFont, 'You Win!', (500, 125), (255, 255, 255))

                if gameInfo.FinalHP == math.inf:
                    centredPrint(font, f'Your Final Score: {INFINITYSTR}', (500, 250), (255, 255, 255))
                else:
                    centredPrint(font, f'Your Final Score: {gameInfo.FinalHP}', (500, 250), (255, 255, 255))

                centredPrint(font, f'Press [SPACE] to continue!', (500, 280), (255, 255, 255))

                if not saved:
                    pygame.draw.rect(screen, (128, 128, 128), (800, 550, 175, 30))
                    centredPrint(font, 'Download Replay', (887, 565))
                    if 800 <= mx <= 975 and 550 <= my <= 580:
                        pygame.draw.rect(screen, (64, 64, 64), (800, 550, 175, 30), 3)
                    else:
                        pygame.draw.rect(screen, (0, 0, 0), (800, 550, 175, 30), 3)

                if info.sandboxMode:
                    centredPrint(font, 'You were playing on Sandbox Mode!', (500, 350), (255, 255, 255))
                else:
                    totalLength = font.size(f'+{gameInfo.FinalHP // 2 + 10}')[0] + 40
                    leftAlignPrint(font, f'+{gameInfo.FinalHP // 2 + 10}', (500 - totalLength // 2, 350), (255, 255, 255))
                    centredBlit(tokenImage, (485 + totalLength // 2, 350))

                pygame.display.update()

                cont = True
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            info.status = 'mapSelect'
                            cont = False
                            info.gameReplayData.clear()

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if not saved:
                                if 800 <= mx <= 975 and 550 <= my <= 580:
                                    filename = f'replay-{int(time.time())}.txt'
                                    open(os.path.join(curr_path, os.pardir, 'replay-files', filename), 'w')

                                    try:
                                        with open(os.path.join(curr_path, os.pardir, 'replay-files', filename), 'wb') as file:
                                            pickle.dump([info.gameReplayData, gameInfo.Map], file)
                                        saved = True
                                        info.gameReplayData.clear()

                                    except FileNotFoundError as e:
                                        print(f'An error occured while saving {filename} to {os.path.join(curr_path, "replay-files")}. See details: {e}')
                                        saved = False

                    elif event.type == pygame.QUIT:
                        save()
                        quit()

                clock.tick(MaxFPS)
                if not cont:
                    break

        elif info.status == 'lose':
            cont = False
            gameInfo.reset()
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
                            info.gameReplayData.clear()

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

                        if 800 <= mx <= 900 and 450 <= my <= 480:
                            pygame.draw.rect(screen, (128, 128, 128), (800, 450, 100, 30), 5)
                        else:
                            pygame.draw.rect(screen, (0, 0, 0), (800, 450, 100, 30), 3)

                    pygame.draw.rect(screen, (255, 0, 0), (30, 550, 100, 30))
                    centredPrint(font, 'Cancel', (80, 565))
                    if 30 <= mx <= 130 and 550 <= my <= 580:
                        pygame.draw.rect(screen, (128, 128, 128), (30, 550, 100, 30), 5)
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
                                                info.mapMakerData[field] = (letter.upper() if (uppercase or shifting) else letter.lower()) + info.mapMakerData[field]
                                            elif charInsertIndex == len(info.mapMakerData[field]):
                                                info.mapMakerData[field] += (letter.upper() if (uppercase or shifting) else letter.lower())
                                            else:
                                                info.mapMakerData[field] = info.mapMakerData[field][:charInsertIndex] + (letter.upper() if (uppercase or shifting) else letter.lower()) + info.mapMakerData[field][charInsertIndex:]

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

                                    info.mapMakerData['path'] = [[]]
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

                    y = 150
                    for fieldName in ['name', 'backgroundColor', 'pathColor']:
                        info.mapMakerData[fieldName] = str(info.mapMakerData[fieldName])

                        txt = info.mapMakerData[fieldName]
                        if ticks < 25 and fieldName == field:
                            length = font.size(txt[:charInsertIndex])[0]
                            pygame.draw.line(screen, (0, 0, 0), (length + 230, y), (length + 230, y + 20))

                        leftAlignPrint(font, txt, (230, y + 10))
                        y += 100

                    pygame.display.update()
                    ticks = (ticks + 1) % 50
                    clock.tick(MaxFPS)

            else:
                while True:
                    mx, my = pygame.mouse.get_pos()

                    screen.fill((200, 200, 200))
                    centredPrint(mediumFont, 'Map Maker', (500, 50))
                    pygame.draw.rect(screen, (0, 0, 0), (100, 125, 800, 450), 5)
                    pygame.draw.rect(screen, info.mapMakerData['backgroundColor'], (100, 125, 800, 450))

                    cx = None
                    cy = None
                    placable = True

                    if mx <= 100:
                        cx = 100
                        placable = False

                    if mx >= 900:
                        cx = 900
                        placable = False

                    if my <= 125:
                        cy = 125
                        placable = False

                    if my >= 575:
                        cy = 575
                        placable = False

                    try:
                        ncx, ncy = getClosestPoint(mx, my, sx=info.mapMakerData['path'][-1][-1][0], sy=info.mapMakerData['path'][-1][-1][1])
                    except IndexError:
                        ncx, ncy = getClosestPoint(mx, my)

                    if cx is None:
                        cx = ncx

                    if cy is None:
                        cy = ncy

                    if 100 <= cx <= 900 and 125 <= cy <= 575:
                        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), 3)

                    for i in range(len(info.mapMakerData['path'])):
                        for j in range(len(info.mapMakerData['path'][i]) - 1):
                            lineWidth = 14 if info.mapMakerData['path'][i][j][0] != info.mapMakerData['path'][i][j + 1][0] and info.mapMakerData['path'][i][j][1] != info.mapMakerData['path'][i][j + 1][1] else 10
                            pygame.draw.line(screen, info.mapMakerData['pathColor'], info.mapMakerData['path'][i][j], info.mapMakerData['path'][i][j + 1], lineWidth)
                            pygame.draw.circle(screen, info.mapMakerData['pathColor'], info.mapMakerData['path'][i][j + 1], lineWidth // 2)

                            try:
                                pygame.draw.circle(screen, info.mapMakerData['pathColor'], info.mapMakerData['path'][i][0], 10)
                            except IndexError:
                                pass

                            try:
                                pygame.draw.circle(screen, info.mapMakerData['pathColor'], info.mapMakerData['path'][i][-1], 10)
                            except IndexError:
                                pass

                    pygame.draw.rect(screen, (200, 200, 200), (90, 115, 900, 10))
                    pygame.draw.rect(screen, (200, 200, 200), (90, 575, 900, 10))
                    pygame.draw.rect(screen, (200, 200, 200), (90, 125, 10, 450))
                    pygame.draw.rect(screen, (200, 200, 200), (900, 125, 10, 450))

                    left = (cx - 100) // 25
                    right = 32 - left
                    up = (cy - 125) // 25
                    down = 18 - up

                    pygame.draw.line(screen, (0, 0, 0), (100, 115), (900, 115), 2)
                    pygame.draw.line(screen, (0, 0, 0), (910, 125), (910, 575), 2)

                    pygame.draw.line(screen, (0, 0, 0), (cx, 110), (cx, 120), 2)
                    pygame.draw.line(screen, (0, 0, 0), (905, cy), (915, cy), 2)

                    if left > 0:
                        centredPrint(font, str(left), (50 + cx // 2, 90))
                    if right > 0:
                        centredPrint(font, str(right), (450 + cx // 2, 90))
                    if up > 0:
                        centredPrint(font, str(up), (930, 62 + cy // 2))
                    if down > 0:
                        centredPrint(font, str(down), (930, 287 + cy // 2))

                    if len(info.mapMakerData['path'][-1]) >= 2:
                        pygame.draw.rect(screen, (44, 255, 44), (20, 420, 60, 30))
                        centredPrint(font, 'Done', (50, 435))
                        if 20 <= mx <= 80 and 420 <= my <= 450:
                            pygame.draw.rect(screen, (128, 128, 128), (20, 420, 60, 30), 5)
                        else:
                            pygame.draw.rect(screen, (0, 0, 0), (20, 420, 60, 30), 3)

                        pygame.draw.rect(screen, (100, 100, 100), (20, 460, 60, 30))
                        centredPrint(font, 'Add', (50, 475))
                        if 20 <= mx <= 80 and 460 <= my <= 490:
                            pygame.draw.rect(screen, (128, 128, 128), (20, 460, 60, 30), 5)
                        else:
                            pygame.draw.rect(screen, (0, 0, 0), (20, 460, 60, 30), 3)

                    pygame.draw.rect(screen, (100, 100, 100), (20, 500, 60, 30))
                    centredPrint(font, 'Undo', (50, 515))
                    if 20 <= mx <= 80 and 500 <= my <= 530:
                        pygame.draw.rect(screen, (128, 128, 128), (20, 500, 60, 30), 5)
                    else:
                        pygame.draw.rect(screen, (0, 0, 0), (20, 500, 60, 30), 3)

                    pygame.draw.rect(screen, (100, 100, 100), (20, 540, 60, 30))
                    centredPrint(font, 'Clear', (50, 555))
                    if 20 <= mx <= 80 and 540 <= my <= 570:
                        pygame.draw.rect(screen, (128, 128, 128), (20, 540, 60, 30), 5)
                    else:
                        pygame.draw.rect(screen, (0, 0, 0), (20, 540, 60, 30), 3)

                    pygame.display.update()

                    cont = True
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            save()
                            quit()

                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                if 100 <= cx <= 900 and 125 <= cy <= 575 and placable:
                                    info.mapMakerData['path'][-1].append([cx, cy])

                                if len(info.mapMakerData['path'][-1]) >= 2:
                                    if 20 <= mx <= 80 and 420 <= my <= 450:
                                        mapShiftedPath = []
                                        for path in info.mapMakerData['path']:
                                            mapShiftedPath.append([])
                                            for point in path:
                                                mapShiftedPath[-1].append([point[0] - 100, point[1] - 125])

                                        print(f'This is the map code for your map!\n\nMap({mapShiftedPath}, \'{info.mapMakerData["name"]}\', {tuple(info.mapMakerData["backgroundColor"])}, {tuple(info.mapMakerData["pathColor"])})')
                                        info.status = 'mapSelect'
                                        info.mapMakerData = defaults['mapMakerData'].copy()
                                        cont = False

                                    if 20 <= mx <= 80 and 460 <= my <= 490:
                                        info.mapMakerData['path'].append([])

                                if 20 <= mx <= 80 and 500 <= my <= 530:
                                    try:
                                        info.mapMakerData['path'][-1] = info.mapMakerData['path'][-1][:-1]
                                    except IndexError:
                                        pass

                                if 20 <= mx <= 80 and 540 <= my <= 570:
                                    if info.mapMakerData['path'][-1]:
                                        info.mapMakerData['path'][-1].clear()
                                    else:
                                        info.mapMakerData['path'] = [[]]

                    if not cont:
                        break

                    clock.tick(MaxFPS)

        elif info.status == 'replay':
            screen.fill((200, 200, 200))
            pygame.draw.rect(screen, (0, 0, 0), (100, 75, 800, 450), 3)
            pygame.display.update()

            replayLength = len(info.gameReplayData)
            replayLengthStr = durationToString(replayLength / ReplayFPS)

            while True:
                mx, my = pygame.mouse.get_pos()

                screen.fill((0, 0, 0))

                pygame.draw.rect(screen, (0, 0, 0), (100, 75, 800, 450), 3)
                pygame.draw.rect(screen, gameInfo.Map.backgroundColor, (100, 75, 800, 450))

                for i in range(len(gameInfo.Map.path)):
                    for j in range(len(gameInfo.Map.path[i]) - 1):
                        lineWidth = 14 if gameInfo.Map.path[i][j][0] != gameInfo.Map.path[i][j + 1][0] and gameInfo.Map.path[i][j][1] != gameInfo.Map.path[i][j + 1][1] else 10
                        x1, y1 = gameInfo.Map.path[i][j]
                        x2, y2 = gameInfo.Map.path[i][j + 1]
                        pygame.draw.line(screen, gameInfo.Map.pathColor, [x1 + 100, y1 + 75], [x2 + 100, y2 + 75], lineWidth)
                        pygame.draw.circle(screen, gameInfo.Map.pathColor, [x2 + 100, y2 + 75], lineWidth // 2)

                try:
                    data = info.gameReplayData.copy()[gameInfo.ticks]
                except IndexError:
                    data = info.gameReplayData.copy()[-1]

                try:
                    for tower in data['towers']:
                        towerName, x, y, imageFrame = tower

                        color = None
                        for TowerType in Towers.__subclasses__():
                            if TowerType.name == towerName:
                                color = TowerType.color

                        try:
                            if towerImages[towerName] is not None:
                                try:
                                    screen.blit(towerImages[towerName], (x + 85, y + 55))
                                except TypeError:
                                    screen.blit(towerImages[towerName][imageFrame], (x + 85, y + 55))

                            elif color is None:
                                raise AttributeError
                            else:
                                pygame.draw.circle(screen, color, (x + 100, y + 75), 15)

                        except AttributeError:
                            pygame.draw.circle(screen, (200, 200, 200), (x + 100, y + 75), 15)

                except KeyError:
                    pass

                try:
                    for enemy in data['enemies']:
                        camo, regen, tier, x, y, HP, MaxHP = enemy

                        if tier in bosses:
                            healthPercent = HP / trueHP[tier]

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

                            pygame.draw.rect(screen, (128, 128, 128), (x + 50, y + 50, 100, 5))
                            pygame.draw.rect(screen, color, (x + 50, y + 50, round(HP / MaxHP * 100), 5))
                            pygame.draw.rect(screen, (0, 0, 0), (x + 50, y + 50, 100, 5), 1)
                            centredPrint(font, f'{math.ceil(HP / MaxHP * 100)}%', (x + 100, y + 40))

                        pygame.draw.circle(screen, enemyColors[str(tier)], (x + 100, y + 75), 20 if tier in bosses else 10)
                        if camo:
                            pygame.draw.circle(screen, (0, 0, 0), (x + 100, y + 75), 20 if tier in bosses else 10, 2)
                        if regen:
                            pygame.draw.circle(screen, (255, 105, 180), (x + 100, y + 75), 20 if tier in bosses else 10, 2)

                except KeyError:
                    pass

                try:
                    for proj in data['projectiles']:
                        color, x, y = proj

                        pygame.draw.circle(screen, color, (x + 100, y + 75), 3)

                except KeyError:
                    pass

                try:
                    for piercingProj in data['piercingProjectiles']:
                        x, y = piercingProj

                        pygame.draw.circle(screen, (16, 16, 16), (x + 100, y + 75), 5)

                except KeyError:
                    pass

                try:
                    for effect in data['effects']:
                        if effect[0] == 'circle':
                            pygame.draw.circle(screen, effect[1], (effect[2][0] + 100, effect[2][1] + 75), effect[3])

                        if effect[0] == 'line':
                            pygame.draw.line(screen, effect[1], (effect[2][0] + 100, effect[2][1] + 75), (effect[3][0] + 100, effect[3][1] + 75), 3)

                except KeyError:
                    pass

                pygame.draw.rect(screen, (200, 200, 200), (0, 0, 1000, 75))
                pygame.draw.rect(screen, (200, 200, 200), (0, 0, 100, 675))
                pygame.draw.rect(screen, (200, 200, 200), (900, 0, 100, 675))
                pygame.draw.rect(screen, (200, 200, 200), (0, 525, 1000, 75))

                centredPrint(mediumFont, 'Replay', (500, 35))

                pygame.draw.rect(screen, (0, 255, 0), (160, 560, 680 * gameInfo.ticks / replayLength, 10))
                pygame.draw.rect(screen, (100, 100, 100), (160, 560, 680, 10), 2)

                centredPrint(tinyFont, f'{durationToString((gameInfo.ticks + 1) / ReplayFPS)}/{replayLengthStr}', (920, 565))

                if 160 <= mx <= 840 and 560 <= my <= 570:
                    pygame.draw.polygon(screen, (100, 100, 100), ((mx - 5, 545), (mx - 5, 555), (mx, 560), (mx + 5, 555), (mx + 5, 545)))
                    centredPrint(tinyFont, durationToString(replayLength * (mx - 160) / 680 / ReplayFPS), (mx, 535))

                pygame.draw.rect(screen, (255, 0, 0), (30, 550, 100, 30))
                centredPrint(font, 'Close', (80, 565))
                if 30 <= mx <= 130 and 550 <= my <= 580:
                    pygame.draw.rect(screen, (64, 64, 64), (30, 550, 100, 30), 3)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (30, 550, 100, 30), 3)

                cont = True
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        save()
                        quit()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if 30 <= mx <= 130 and 550 <= my <= 580:
                                cont = False
                                info.status = 'mapSelect'

                if not cont:
                    break

                if pygame.mouse.get_pressed(3)[0]:
                    if 160 <= mx <= 840 and 560 <= my <= 570:
                        gameInfo.ticks = round(replayLength * (mx - 160) / 680)

                clock.tick(ReplayFPS)
                pygame.display.update()

                if gameInfo.ticks < replayLength - 1:
                    gameInfo.ticks += 1

        elif info.status == 'shop':
            while True:
                mx, my = pygame.mouse.get_pos()

                screen.fill((200, 200, 200))

                centredPrint(mediumFont, 'Shop', (500, 40))

                for n in range(len(info.shopData)):
                    x = 100 + 300 * (n % 3)
                    y = 100 if n < 3 else 325

                    pygame.draw.rect(screen, (100, 100, 100), (x, y, 200, 200))
                    if x <= mx <= x + 200 and y <= my <= y + 200:
                        pygame.draw.rect(screen, (128, 128, 128), (x, y, 200, 200), 5)
                    else:
                        pygame.draw.rect(screen, (0, 0, 0), (x, y, 200, 200), 3)

                    if info.shopData[n]['type'] == 'skin':
                        centredBlit(getSkin(info.shopData[n]['item']).imageTexture, (x + 100, y + 100))

                    if info.shopData[n]['type'] == 'rune':
                        centredBlit(getRune(info.shopData[n]['item']).imageTexture, (x + 100, y + 100))

                    if info.shopData[n]['type'] == 'powerUp':
                        centredBlit(powerUps[info.shopData[n]['item']][1], (x + 100, y + 100))
                        centredPrint(tinyFont, powerUps[info.shopData[n]['item']][2], (x + 100, y + 180))
                    else:
                        centredPrint(tinyFont, info.shopData[n]['item'], (x + 100, y + 180))

                    if info.shopData[n]['count'] > 1:
                        rightAlignPrint(font, f'x{info.shopData[n]["count"]}', (x + 190, y + 20))

                    if info.shopData[n]['bought']:
                        leftAlignPrint(font, 'BOUGHT', (x + 10, y + 20))
                    else:
                        centredBlit(tokenImage, (x + 20, y + 20))
                        price = info.shopData[n]['price']
                        if price == 0:
                            leftAlignPrint(font, 'FREE', (x + 38, y + 20), (225, 225, 0))
                        else:
                            if info.tokens >= price:
                                leftAlignPrint(font, str(price), (x + 38, y + 20))
                            else:
                                leftAlignPrint(font, str(price), (x + 38, y + 20), (255, 0, 0))

                centredBlit(tokenImage, (830, 30))
                pygame.draw.rect(screen, (128, 128, 128), (850, 15, 100, 30))
                pygame.draw.rect(screen, (0, 0, 0), (850, 15, 100, 30), 2)
                leftAlignPrint(font, str(info.tokens), (860, 30))

                t = -28800 - time.time() % 86400
                if t < 0:
                    t += 86400

                if t <= 0:
                    refreshShop()

                leftAlignPrint(tinyFont, f'Time until refresh: {durationToString(t)}', (20, 20))

                pygame.draw.rect(screen, (255, 0, 0), (30, 550, 100, 30))
                centredPrint(font, 'Close', (80, 565))
                if 30 <= mx <= 130 and 550 <= my <= 580:
                    pygame.draw.rect(screen, (128, 128, 128), (30, 550, 100, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (30, 550, 100, 30), 3)

                cont = True
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        save()
                        quit()

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if 30 <= mx <= 130 and 550 <= my <= 580:
                                cont = False
                                info.status = 'mapSelect'

                            for n in range(len(info.shopData)):
                                x = 100 + 300 * (n % 3)
                                y = 100 if n < 3 else 325

                                if x <= mx <= x + 200 and y <= my <= y + 200 and not info.shopData[n]['bought']:
                                    if info.tokens >= info.shopData[n]['price']:
                                        if info.shopData[n]['type'] == 'skin':
                                            info.skins.append(info.shopData[n]['item'])
                                        if info.shopData[n]['type'] == 'rune':
                                            info.runes.append(info.shopData[n]['item'])
                                        if info.shopData[n]['type'] == 'powerUp':
                                            info.powerUps[info.shopData[n]['item']] += info.shopData[n]['count']

                                        info.tokens -= info.shopData[n]['price']
                                        info.shopData[n]['bought'] = True

                if not cont:
                    break

                pygame.display.update()

        elif info.status == 'cosmetics':
            if info.cosmeticPage == 'runes':
                while True:
                    mx, my = pygame.mouse.get_pos()

                    screen.fill((200, 200, 200))

                    pygame.draw.rect(screen, (255, 0, 0), (30, 550, 100, 30))
                    centredPrint(font, 'Close', (80, 565))
                    if 30 <= mx <= 130 and 550 <= my <= 580:
                        pygame.draw.rect(screen, (128, 128, 128), (30, 550, 100, 30), 5)
                    else:
                        pygame.draw.rect(screen, (0, 0, 0), (30, 550, 100, 30), 3)

                    pygame.draw.rect(screen, (160, 160, 160), (820, 550, 150, 30))
                    centredPrint(font, 'Next Page', (895, 565))
                    if 820 <= mx <= 970 and 550 <= my <= 580:
                        pygame.draw.rect(screen, (128, 128, 128), (820, 550, 150, 30), 5)
                    else:
                        pygame.draw.rect(screen, (0, 0, 0), (820, 550, 150, 30), 3)

                    pygame.draw.rect(screen, (160, 160, 160), (440, 100, 120, 120))
                    centredPrint(mediumFont, 'Runes', (500, 40))
                    centredPrint(font, 'Click on a Rune to equip!' if info.equippedRune is None else 'Equipped Rune:', (500, 75))

                    pygame.draw.rect(screen, (160, 160, 160), (50, 250, 900, 225))
                    if len(info.runes) == 0:
                        centredPrint(font, 'You have no runes!', (500, 362))
                        centredPrint(tinyFont, 'Win some battles to earn some runes!', (500, 390))

                    x = 0
                    y = 0
                    for rune in info.runes:
                        try:
                            pygame.draw.rect(screen, (64, 64, 64), (x * 75 + 52, y * 75 + 252, 70, 70))
                            getRune(rune).draw(screen, x * 75 + 87, y * 75 + 287, 66)

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
                            getRune(info.equippedRune).draw(screen, 500, 160)
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

                                if 820 <= mx <= 970 and 550 <= my <= 580:
                                    info.cosmeticPage = 'skins'
                                    cont = False

                                if 440 <= mx <= 560 and 100 <= my <= 220:
                                    info.equippedRune = None

                                if 50 <= mx <= 950 and 250 <= my <= 475:
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
                                    shifting = pygame.key.get_pressed()[pygame.K_LSHIFT]

                                    if event.key == pygame.K_UP:
                                        info.equippedRune = info.runes[max(info.runes.index(info.equippedRune) - 12, 0)]
                                    if event.key == pygame.K_DOWN:
                                        info.equippedRune = info.runes[min(info.runes.index(info.equippedRune) + 12, len(info.runes) - 1)]
                                    if event.key == pygame.K_LEFT:
                                        info.equippedRune = info.runes[max(info.runes.index(info.equippedRune) - 1, 0)]
                                    if event.key == pygame.K_RIGHT:
                                        if shifting:
                                            info.cosmeticPage = 'skins'
                                            cont = False
                                        else:
                                            info.equippedRune = info.runes[min(info.runes.index(info.equippedRune) + 1, len(info.runes) - 1)]

                                except ValueError:
                                    print('tower-defense.core: Fatal - There seems to be a problem with your equipped rune.')

                    if not cont:
                        break

                    pygame.display.update()

            elif info.cosmeticPage == 'skins':
                while True:
                    mx, my = pygame.mouse.get_pos()

                    screen.fill((200, 200, 200))

                    centredPrint(mediumFont, 'Skins', (500, 40))

                    pygame.draw.rect(screen, (255, 0, 0), (30, 550, 100, 30))
                    centredPrint(font, 'Close', (80, 565))
                    if 30 <= mx <= 130 and 550 <= my <= 580:
                        pygame.draw.rect(screen, (128, 128, 128), (30, 550, 100, 30), 5)
                    else:
                        pygame.draw.rect(screen, (0, 0, 0), (30, 550, 100, 30), 3)

                    pygame.draw.rect(screen, (160, 160, 160), (820, 550, 150, 30))
                    centredPrint(font, 'Previous Page', (895, 565))
                    if 820 <= mx <= 970 and 550 <= my <= 580:
                        pygame.draw.rect(screen, (128, 128, 128), (820, 550, 150, 30), 5)
                    else:
                        pygame.draw.rect(screen, (0, 0, 0), (820, 550, 150, 30), 3)

                    centredPrint(tinyFont, 'Enemy Skins', (500, 80))
                    pygame.draw.rect(screen, (160, 160, 160), (50, 100, 900, 100))

                    centredPrint(tinyFont, 'Tower Skins', (500, 225))
                    pygame.draw.rect(screen, (160, 160, 160), (50, 245, 900, 100))

                    deltaX = [-1, -1]
                    for skin in info.skins:
                        skinObj = getSkin(skin)
                        if skinObj is None:
                            print('tower-defense.core: Fatal - There seems to be a removed skin in your inventory and it has been removed!')
                            info.skins.remove(skin)
                            continue

                        if skinObj.skinType == 'Enemy':
                            i = 0
                            y = 105
                        else:
                            i = 1
                            y = 250

                        deltaX[i] += 1

                        pygame.draw.rect(screen, (64, 64, 64), (55 + 100 * deltaX[i], y, 90, 90))
                        if skin in info.skinsEquipped:
                            pygame.draw.rect(screen, (100, 100, 100), (55 + 100 * deltaX[i], y, 90, 90), 3)

                        centredBlit(skinObj.smallImageTexture, (100 + 100 * deltaX[i], y + 45))

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

                                if 820 <= mx <= 970 and 550 <= my <= 580:
                                    info.cosmeticPage = 'runes'
                                    cont = False

                                if 105 <= my <= 195:
                                    index = None
                                    enemySkins = [s for s in info.skins if getSkin(s).skinType == 'Enemy']
                                    for n in range(len(enemySkins)):
                                        if 55 + 100 * n <= mx <= 145 + 100 * n:
                                            index = n

                                    if index is not None:
                                        info.skinsEquipped[0] = enemySkins[index]

                                if 245 <= my <= 335:
                                    index = None
                                    towerSkins = [s for s in info.skins if getSkin(s).skinType == 'Tower']
                                    for n in range(len(towerSkins)):
                                        if 55 + 100 * n <= mx <= 145 + 100 * n:
                                            index = n

                                    if index is not None:
                                        info.skinsEquipped[1] = towerSkins[index]

                    if not cont:
                        break

                    pygame.display.update()

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

                    leftAlignPrint(font, f'{mapName}: {wins} ' + ('win' if wins == 1 else 'wins'), (20, 400 + 30 * numMaps - scroll))

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

        elif info.status == 'achievements':
            highestAchievementTiers = {}
            for achievement, requirement in achievementRequirements.items():
                stat = info.statistics[requirement['attr']]
                highest = 0
                for tier in requirement['tiers']:
                    if stat >= tier:
                        highest += 1
                highestAchievementTiers[achievement] = highest

            scroll = 0
            while True:
                mx, my = pygame.mouse.get_pos()
                screen.fill((200, 200, 200))

                n = 0
                for achievement, information in achievements.items():
                    pygame.draw.rect(screen, (100, 100, 100), (10, 80 + 110 * n - scroll, 980, 100))
                    leftAlignPrint(font, information['names'][min(info.achievements[achievement], 2)], (20, 93 + 110 * n - scroll))

                    leftAlignPrint(tinyFont, information['lore'].replace('[%]', str(achievementRequirements[achievement]['tiers'][min(info.claimedAchievementRewards[achievement], 2)])), (20, 120 + 110 * n - scroll))

                    for m in range(3):
                        if info.claimedAchievementRewards[achievement] > m:
                            pygame.draw.circle(screen, (255, 255, 0), (900 + m * 20, 100 + 110 * n - scroll), 7)
                        pygame.draw.circle(screen, (0, 0, 0), (900 + m * 20, 100 + 110 * n - scroll), 7, 2)

                    if info.claimedAchievementRewards[achievement] < len(achievementRequirements[achievement]['tiers']):
                        current = info.statistics[achievementRequirements[achievement]['attr']]
                        target = achievementRequirements[achievement]['tiers'][info.claimedAchievementRewards[achievement]]
                        percent = min(current / target * 100, 100)

                        pygame.draw.rect(screen, (0, 255, 0), (40, 140 + 110 * n - scroll, percent * 8, 20))

                        txt = f'{round(percent, 1)}%'
                        if 10 <= mx <= 990 and 80 + 110 * n <= my + scroll <= 180 + 110 * n:
                            txt += f' ({current} / {target})'
                        centredPrint(font, txt, (440, 150 + 110 * n - scroll))

                        if highestAchievementTiers[achievement] > info.claimedAchievementRewards[achievement]:
                            pygame.draw.rect(screen, (255, 255, 0), (860, 140 + 110 * n - scroll, 120, 20))
                            if 860 <= mx <= 980 and 140 + 110 * n - scroll <= my <= 160 + 110 * n - scroll:
                                pygame.draw.rect(screen, (128, 128, 128), (860, 140 + 110 * n - scroll, 120, 20), 3)
                            else:
                                pygame.draw.rect(screen, (0, 0, 0), (860, 140 + 110 * n - scroll, 120, 20), 2)
                        else:
                            pygame.draw.rect(screen, (64, 64, 64), (860, 140 + 110 * n - scroll, 120, 20))

                        txt = f'{achievements[achievement]["rewards"][info.claimedAchievementRewards[achievement]]}'
                        txtLength = font.size(txt)[0]
                        centredPrint(font, txt, (915 - txtLength // 2, 150 + 110 * n - scroll))
                        centredBlit(smallTokenImage, (920 + txtLength // 2, 150 + 110 * n - scroll))

                    else:
                        current = info.statistics[achievementRequirements[achievement]['attr']]
                        target = achievementRequirements[achievement]['tiers'][info.claimedAchievementRewards[achievement] - 1]

                        pygame.draw.rect(screen, (0, 255, 0), (40, 140 + 110 * n - scroll, 800, 20))

                        txt = '100.0%'
                        if 10 <= mx <= 990 and 80 + 110 * n <= my + scroll <= 180 + 110 * n:
                            txt += f' ({current} / {target})'
                        centredPrint(font, txt, (440, 150 + 110 * n - scroll))

                    pygame.draw.rect(screen, (0, 0, 0), (40, 140 + 110 * n - scroll, 800, 20), 3)

                    n += 1

                pygame.draw.rect(screen, (200, 200, 200), (0, 0, 1000, 70))
                centredPrint(mediumFont, 'Achievements', (500, 40))

                pygame.draw.rect(screen, (200, 200, 200), (0, 520, 1000, 80))

                pygame.draw.rect(screen, (255, 0, 0), (20, 550, 100, 30))
                centredPrint(font, 'Close', (70, 565))
                if 20 <= mx <= 120 and 550 <= my <= 580:
                    pygame.draw.rect(screen, (128, 128, 128), (20, 550, 100, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (20, 550, 100, 30), 3)

                maxScroll = len(achievements) * 110 - 440
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

                            n = 0
                            for achievement in achievements.keys():
                                if highestAchievementTiers[achievement] > info.claimedAchievementRewards[achievement]:
                                    if 860 <= mx <= 980 and 140 + 110 * n - scroll <= my <= 160 + 110 * n - scroll:
                                        info.tokens += achievements[achievement]["rewards"][info.claimedAchievementRewards[achievement]]
                                        info.claimedAchievementRewards[achievement] += 1

                                n += 1

                        elif event.button == 4:
                            scroll = max(0, scroll - 10)

                        elif event.button == 5:
                            scroll = min(maxScroll, scroll + 10)

                if not cont:
                    break

                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_UP]:
                    scroll = max(0, scroll - 2)
                if pressed[pygame.K_DOWN]:
                    scroll = min(scroll + 2, maxScroll)

                pygame.display.update()

                clock.tick(MaxFPS)

        elif info.status == 'game':
            global rainbowShiftCount, rainbowShiftIndex

            mx, my = pygame.mouse.get_pos()

            mouseTrail.append([mx, my])
            if len(mouseTrail) >= 10:
                mouseTrail = mouseTrail[:-10]

            if gameInfo.spawndelay == 0 and len(gameInfo.spawnleft) > 0:
                Enemy(gameInfo.spawnleft[1], 0, gameInfo.spawnleft[1], mapPath=gameInfo.spawnPath, camo=gameInfo.spawnleft[0] in ['1', '3', '5', '7'], regen=gameInfo.spawnleft[0] in ['2', '3', '6', '7'], fortified=gameInfo.spawnleft[0] in ['4', '5', '6', '7'])

                gameInfo.spawnleft = gameInfo.spawnleft[2:]
                gameInfo.spawndelay = 30

                gameInfo.spawnPath = (gameInfo.spawnPath + 1) % len(gameInfo.Map.path)

            else:
                gameInfo.spawndelay -= 1

            if len(gameInfo.enemies) == 0:
                if len(gameInfo.spawnleft) == 0 and gameInfo.ticksSinceNoEnemies == 0:
                    gameInfo.coins += 110 + 40 * math.sqrt(gameInfo.wave)
                    gameInfo.ticksSinceNoEnemies += 1

                if gameInfo.nextWave <= 0:
                    try:
                        gameInfo.spawnleft = waves[gameInfo.wave]
                        gameInfo.ticksSinceNoEnemies = 0

                    except IndexError:
                        info.status = 'win'

                        if not info.sandboxMode:
                            try:
                                info.statistics['wins'][gameInfo.Map.name] += 1
                            except KeyError:
                                info.statistics['wins'][gameInfo.Map.name] = 1
                            finally:
                                info.statistics['totalWins'] += 1

                            for rune in Runes:
                                if rune.roll(info):
                                    info.runes.append(rune.name)
                                    info.newRunes += 1

                        try:
                            nextMap = Maps[[m.name for m in Maps].index(gameInfo.Map.name) + 1].name
                            if info.PBs[nextMap] == LOCKED:
                                info.PBs[nextMap] = None

                        except IndexError:
                            pass

                        if not info.sandboxMode:
                            if info.PBs[gameInfo.Map.name] is None or info.PBs[gameInfo.Map.name] == LOCKED:
                                info.PBs[gameInfo.Map.name] = gameInfo.HP
                            elif info.PBs[gameInfo.Map.name] < gameInfo.HP:
                                info.PBs[gameInfo.Map.name] = gameInfo.HP

                            info.tokens += gameInfo.HP // 2 + 10

                        info.statistics['mapsBeat'] = len([m for m in info.PBs.keys() if type(info.PBs[m]) is int])

                        gameInfo.FinalHP = gameInfo.HP
                        gameInfo.reset()
                        save()

                    else:
                        gameInfo.spawndelay = 20
                        gameInfo.nextWave = 300

                else:
                    if gameInfo.nextWave == 300:
                        gameInfo.wave += 1
                        info.statistics['wavesPlayed'] += 1

                    gameInfo.nextWave -= 1

            clock.tick(MaxFPS)
            gameInfo.coins += income()

            for enemy in gameInfo.enemies:
                enemy.updateRegen()

            draw()
            move()

            if gameInfo.replayRefresh >= ReplayRefreshRate:
                replayTowers = []
                replayEnemies = []
                replayProjectiles = []
                replayPiercingProjectiles = []
                replayEffects = []

                for tower in gameInfo.towers:
                    replayTowers.append([tower.name, tower.x, tower.y, tower.getImageFrame()])

                    if type(tower) is SpikeTower:
                        for spike in tower.spikes.spikes:
                            if spike.visible:
                                replayEffects.append(['circle', (0, 0, 0), (spike.x, spike.y), 2])

                    if type(tower) is Wizard:
                        if tower.lightning.visibleTicks >= 0:
                            if tower.lightning.t1 is not None:
                                replayEffects.append(['line', (191, 0, 255), (tower.x, tower.y), (tower.lightning.t1.x, tower.lightning.t1.y)])
                                if tower.lightning.t2 is not None:
                                    replayEffects.append(['line', (191, 0, 255), (tower.lightning.t1.x, tower.lightning.t1.y), (tower.lightning.t2.x, tower.lightning.t2.y)])
                                    if tower.lightning.t3 is not None:
                                        replayEffects.append(['line', (191, 0, 255), (tower.lightning.t2.x, tower.lightning.t2.y), (tower.lightning.t3.x, tower.lightning.t3.y)])
                                        if tower.lightning.t4 is not None:
                                            replayEffects.append(['line', (191, 0, 255), (tower.lightning.t2.x, tower.lightning.t3.y), (tower.lightning.t4.x, tower.lightning.t4.y)])
                                            if tower.lightning.t5 is not None:
                                                replayEffects.append(['line', (191, 0, 255), (tower.lightning.t2.x, tower.lightning.t4.y), (tower.lightning.t5.x, tower.lightning.t5.y)])

                    if type(tower) is Sniper:
                        if tower.rifleFireTicks > 0:
                            dx = [0, 7, 14, 7, 0, -7, -14, -7][tower.rotation]
                            dy = [14, 7, 0, -7, -14, -7, 0, 7][tower.rotation]

                            replayEffects.append(['circle', (255, 128, 0), (tower.x + dx, tower.y + dy), 3])

                    if type(tower) in [InfernoTower, Elemental]:
                        for render in tower.inferno.renders:
                            replayEffects.append(['line', (255, 69, 0), (render.target.x, render.target.y), (tower.x, tower.y - 12)])

                for enemy in gameInfo.enemies:
                    replayEnemies.append([enemy.camo, enemy.regen, enemy.tier, enemy.x, enemy.y, enemy.HP, enemy.MaxHP])

                for proj in gameInfo.projectiles:
                    replayProjectiles.append([proj.color, proj.x, proj.y])

                for piercingProj in gameInfo.piercingProjectiles:
                    replayPiercingProjectiles.append([piercingProj.x, piercingProj.y])

                for powerUp in PowerUps.objects:
                    if type(powerUp) is PhysicalPowerUp.Spike:
                        replayEffects.append(['circle', (0, 0, 0), (powerUp.x, powerUp.y), 3])

                    if type(powerUp) is PhysicalPowerUp.Lightning:
                        replayEffects.append(['line', (191, 0, 255), (500, -200), (powerUp.x, powerUp.y)])

                toAppend = {
                    'towers': replayTowers,
                    'enemies': replayEnemies,
                    'projectiles': replayProjectiles,
                    'piercingProjectiles': replayPiercingProjectiles,
                    'effects': replayEffects
                }

                info.gameReplayData.append({k: v for k, v in toAppend.items() if v})

                gameInfo.replayRefresh = 0
            else:
                gameInfo.replayRefresh += 1

            if info.equippedRune == 'Rainbow Rune':
                rainbowShiftCount += 1
                if rainbowShiftCount > 1000:
                    rainbowShiftIndex = (rainbowShiftIndex + 1) % 7
                    rainbowShiftCount = 0

                for n in range(len(mouseTrail) - 1):
                    pygame.draw.line(screen, [rainbowColors[rainbowShiftIndex][n] + rainbowShift[rainbowShiftIndex][n] * rainbowShiftCount for n in range(3)], mouseTrail[n], mouseTrail[n + 1], 5)

            pygame.display.update()

            RuneEffects.update(info)
            PowerUps.update(gameInfo)

            if gameInfo.doubleReloadTicks > 0:
                gameInfo.doubleReloadTicks -= 1

            if gameInfo.HP <= 0:
                info.status = 'lose'
                info.statistics['losses'] += 1
                info.gameReplayData.clear()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save()
                    quit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if mx <= 800 and my <= 450:
                            if gameInfo.placing == 'spikes':
                                for n in range(25):
                                    theta = random.randint(1, 360) * math.pi / 180
                                    radius = random.randint(0, 10)
                                    PowerUps.objects.append(PhysicalPowerUp.Spike(mx + radius * math.sin(theta), my + radius * math.cos(theta), PowerUps))
                                gameInfo.placing = ''

                            else:
                                for towerType in Towers.__subclasses__():
                                    if towerType.name == gameInfo.placing:
                                        gameInfo.placing = ''
                                        towerType(mx, my)
                                        info.statistics['towersPlaced'] += 1
                                        gameInfo.towersPlaced += 1

                                found = False
                                for tower in gameInfo.towers:
                                    if abs(tower.x - mx) ** 2 + abs(tower.y - my) ** 2 <= 225:
                                        gameInfo.selected = tower
                                        found = True

                                if not found:
                                    gameInfo.selected = None

                        if 810 <= mx <= 910:
                            n = 0
                            for tower in Towers.__subclasses__():
                                if tower is Elemental:
                                    continue

                                if 40 + n * 80 + gameInfo.shopScroll <= my <= 70 + n * 80 + gameInfo.shopScroll and my <= 450 and gameInfo.coins >= tower.price and gameInfo.placing == '' and (gameInfo.wave >= tower.req or info.sandboxMode):
                                    gameInfo.coins -= tower.price
                                    gameInfo.placing = tower.name
                                    gameInfo.selected = None
                                    if not info.sandboxMode:
                                        info.statistics['coinsSpent'] += tower.price
                                n += 1

                        if mx <= 20 and 450 <= my <= 470:
                            gameInfo.reset()
                            info.status = 'mapSelect'

                        if 460 <= my <= 510:
                            if 810 <= mx <= 860 and info.powerUps['spikes'] > 0 and gameInfo.placing == '':
                                if not info.sandboxMode:
                                    info.powerUps['spikes'] -= 1

                                gameInfo.placing = 'spikes'

                            if 875 <= mx <= 925 and info.powerUps['lightning'] > 0:
                                t1 = getTarget(Towers(0, 0, overrideAddToTowers=True), overrideRange=1000, ignoreBosses=True)
                                if t1 is not None:
                                    t2 = getTarget(Towers(0, 0, overrideAddToTowers=True), ignore=[t1], overrideRange=1000, ignoreBosses=True)
                                    t1.kill(spawnNew=False, ignoreRegularEnemyHealth=True)
                                    PowerUps.objects.append(PhysicalPowerUp.Lightning(t1.x, t1.y, PowerUps))
                                    if t2 is not None:
                                        t3 = getTarget(Towers(0, 0, overrideAddToTowers=True), ignore=[t1, t2], overrideRange=1000, ignoreBosses=True)
                                        t2.kill(spawnNew=False, ignoreRegularEnemyHealth=True)
                                        PowerUps.objects.append(PhysicalPowerUp.Lightning(t2.x, t2.y, PowerUps))
                                        if t3 is not None:
                                            t4 = getTarget(Towers(0, 0, overrideAddToTowers=True), ignore=[t1, t2, t3], overrideRange=1000, ignoreBosses=True)
                                            t3.kill(spawnNew=False, ignoreRegularEnemyHealth=True)
                                            PowerUps.objects.append(PhysicalPowerUp.Lightning(t3.x, t3.y, PowerUps))
                                            if t4 is not None:
                                                t5 = getTarget(Towers(0, 0, overrideAddToTowers=True), ignore=[t1, t2, t3, t4], overrideRange=1000, ignoreBosses=True)
                                                t4.kill(spawnNew=False, ignoreRegularEnemyHealth=True)
                                                PowerUps.objects.append(PhysicalPowerUp.Lightning(t4.x, t4.y, PowerUps))
                                                if t5 is not None:
                                                    t5.kill(spawnNew=False, ignoreRegularEnemyHealth=True)
                                                    PowerUps.objects.append(PhysicalPowerUp.Lightning(t5.x, t5.y, PowerUps))

                                    if not info.sandboxMode:
                                        info.powerUps['lightning'] -= 1

                            if 940 <= mx <= 990 and info.powerUps['antiCamo'] > 0:
                                found = False
                                for enemy in gameInfo.enemies:
                                    if enemy.camo and enemy.tier not in forceCamo:
                                        enemy.camo = False
                                        found = True

                                if found and not info.sandboxMode:
                                    info.powerUps['antiCamo'] -= 1

                        if 530 <= my <= 580:
                            if 810 <= mx <= 860 and info.powerUps['heal'] > 0:
                                if gameInfo.HP < 250:
                                    gameInfo.HP = min(250, gameInfo.HP + 5)

                                    if not info.sandboxMode:
                                        info.powerUps['heal'] -= 1

                            if 875 <= mx <= 925 and info.powerUps['freeze'] > 0:
                                if len(gameInfo.enemies) > 0:
                                    for enemy in gameInfo.enemies:
                                        enemy.freezeTimer = max(500, enemy.freezeTimer)

                                    if not info.sandboxMode:
                                        info.powerUps['freeze'] -= 1

                            if 940 <= mx <= 990 and info.powerUps['reload'] > 0:
                                if len(gameInfo.towers) > 0:
                                    gameInfo.doubleReloadTicks = 1000

                                    if not info.sandboxMode:
                                        info.powerUps['reload'] -= 1

                        if issubclass(type(gameInfo.selected), Towers):
                            if 295 <= mx <= 595 and 485 <= my <= 570:
                                if gameInfo.selected.upgrades[0] == gameInfo.selected.upgrades[1] == gameInfo.selected.upgrades[2] == 3:
                                    if gameInfo.selected.upgrades[3]:
                                        if gameInfo.selected.abilityCooldown >= gameInfo.selected.totalAbilityCooldown:
                                            gameInfo.selected.abilityCooldown = 0
                                            gameInfo.selected.abilityData['active'] = True

                                    elif type(gameInfo.selected) is Village:
                                        price = 0
                                        sacrifice = []
                                        for tower in gameInfo.towers:
                                            if tower == gameInfo.selected:
                                                continue

                                            if type(tower) is Elemental:
                                                continue

                                            if abs(tower.x - gameInfo.selected.x) ** 2 + abs(tower.y - gameInfo.selected.y) ** 2 <= gameInfo.selected.range ** 2:
                                                price += getSellPrice(tower, pricePercent=100)
                                                sacrifice.append(tower)

                                            if price >= 10000:
                                                break

                                        if price >= 10000:
                                            cost = Village.upgradePrices[3]
                                            if gameInfo.coins >= cost:
                                                gameInfo.coins -= cost
                                                if not info.sandboxMode:
                                                    info.statistics['coinsSpent'] += cost

                                                for tower in sacrifice:
                                                    gameInfo.towers.remove(tower)
                                                gameInfo.towers.remove(gameInfo.selected)

                                                elemental = Elemental(gameInfo.selected.x, gameInfo.selected.y)
                                                elemental.hits = sum([t.hits for t in sacrifice])
                                                gameInfo.towersPlaced += 1

                                                gameInfo.selected = elemental

                                    else:
                                        cost = type(gameInfo.selected).upgradePrices[3]
                                        if gameInfo.coins >= cost:
                                            gameInfo.coins -= cost
                                            if not info.sandboxMode:
                                                info.statistics['coinsSpent'] += cost
                                            gameInfo.selected.upgrades[3] = True

                                elif type(gameInfo.selected) is not Elemental:
                                    n = (my - 485) // 30
                                    if gameInfo.selected.upgrades[n] < 3:
                                        cost = type(gameInfo.selected).upgradePrices[n][gameInfo.selected.upgrades[n]]
                                        if gameInfo.coins >= cost and (gameInfo.wave >= gameInfo.selected.req or info.sandboxMode):
                                            gameInfo.coins -= cost
                                            if not info.sandboxMode:
                                                info.statistics['coinsSpent'] += cost
                                            gameInfo.selected.upgrades[n] += 1

                            if 620 <= mx < 770 and 545 <= my <= 570:
                                gameInfo.towers.remove(gameInfo.selected)
                                gameInfo.coins += getSellPrice(gameInfo.selected)
                                info.statistics['towersSold'] += 1
                                gameInfo.selected = None

                            if type(gameInfo.selected) is IceTower:
                                if 620 <= mx <= 770 and 485 <= my <= 510:
                                    gameInfo.selected.enabled = not gameInfo.selected.enabled

                            if type(gameInfo.selected) not in [Bowler, InfernoTower]:
                                if 620 <= mx <= 770 and 515 <= my <= 540:
                                    if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                                        gameInfo.selected.targeting = targetingCycle[(targetingCycle.index(gameInfo.selected.targeting) - 1) % len(targetingCycle)]
                                    else:
                                        gameInfo.selected.targeting = targetingCycle[(targetingCycle.index(gameInfo.selected.targeting) + 1) % len(targetingCycle)]

                    elif event.button == 4:
                        if mx > 800 and my < 450:
                            gameInfo.shopScroll = min(0, gameInfo.shopScroll + 10)
                        pygame.display.update()

                    elif event.button == 5:
                        if mx > 800 and my < 450:
                            maxScroll = len([tower for tower in Towers.__subclasses__() if (gameInfo.wave >= tower.req or info.sandboxMode) and not tower is Elemental]) * 80 - 450
                            if maxScroll > 0:
                                gameInfo.shopScroll = max(-maxScroll, gameInfo.shopScroll - 10)
                        pygame.display.update()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if gameInfo.placing == 'spikes':
                            if not info.sandboxMode:
                                info.powerUps['spikes'] += 1
                        else:
                            try:
                                price = {t.name: t.price for t in Towers.__subclasses__()}[gameInfo.placing]
                                gameInfo.coins += price
                                if not info.sandboxMode:
                                    info.statistics['coinsSpent'] -= price
                            except KeyError:
                                pass

                        gameInfo.placing = ''

            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_UP]:
                gameInfo.shopScroll = min(0, gameInfo.shopScroll + 5)
            if pressed[pygame.K_DOWN]:
                maxScroll = len([tower for tower in Towers.__subclasses__() if (gameInfo.wave >= tower.req or info.sandboxMode) and tower is not Elemental]) * 80 - 450
                if maxScroll > 0:
                    gameInfo.shopScroll = max(-maxScroll, gameInfo.shopScroll - 5)

            gameInfo.ticks += 1

powerUps = {
    'lightning': [pygame.image.load(os.path.join(resource_path, 'lightning_power_up.png')), pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'lightning_power_up.png')), (60, 60)), 'Lightning Power Up'],
    'spikes': [pygame.image.load(os.path.join(resource_path, 'spikes_power_up.png')), pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'spikes_power_up.png')), (60, 60)), 'Spikes Power Up'],
    'antiCamo': [pygame.image.load(os.path.join(resource_path, 'anti_camo_power_up.png')), pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'anti_camo_power_up.png')), (60, 60)), 'Anti-Camo Power Up'],
    'heal': [pygame.image.load(os.path.join(resource_path, 'heal_power_up.png')), pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'heal_power_up.png')), (60, 60)), 'Heal Power Up'],
    'freeze': [pygame.image.load(os.path.join(resource_path, 'freeze_power_up.png')), pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'freeze_power_up.png')), (60, 60)), 'Freeze Power Up'],
    'reload': [pygame.image.load(os.path.join(resource_path, 'reload_power_up.png')), pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'reload_power_up.png')), (60, 60)), 'Reload Power Up']
}

IceCircle = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'ice_circle.png')), (75, 75)).copy()
IceCircle.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)

possibleRanges = [0, 30, 50, 100, 125, 130, 150, 160, 165, 175, 180, 200, 250, 400]
rangeImages = []
explosionImages = []
for possibleRange in possibleRanges:
    rangeImage = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'range.png')), (possibleRange * 2, possibleRange * 2))
    alphaRangeImage = rangeImage.copy()
    alphaRangeImage.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
    rangeImages.append(alphaRangeImage)

    explosionImage = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'explosion.png')), (possibleRange * 2, possibleRange * 2))
    alphaExplosionImage = explosionImage.copy()
    alphaExplosionImage.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
    explosionImages.append(alphaExplosionImage)

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

healthImage = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'heart_0.png')), (16, 16))
goldenHealthImage = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'heart_1.png')), (16, 16))
tokenImage = pygame.image.load(os.path.join(resource_path, 'token.png'))
smallTokenImage = pygame.transform.scale(tokenImage, (15, 15))

info = data()
gameInfo = gameData()
PowerUps = PhysicalPowerUp()
RuneEffects = RuneEffect(info)
skinsEquipped = [None, None]

mouseTrail = []
rainbowShiftCount = random.randint(0, 999)
rainbowShiftIndex = random.randint(0, 6)

if __name__ == '__main__':
    app()
    print('tower-defense.core: An unexpected error occured.')
