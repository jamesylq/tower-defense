import os
import pygame
import pickle
import random
import math

from _pickle import UnpicklingError

current_path = os.path.dirname(__file__)
resource_path = os.path.join(current_path, 'resources')

screen, clock, font, largeFont, smallIceCircle, largeIceCircle, Maps, waves, enemyColors, speed, damages, info = [None] * 12
MaxFPS = 100


class Map:
    def __init__(self, path: list, name: str, backgroundColor: int, pathColor: int):
        self.name = name
        self.path = path
        self.backgroundColor = backgroundColor
        self.pathColor = pathColor


POND = Map([[0, 25], [700, 25], [700, 375], [100, 375], [100, 75], [800, 75]], "Pond", (6, 50, 98), (0, 0, 255))
LAVA_SPIRAL = Map([[300, 225], [575, 225], [575, 325], [125, 325], [125, 125], [675, 125], [675, 425], [25, 425], [25, 0]], "Lava Spiral", (207, 16, 32), (255, 140, 0))
PLAINS = Map([[25, 0], [25, 375], [500, 375], [500, 25], [350, 25], [350, 175], [750, 175], [750, 0]], "Plains", (19, 109, 21), (155, 118, 83))
DESERT = Map([[0, 25], [750, 25], [750, 200], [25, 200], [25, 375], [800, 375]], "Desert", (170, 108, 35), (178, 151, 5))
THE_END = Map([[0, 225], [800, 225]], "The End", (100, 100, 100), (200, 200, 200))
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
    'win': False,
    'lose': False,
    'MapSelect': True,
    'shopScroll': 0,
    'spawnleft': '',
    'spawndelay': 9,
    'Map': None
}


class data:
    def __init__(self):
        self.PBs = {Map.name: None for Map in Maps}
        for attr, default in defaults.items():
            setattr(self, attr, default)

    def reset(self):
        for attr, default in defaults.items():
            if attr in ['PBs', 'FinalHP']:
                continue

            setattr(self, attr, default if type(default) is not list else [])


class Towers:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.timer = 0
        self.upgrades = [False, False, False]


class Turret(Towers):
    name = 'Turret'
    color = (128, 128, 128)
    req = 0
    price = 50
    upgradePrices = [30, 20, 75]
    upgradeNames = ['Longer Range', 'More Bullets', 'Explosive Shots']
    range = 100

    def __init__(self, x: int, y: int):
        super().__init__(x, y)

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

    def attack(self):
        if self.timer >= (25 if self.upgrades[1] else 50):
            try:
                closest = getTarget(self.x, self.y, self.range)
                info.projectiles.append(Projectile(self, self.x, self.y, closest.x, closest.y, explosiveRadius=30 if self.upgrades[2] else 0))
                self.timer = 0
            except AttributeError:
                pass
        else:
            self.timer += 1

    def update(self):
        if self.upgrades[0]:
            self.range = 150


class IceTower(Towers):
    class SnowStormCircle:
        def __init__(self, parent, x, y):
            self.x = x
            self.y = y
            self.parent = parent
            self.freezeDuration = 199 if self.parent.upgrades[2] else 100
            self.visibleTicks = 0

        def draw(self):
            if self.visibleTicks > 0:
                self.visibleTicks -= 1
                screen.blit(largeIceCircle if self.parent.upgrades[0] else smallIceCircle, (self.x - self.parent.range, self.y - self.parent.range))

        def freeze(self):
            self.visibleTicks = 50

            for enemy in info.enemies:
                if abs(enemy.x - self.x) ** 2 + abs(enemy.y - self.y) ** 2 <= self.parent.range ** 2:
                    enemy.freezeTimer = self.freezeDuration

    name = 'Ice Tower'
    color = (32, 32, 200)
    req = 2
    price = 30
    upgradePrices = [15, 25, 35]
    upgradeNames = ['Longer Range', 'Snowstorm Circle', 'Longer Freeze']
    range = 125

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.snowCircle = self.SnowStormCircle(self, self.x, self.y)

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)
        self.snowCircle.draw()

    def attack(self):
        if self.timer >= (500 if self.upgrades[1] else 100):
            if self.upgrades[1]:
                self.snowCircle.freeze()
                self.timer = 0
            else:
                try:
                    closest = getTarget(self.x, self.y, self.range)
                    info.projectiles.append(Projectile(self, self.x, self.y, closest.x, closest.y, freeze=True))
                    self.timer = 0
                except AttributeError:
                    pass
        else:
            self.timer += 1

    def update(self):
        if self.upgrades[0]:
            self.range = 175


class BombTower(Towers):
    name = 'Bomb Tower'
    color = (0, 0, 0)
    req = 4
    price = 100
    upgradePrices = [30, 20, 75]
    upgradeNames = ['Longer Range', 'More Bombs', 'Larger Explosions']
    range = 50

    def __init__(self, x: int, y: int):
        super().__init__(x, y)

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

    def attack(self):
        if self.timer >= (125 if self.upgrades[1] else 250):
            try:
                closest = getTarget(self.x, self.y, self.range)
                info.projectiles.append(Projectile(self, self.x, self.y, closest.x, closest.y, explosiveRadius=50))
                self.timer = 0
            except AttributeError:
                pass
        else:
            self.timer += 1

    def update(self):
        if self.upgrades[0]:
            self.range = 100


class BananaFarm(Towers):
    name = 'Banana Farm'
    color = (255, 255, 0)
    req = 4
    price = 150
    upgradePrices = [30, 30, 40]
    upgradeNames = ['Banana Cannon', 'Increased Income', 'Double Coin Drop']
    range = 100

    def __init__(self, x: int, y: int):
        super().__init__(x, y)

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

    def attack(self):
        if self.upgrades[0]:
            if self.timer >= 100:
                try:
                    closest = getTarget(self.x, self.y, self.range)
                    info.projectiles.append(Projectile(self, self.x, self.y, closest.x, closest.y))
                    self.timer = 0
                except AttributeError:
                    pass
            else:
                self.timer += 1

    def update(self):
        pass


class Bowler(Towers):
    name = 'Bowler'
    color = (32, 32, 32)
    req = 5
    price = 175
    upgradePrices = [30, 20, 50]
    upgradeNames = ['Double Damage', 'More Rocks', '10 Enemies Pierce']
    range = 0

    def __init__(self, x: int, y: int):
        super().__init__(x, y)

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

    def attack(self):
        if self.timer >= (200 if self.upgrades[1] else 300):
            try:
                for direction in ['left', 'right', 'up', 'down']:
                    info.piercingProjectiles.append(PiercingProjectile(self, self.x, self.y, 10 if self.upgrades[2] else 3, direction))
                self.timer = 0
            except AttributeError:
                pass
        else:
            self.timer += 1

    def update(self):
        pass


class Wizard(Towers):
    class LightningBolt:
        def __init__(self, parent):
            self.parent = parent
            self.pos0 = [self.parent.x, self.parent.y]
            self.t1 = None
            self.t2 = None
            self.t3 = None
            self.visibleTicks = 0

        def attack(self):
            self.visibleTicks = 50
            self.t1 = getTarget(self.pos0[0], self.pos0[1], 1000)
            if type(self.t1) is Enemy:
                self.t1.kill()
                self.t2 = getTarget(self.t1.x, self.t1.y, 1000, [self.t1])
                if type(self.t2) is Enemy:
                    self.t2.kill()
                    self.t3 = getTarget(self.t2.x, self.t2.y, 1000, [self.t1, self.t2])
                    if type(self.t3) is Enemy:
                        self.t3.kill()
                else:
                    self.t3 = None
            else:
                self.t2 = None
                self.t3 = None

            if self.t1 is None:
                self.parent.lightningTimer = 500
            else:
                self.parent.lightningTimer = 0

        def draw(self):
            if self.visibleTicks > 0:
                self.visibleTicks -= 1

                if self.t1 is not None:
                    pygame.draw.line(screen, (191, 0, 255), self.pos0, [self.t1.x, self.t1.y], 3)
                    if self.t2 is not None:
                        pygame.draw.line(screen, (191, 0, 255), [self.t1.x, self.t1.y], [self.t2.x, self.t2.y], 3)
                        if self.t3 is not None:
                            pygame.draw.line(screen, (191, 0, 255), [self.t2.x, self.t2.y], [self.t3.x, self.t3.y], 3)

    name = 'Wizard'
    color = (128, 0, 128)
    req = 7
    price = 250
    upgradePrices = [30, 75, 50]
    upgradeNames = ['Longer Range', 'Lightning Zap', 'Big Blast Radius']
    range = 125

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.lightning = self.LightningBolt(self)
        self.lightningTimer = 0

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)
        self.lightning.draw()

    def attack(self):
        if self.timer >= (80 if self.upgrades[2] else 160):
            try:
                closest = getTarget(self.x, self.y, self.range)
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
        if self.upgrades[0]:
            self.range = 200


class Projectile:
    def __init__(self, parent: Towers, x: int, y: int, tx: int, ty: int, *, explosiveRadius: int = 0, freeze: bool = False):
        self.parent = parent
        self.x = x
        self.y = y
        self.tx = tx
        self.ty = ty
        self.dx = None
        self.dy = None
        self.explosiveRadius = explosiveRadius
        self.freeze = freeze
        self.coinMultiplier = getCoinMultiplier(parent)
        if self.explosiveRadius > 0:
            self.color = (0, 0, 0)
        elif self.freeze:
            self.color = (0, 0, 187)
        elif self.coinMultiplier > 1:
            self.color = (255, 255, 0)
        else:
            self.color = (187, 187, 187)

    def move(self):
        if self.dx is None:
            try:
                dx = self.tx - self.x
                dy = self.ty - self.y
                self.dx = abs(dx / (dx + dy)) * 5
                self.dy = abs(dy / (dx + dy)) * 5

                if self.tx > self.x:
                    self.dx = -self.dx
                if self.ty > self.y:
                    self.dy = -self.dy

                self.x -= self.dx
                self.y -= self.dy
            except ZeroDivisionError:
                info.projectiles.remove(self)
        else:
            self.x -= self.dx
            self.y -= self.dy

        if self.x < 0 or self.x > 800 or self.y < 0 or self.y > 450:
            info.projectiles.remove(self)

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 3)

    def explode(self, centre):
        for enemy in info.enemies:
            if enemy == centre:
                continue

            if abs(enemy.x - self.x) ** 2 + abs(enemy.y - self.y) ** 2 < self.explosiveRadius ** 2:
                enemy.kill()


class PiercingProjectile:
    def __init__(self, parent: Towers, x: int, y: int, pierceLimit: int, direction: str):
        self.parent = parent
        self.x = x
        self.y = y
        self.pierce = pierceLimit
        self.direction = direction
        self.ignore = []

    def move(self):
        if self.direction == 'left':
            self.x -= 1
        elif self.direction == 'right':
            self.x += 1
        elif self.direction == 'up':
            self.y -= 1
        elif self.direction == 'down':
            self.y += 1

        if self.x < 0 or self.x > 800 or self.y < 0 or self.y > 450:
            info.piercingProjectiles.remove(self)

    def draw(self):
        pygame.draw.circle(screen, (16, 16, 16), (self.x, self.y), 5)


class Enemy:
    def __init__(self, tier: int, spawn: [int, int], lineIndex: int):
        self.tier = tier
        self.x, self.y = spawn
        self.lineIndex = lineIndex
        self.totalMovement = 0
        self.freezeTimer = 0
        self.HP = 1000 if self.tier == 'A' else 1

    def move(self):
        if self.freezeTimer > 0:
            self.freezeTimer -= 1
        else:
            if len(info.Map.path) - 1 == self.lineIndex:
                self.kill(spawnNew=False)
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
                    self.kill(spawnNew=False)

                self.totalMovement += 1

            if type(self.tier) is str:
                self.freezeTimer = 5

    def update(self):
        for projectile in info.projectiles:
            if abs(self.x - projectile.x) ** 2 + abs(self.y - projectile.y) ** 2 < 625 if type(self.tier) is str else 100:
                if projectile.freeze:
                    info.projectiles.remove(projectile)
                    if type(projectile.parent) is IceTower:
                        self.freezeTimer = 99 if projectile.parent.upgrades[2] else 50
                else:
                    info.projectiles.remove(projectile)
                    if projectile.explosiveRadius > 0:
                        projectile.explode(self)
                        if self.tier == 6:
                            self.kill(coinMultiplier=projectile.coinMultiplier)
                    if self.tier != 6:
                        self.kill(coinMultiplier=projectile.coinMultiplier)

        if self.tier not in [6, 'A']:
            for projectile in info.piercingProjectiles:
                if abs(self.x - projectile.x) ** 2 + abs(self.y - projectile.y) ** 2 < 100:
                    if self not in projectile.ignore:
                        new = self.kill()
                        if projectile.parent.upgrades[0] and new is not None:
                            new = new.kill()
                        projectile.ignore.append(new)
                        if projectile.pierce == 1:
                            info.piercingProjectiles.remove(projectile)
                        else:
                            projectile.pierce -= 1

    def draw(self):
        pygame.draw.circle(screen, enemyColors[str(self.tier)], (self.x, self.y), 20 if type(self.tier) is str else 10)

    def kill(self, *, spawnNew: bool = True, coinMultiplier: int = 1, ignoreBoss: bool = False):
        if type(self.tier) is int or ignoreBoss:
            try:
                info.enemies.remove(self)
            except ValueError:
                pass
            if spawnNew:
                if self.tier == 0:
                    info.coins += 2 * coinMultiplier
                elif self.tier == 'A':
                    info.coins += 150
                else:
                    info.coins += 1 * coinMultiplier
                    info.enemies.append(Enemy(self.tier - 1, (self.x, self.y), self.lineIndex))
                    return info.enemies[-1]
        else:
            self.HP -= 1
            if self.HP == 0:
                self.kill(spawnNew=spawnNew, coinMultiplier=coinMultiplier, ignoreBoss=True)


def getSellPrice(tower: Towers) -> float:
    price = tower.price
    for n in range(len(tower.upgrades)):
        if tower.upgrades[n]:
            price += tower.upgradePrices[n]

    return price * 0.5


def centredBlit(font: pygame.font.Font, text: str, color: (int, int, int), pos: (int, int)):
    textObj = font.render(text, True, color)
    screen.blit(textObj, textObj.get_rect(center=pos))


def income() -> float:
    total = 0.001
    for tower in info.towers:
        if type(tower) is BananaFarm:
            total += 0.001
            if tower.upgrades[1]:
                total += 0.003
    return total


def getCoinMultiplier(Tower: Towers) -> int:
    bananaFarms = [tower for tower in info.towers if type(tower) is BananaFarm and tower.upgrades[2]]
    for bananaFarm in bananaFarms:
        if abs(Tower.x - bananaFarm.x) ** 2 + abs(Tower.y - bananaFarm.y) ** 2 < bananaFarm.range ** 2:
            return 2
    return 1


def getTarget(x: int, y: int, radius: int, ignore: [Enemy] = None) -> Enemy:
    currMaxEnemy, currMaxValue = None, 0
    if ignore is None:
        ignore = []

    for enemy in info.enemies:
        if enemy in ignore:
            continue

        if abs(enemy.x - x) ** 2 + abs(enemy.y - y) ** 2 <= radius ** 2:
            if currMaxValue < enemy.totalMovement:
                currMaxEnemy = enemy
                currMaxValue = enemy.totalMovement
    try:
        return currMaxEnemy
    except AttributeError:
        return None


def draw():
    mx, my = pygame.mouse.get_pos()

    screen.fill(info.Map.backgroundColor)

    for i in range(len(info.Map.path) - 1):
        pygame.draw.line(screen, info.Map.pathColor, info.Map.path[i], info.Map.path[i + 1], 10)
    pygame.draw.circle(screen, info.Map.pathColor, info.Map.path[0], 10)

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

    for enemy in info.enemies:
        enemy.draw()

    pygame.draw.rect(screen, (221, 221, 221), (800, 0, 200, 450))

    n = 0
    for towerType in Towers.__subclasses__():
        if info.wave >= towerType.req:
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

    for tower in info.towers:
        tower.draw()

    if info.selected is not None:
        original = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'range.png')), (info.selected.range * 2, info.selected.range * 2))
        modified = original.copy()
        modified.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
        screen.blit(modified, (info.selected.x - info.selected.range, info.selected.y - info.selected.range))

    for projectile in info.projectiles:
        projectile.draw()

    for projectile in info.piercingProjectiles:
        projectile.draw()

    if issubclass(type(info.selected), Towers):
        screen.blit(font.render('Upgrades:', True, 0), (200, 475))

        for n in range(3):
            if info.selected.upgrades[n]:
                pygame.draw.rect(screen, (255, 255, 191), (295, 485 + 30 * n, 300, 30))
            pygame.draw.rect(screen, (128, 128, 128), (295, 485 + 30 * n, 300, 30), 5)

            nameWithSpace = ''
            for m in range(18):
                nameWithSpace += info.selected.upgradeNames[n][m] if m < len(info.selected.upgradeNames[n]) else ' '

            screen.blit(font.render(f'{nameWithSpace} [${info.selected.upgradePrices[n]}]', True, (32, 32, 32)), (300, 485 + n * 30))

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
        if info.spawnleft[0] == 'A':
            info.enemies.append(Enemy(info.spawnleft[0], info.Map.path[0], 0))
        else:
            info.enemies.append(Enemy(int(info.spawnleft[0]), info.Map.path[0], 0))
        info.spawnleft = info.spawnleft[1:]
        info.spawndelay = 15
    else:
        info.spawndelay -= 1

    if len(info.enemies) == 0:
        if info.nextWave <= 0:
            try:
                info.spawnleft = waves[info.wave]
            except IndexError:
                info.win = True
            info.spawndelay = 15
            info.nextWave = 300
        else:
            if info.nextWave == 300:
                info.coins += 100
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
                        if 40 + n * 80 + info.shopScroll <= my <= 70 + n * 80 + info.shopScroll <= 450 and info.coins >= tower.price and info.placing == '' and info.wave >= tower.req:
                            info.coins -= tower.price
                            info.placing = tower.name
                            info.selected = None
                        n += 1

                if 775 <= mx <= 975 and 500 <= my <= 530:
                    info.reset()

                if issubclass(type(info.selected), Towers):
                    if 295 <= mx <= 595 and 485 <= my <= 570:
                        n = (my - 485) // 30
                        cost = type(info.selected).upgradePrices[n]
                        if info.coins >= cost and info.wave >= info.selected.req and not info.selected.upgrades[n]:
                            info.coins -= cost
                            info.selected.upgrades[n] = True
                    elif 620 <= mx < 820 and 545 <= my < 570:
                        info.towers.remove(info.selected)
                        info.coins += getSellPrice(info.selected)
                        info.selected = None

            elif event.button == 4:
                if mx > 800 and my < 450:
                    info.shopScroll = min(0, info.shopScroll + 10)

            elif event.button == 5:
                if mx > 800 and my < 450:
                    maxScroll = len([tower for tower in Towers.__subclasses__() if info.wave >= tower.req]) * 80 - 450
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
                print(f'Updated Savefile: Added attribute {attr}')

        for Map in Maps:
            if Map.name not in info.PBs.keys():
                info.PBs[Map.name] = None
                print(f'Updated Savefile: Added map {Map.name}')
    except FileNotFoundError:
        open('save.txt', 'w')
    except (EOFError, ValueError, UnpicklingError):
        pass


def app():
    global screen, clock, font, largeFont, smallIceCircle, largeIceCircle, Maps, waves, enemyColors, speed, damages, info, defaults

    screen = pygame.display.set_mode((1000, 600))
    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Ubuntu Mono', 20)
    largeFont = pygame.font.SysFont('Ubuntu Mono', 75)
    pygame.display.set_caption('Tower Defense')

    IceCircle = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'ice_circle.png')), (250, 250))
    smallIceCircle = IceCircle.copy()
    smallIceCircle.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)

    IceCircle = pygame.transform.scale(pygame.image.load(os.path.join(resource_path, 'ice_circle.png')), (350, 350))
    largeIceCircle = IceCircle.copy()
    largeIceCircle.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)

    Maps = [POND, LAVA_SPIRAL, PLAINS, DESERT, THE_END]
    waves = [
        'A',
        '000',
        '11100000',
        '11111222000',
        '1111100022222333',
        '333333333333333333333',
        '22222222222222222222222223333333333333333333333333',
        '444444444444444444444',
        '5555555555555555555554444444444',
        '666666666666666666666',
        'A'
    ]
    enemyColors = {
        '0': (255, 0, 0),
        '1': (0, 0, 221),
        '2': (0, 255, 0),
        '3': (255, 255, 0),
        '4': (255, 20, 147),
        '5': (68, 68, 68),
        '6': (16, 16, 16),
        'A': (146, 43, 62)
    }

    damages = {
        '0': 1,
        '1': 2,
        '2': 3,
        '3': 4,
        '4': 5,
        '5': 6,
        '6': 8,
        'A': 25
    }

    speed = {
        '0': 1,
        '1': 1,
        '2': 2,
        '3': 2,
        '4': 3,
        '5': 4,
        '6': 2,
        'A': 1
    }

    info = data()

    load()
    while True:
        mx, my = pygame.mouse.get_pos()

        if info.MapSelect:
            screen.fill((68, 68, 68))

            screen.blit(font.render('Map Select', True, (255, 255, 255)), (450, 25))
            pygame.draw.rect(screen, (200, 200, 200), (850, 550, 125, 30))
            screen.blit(font.render('Random Map', True, (0, 0, 0)), (860, 555))
            if 850 <= mx <= 975 and 550 < my <= 580:
                pygame.draw.rect(screen, (128, 128, 128), (850, 550, 125, 30), 5)
            else:
                pygame.draw.rect(screen, (0, 0, 0), (850, 550, 125, 30), 3)

            for n in range(len(Maps)):
                pygame.draw.rect(screen, Maps[n].backgroundColor, (10, 40 * n + 60, 980, 30))
                if 10 <= mx <= 980 and 40 * n + 60 < my <= 40 * n + 90:
                    pygame.draw.rect(screen, (128, 128, 128), (10, 40 * n + 60, 980, 30), 5)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (10, 40 * n + 60, 980, 30), 3)
                screen.blit(font.render(Maps[n].name.upper(), True, (0, 0, 0)), (20, 62 + n * 40))
                screen.blit(font.render(f'(Best: {info.PBs[Maps[n].name]})', True, (225, 255, 0) if info.PBs[Maps[n].name] == 100 else (0, 0, 0)), (800, 62 + n * 40))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if 10 <= mx <= 980:
                            for n in range(len(Maps)):
                                if 40 * n + 60 <= my <= 40 * n + 90:
                                    info.Map = Maps[n]
                                    info.MapSelect = False
                        if 850 <= mx <= 975 and 550 <= my <= 580:
                            info.Map = random.choice(Maps)
                            info.MapSelect = False
        else:
            if info.win:
                cont = False
                if info.PBs[info.Map.name] is None:
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


if __name__ == '__main__':
    app()
