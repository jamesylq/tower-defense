import pygame
import maps
import pickle
import math

from _pickle import UnpicklingError


screen = pygame.display.set_mode((1000, 600))
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()
font = pygame.font.SysFont('Ubuntu Mono', 20)
largeFont = pygame.font.SysFont('Ubuntu Mono', 75)
pygame.display.set_caption('Tower Defense')

IceCircle = pygame.transform.scale(pygame.image.load('Resources/Ice Circle.png'), (250, 250))
smallIceCircle = IceCircle.copy()
smallIceCircle.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)

IceCircle = pygame.transform.scale(pygame.image.load('Resources/Ice Circle.png'), (350, 350))
largeIceCircle = IceCircle.copy()
largeIceCircle.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)

Maps = [maps.PLAINS, maps.POND, maps.LAVA_SPIRAL, maps.DESERT]
Map = None
waves = [
    '000',
    '11100000',
    '11111222000',
    '1111100022222333',
    '333333333333333333333',
    '22222222222222222222222223333333333333333333333333',
    '444444444444444444444',
    '5555555555555555555554444444444',
    '666666666666666666666'
]
enemyColors = [(255, 0, 0), (0, 0, 221), (0, 255, 0), (255, 255, 0), (255, 20, 147), (68, 68, 68), (16, 16, 16)]
damages = [1, 2, 3, 4, 5, 6, 8]
speed = [1, 1, 2, 2, 3, 4, 2]

enemies = []
projectiles = []
piercingProjectiles = []
towers = []
PBs = {}
HP = 100
FinalHP = None
coins = 50
selected = None
placing = ''
nextWave = 299
wave = 0
win = False
MapSelect = True
shopScroll = 0


class Towers:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.timer = 0
        self.upgrades = [False, False, False]


class Turret(Towers):
    name = 'Turret'
    color = (128, 128, 128)
    req = 1
    price = 50
    upgradePrices = [30, 20, 75]

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.range = 100

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

    def attack(self):
        if self.timer >= (25 if self.upgrades[1] else 50):
            try:
                closest = getTarget(self.x, self.y, self.range)
                projectiles.append(Projectile(self, self.x, self.y, closest.x, closest.y, explosiveRadius=30 if self.upgrades[2] else 0))
                self.timer = 0
            except AttributeError:
                pass
        else:
            self.timer += 1

    def update(self):
        if self.upgrades[0]:
            self.range = 150

    def GUIUpgrades(self):
        for n in range(3):
            if self.upgrades[n]:
                pygame.draw.rect(screen, (255, 255, 191), (295, 485 + 30 * n, 300, 30))
            pygame.draw.rect(screen, (128, 128, 128), (295, 485 + 30 * n, 300, 30), 5)
        screen.blit(font.render('Upgrades:', True, 0), (200, 475))
        screen.blit(font.render(f'Longer Range      [${self.upgradePrices[0]}]', True, (32, 32, 32)), (300, 485))
        screen.blit(font.render(f'More Bullets      [${self.upgradePrices[1]}]', True, (32, 32, 32)), (300, 515))
        screen.blit(font.render(f'Explosive Shots   [${self.upgradePrices[2]}]', True, (32, 32, 32)), (300, 545))


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

            for enemy in enemies:
                if abs(enemy.x - self.x) ** 2 + abs(enemy.y - self.y) ** 2 <= self.parent.range ** 2:
                    enemy.freezeTimer = self.freezeDuration

    name = 'Ice Tower'
    color = (32, 32, 200)
    req = 2
    price = 30
    upgradePrices = [15, 25, 35]

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.range = 125
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
                    projectiles.append(Projectile(self, self.x, self.y, closest.x, closest.y, freeze=True))
                    self.timer = 0
                except AttributeError:
                    pass
        else:
            self.timer += 1

    def update(self):
        if self.upgrades[0]:
            self.range = 175

    def GUIUpgrades(self):
        for n in range(3):
            if self.upgrades[n]:
                pygame.draw.rect(screen, (255, 255, 191), (295, 485 + 30 * n, 300, 30))
            pygame.draw.rect(screen, (128, 128, 128), (295, 485 + 30 * n, 300, 30), 5)
        screen.blit(font.render('Upgrades:', True, 0), (200, 475))
        screen.blit(font.render(f'Longer Range      [${self.upgradePrices[0]}]', True, (32, 32, 32)), (300, 485))
        screen.blit(font.render(f'Snowstorm Circle  [${self.upgradePrices[1]}]', True, (32, 32, 32)), (300, 515))
        screen.blit(font.render(f'Longer Freeze     [${self.upgradePrices[2]}]', True, (32, 32, 32)), (300, 545))


class BombTower(Towers):
    name = 'Bomb Tower'
    color = (0, 0, 0)
    req = 4
    price = 100
    upgradePrices = [30, 20, 75]

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.range = 50

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

    def attack(self):
        if self.timer >= (125 if self.upgrades[1] else 250):
            try:
                closest = getTarget(self.x, self.y, self.range)
                projectiles.append(Projectile(self, self.x, self.y, closest.x, closest.y, explosiveRadius=50))
                self.timer = 0
            except AttributeError:
                pass
        else:
            self.timer += 1

    def update(self):
        if self.upgrades[0]:
            self.range = 100

    def GUIUpgrades(self):
        for n in range(3):
            if self.upgrades[n]:
                pygame.draw.rect(screen, (255, 255, 191), (295, 485 + 30 * n, 300, 30))
            pygame.draw.rect(screen, (128, 128, 128), (295, 485 + 30 * n, 300, 30), 5)
        screen.blit(font.render('Upgrades:', True, 0), (200, 475))
        screen.blit(font.render(f'Longer Range      [${self.upgradePrices[0]}]', True, (32, 32, 32)), (300, 485))
        screen.blit(font.render(f'More Bombs        [${self.upgradePrices[1]}]', True, (32, 32, 32)), (300, 515))
        screen.blit(font.render(f'Bigger Explosions [${self.upgradePrices[2]}]', True, (32, 32, 32)), (300, 545))


class BananaFarm(Towers):
    name = 'Banana Farm'
    color = (55, 255, 0)
    req = 4
    price = 150
    upgradePrices = [30, 30, 40]

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.range = 100

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

    def attack(self):
        if self.upgrades[0]:
            if self.timer >= 100:
                try:
                    closest = getTarget(self.x, self.y, self.range)
                    projectiles.append(Projectile(self, self.x, self.y, closest.x, closest.y))
                    self.timer = 0
                except AttributeError:
                    pass
            else:
                self.timer += 1

    def update(self):
        pass

    def GUIUpgrades(self):
        for n in range(3):
            if self.upgrades[n]:
                pygame.draw.rect(screen, (255, 255, 191), (295, 485 + 30 * n, 300, 30))
            pygame.draw.rect(screen, (128, 128, 128), (295, 485 + 30 * n, 300, 30), 5)
        screen.blit(font.render('Upgrades:', True, 0), (200, 475))
        screen.blit(font.render(f'Banana Cannon     [${self.upgradePrices[0]}]', True, (32, 32, 32)), (300, 485))
        screen.blit(font.render(f'Increased Income  [${self.upgradePrices[1]}]', True, (32, 32, 32)), (300, 515))
        screen.blit(font.render(f'Double Coin Drop  [${self.upgradePrices[2]}]', True, (32, 32, 32)), (300, 545))


class Bowler(Towers):
    name = 'Bowler'
    color = (32, 32, 32)
    req = 5
    price = 175
    upgradePrices = [30, 20, 50]

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.range = 0

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

    def attack(self):
        if self.timer >= (200 if self.upgrades[1] else 300):
            try:
                for direction in ['left', 'right', 'up', 'down']:
                    piercingProjectiles.append(PiercingProjectile(self, self.x, self.y, 10 if self.upgrades[2] else 3, direction))
                self.timer = 0
            except AttributeError:
                pass
        else:
            self.timer += 1

    def update(self):
        pass

    def GUIUpgrades(self):
        for n in range(3):
            if self.upgrades[n]:
                pygame.draw.rect(screen, (255, 255, 191), (295, 485 + 30 * n, 300, 30))
            pygame.draw.rect(screen, (128, 128, 128), (295, 485 + 30 * n, 300, 30), 5)
        screen.blit(font.render('Upgrades:', True, 0), (200, 475))
        screen.blit(font.render(f'Double Damage     [${self.upgradePrices[0]}]', True, (32, 32, 32)), (300, 485))
        screen.blit(font.render(f'More Rocks        [${self.upgradePrices[1]}]', True, (32, 32, 32)), (300, 515))
        screen.blit(font.render(f'10 Enemies Pierce [${self.upgradePrices[2]}]', True, (32, 32, 32)), (300, 545))


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
    color = (255, 255, 0)
    req = 7
    price = 250
    upgradePrices = [30, 75, 50]

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.range = 125
        self.lightning = self.LightningBolt(self)
        self.lightningTimer = 0

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)
        self.lightning.draw()

    def attack(self):
        if self.timer >= (80 if self.upgrades[2] else 160):
            try:
                closest = getTarget(self.x, self.y, self.range)
                projectiles.append(Projectile(self, self.x, self.y, closest.x, closest.y, explosiveRadius=60 if self.upgrades[2] else 30))
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

    def GUIUpgrades(self):
        for n in range(3):
            if self.upgrades[n]:
                pygame.draw.rect(screen, (255, 255, 191), (295, 485 + 30 * n, 300, 30))
            pygame.draw.rect(screen, (128, 128, 128), (295, 485 + 30 * n, 300, 30), 5)
        screen.blit(font.render('Upgrades:', True, 0), (200, 475))
        screen.blit(font.render(f'Longer Range      [${self.upgradePrices[0]}]', True, (32, 32, 32)), (300, 485))
        screen.blit(font.render(f'Lightning Zap     [${self.upgradePrices[1]}]', True, (32, 32, 32)), (300, 515))
        screen.blit(font.render(f'Big Blast Radius  [${self.upgradePrices[2]}]', True, (32, 32, 32)), (300, 545))


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
                projectiles.remove(self)
        else:
            self.x -= self.dx
            self.y -= self.dy

        if self.x < 0 or self.x > 800 or self.y < 0 or self.y > 450:
            projectiles.remove(self)

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 3)

    def explode(self, centre):
        for enemy in enemies:
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
            piercingProjectiles.remove(self)

    def draw(self):
        pygame.draw.circle(screen, (16, 16, 16), (self.x, self.y), 5)


class Enemy:
    def __init__(self, tier: int, spawn: [int, int], lineIndex: int):
        self.tier = tier
        self.x, self.y = spawn
        self.lineIndex = lineIndex
        self.delete = False
        self.totalMovement = 0
        self.freezeTimer = 0

    def move(self):
        global HP

        if self.freezeTimer > 0:
            self.freezeTimer -= 1
        else:
            if len(Map.path) - 1 == self.lineIndex:
                self.kill(False)
                HP -= damages[self.tier]
                updateEnemies()
            else:
                current = Map.path[self.lineIndex]
                new = Map.path[self.lineIndex + 1]

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
                    self.kill(False)
                    updateEnemies()

                self.totalMovement += 1

    def update(self):
        global HP

        for projectile in projectiles:
            if abs(self.x - projectile.x) ** 2 + abs(self.y - projectile.y) ** 2 < 100:
                if projectile.freeze:
                    projectiles.remove(projectile)
                    if type(projectile.parent) is IceTower:
                        self.freezeTimer = 99 if projectile.parent.upgrades[2] else 50
                else:
                    projectiles.remove(projectile)
                    if projectile.explosiveRadius > 0:
                        projectile.explode(self)
                        if self.tier == 6:
                            self.kill()
                    if self.tier != 6:
                        self.kill()

        if self.tier != 6:
            for projectile in piercingProjectiles:
                if abs(self.x - projectile.x) ** 2 + abs(self.y - projectile.y) ** 2 < 100:
                    if self not in projectile.ignore:
                        new = self.kill()
                        if projectile.parent.upgrades[0] and new is not None:
                            new = new.kill()
                        projectile.ignore.append(new)
                        if projectile.pierce == 1:
                            piercingProjectiles.remove(projectile)
                        else:
                            projectile.pierce -= 1

    def draw(self):
        pygame.draw.circle(screen, enemyColors[self.tier], (self.x, self.y), 10)

    def kill(self, coinMultiplier: int = 1, spawnNew: bool = True):
        global enemies, coins

        self.delete = True
        if self.tier == 0:
            coins += 2 * coinMultiplier
        else:
            coins += 1 * coinMultiplier
            if spawnNew:
                enemies.append(Enemy(self.tier - 1, (self.x, self.y), self.lineIndex))
                return enemies[-1]


def income() -> float:
    total = 0.001
    for tower in towers:
        if type(tower) is BananaFarm and tower.upgrades[1]:
            total += 0.001
    return total


def getCoinMultiplier(Tower: Towers) -> int:
    bananaFarms = [tower for tower in towers if type(tower) is BananaFarm and tower.upgrades[2]]
    for bananaFarm in bananaFarms:
        if abs(Tower.x - bananaFarm.x) ** 2 + abs(Tower.y - bananaFarm.y) ** 2 < bananaFarm.range ** 2:
            return 2
    return 1


def getTarget(x: int, y: int, radius: int, ignore: [Enemy] = None) -> Enemy:
    currMaxEnemy, currMaxValue = None, 0
    if ignore is None:
        ignore = []

    for enemy in enemies:
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
    screen.fill(Map.backgroundColor)

    for i in range(len(Map.path) - 1):
        pygame.draw.line(screen, Map.pathColor, Map.path[i], Map.path[i + 1], 10)
    pygame.draw.circle(screen, Map.pathColor, Map.path[0], 10)

    pygame.draw.rect(screen, (221, 221, 221), (800, 0, 200, 450))

    n = 0
    for towerType in Towers.__subclasses__():
        if wave + 1 >= towerType.req:
            screen.blit(font.render(f'{towerType.name} (${towerType.price})', True, 0), (810, 10 + 80 * n + shopScroll))
            pygame.draw.rect(screen, (187, 187, 187), (945, 30 + 80 * n + shopScroll, 42, 42))
            pygame.draw.circle(screen, towerType.color, (966, 51 + 80 * n + shopScroll), 15)
            pygame.draw.line(screen, 0, (800, 80 + 80 * n + shopScroll), (1000, 80 + 80 * n + shopScroll), 3)
            pygame.draw.line(screen, 0, (800, 80 * n + shopScroll), (1000, 80 * n + shopScroll), 3)
            pygame.draw.rect(screen, (136, 136, 136), (810, 40 + 80 * n + shopScroll, 100, 30))
            screen.blit(font.render('Buy New', True, 0), (820, 42 + 80 * n + shopScroll))
        n += 1

    pygame.draw.rect(screen, (170, 170, 170), (0, 450, 1000, 150))

    screen.blit(font.render(f'Health: {HP} HP', True, 0), (10, 545))
    screen.blit(font.render(f'Coins: {math.floor(coins)}', True, 0), (10, 570))
    screen.blit(font.render(f'Wave {wave + 1}', True, 0), (900, 570))

    pygame.draw.rect(screen, (128, 128, 128), (775, 500, 200, 30))
    screen.blit(font.render('Map Selection', True, (0, 0, 0)), (800, 505))

    for tower in towers:
        tower.draw()

    if selected is not None:
        original = pygame.transform.scale(pygame.image.load('Resources/Range.png'), (selected.range * 2, selected.range * 2))
        modified = original.copy()
        modified.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
        screen.blit(modified, (selected.x - selected.range, selected.y - selected.range))

    for enemy in enemies:
        enemy.draw()

    for projectile in projectiles:
        projectile.draw()

    for projectile in piercingProjectiles:
        projectile.draw()

    if issubclass(type(selected), Towers):
        selected.GUIUpgrades()

    if placing != '':
        screen.blit(font.render(f'Click anywhere on the map to place the {placing}!', True, 0), (275, 480))

    pygame.display.update()


def move():
    for enemy in enemies:
        for i in range(speed[enemy.tier]):
            enemy.update()
            enemy.move()
            enemy.update()

    updateEnemies()

    for tower in towers:
        tower.update()
        tower.attack()

    for projectile in projectiles:
        projectile.move()

    for projectile in piercingProjectiles:
        projectile.move()


def spawn(wave: int):
    for char in waves[wave]:
        enemies.append(Enemy(int(char), Map.path[0], 0))

        for n in range(18):
            main()


def updateEnemies():
    global enemies

    enemies = [enemy for enemy in enemies if not enemy.delete]


def main():
    global coins, selected, clickOffset, wave, nextWave, placing, win, enemies, towers, shopScroll

    if len(enemies) == 0:
        if nextWave <= 0:
            try:
                spawn(wave)
            except IndexError:
                win = True
            nextWave = 300
        else:
            if nextWave == 300:
                coins += 100
                wave += 1
                if wave == len(waves):
                    win = True
            nextWave -= 1

    mx, my = pygame.mouse.get_pos()

    clock.tick(100)
    coins += income()

    draw()
    move()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if mx <= 800 and my <= 450:
                    for towerType in Towers.__subclasses__():
                        if towerType.name == placing:
                            placing = ''
                            towers.append(towerType(mx, my))
                            return

                    for tower in towers:
                        if abs(tower.x - mx) ** 2 + abs(tower.y - my) ** 2 <= 225:
                            selected = tower
                            clickOffset = [mx - tower.x, my - tower.y]
                            return
                    selected = None

                if 810 <= mx <= 910:
                    n = 0
                    for tower in Towers.__subclasses__():
                        if 40 + n * 80 + shopScroll <= my <= 70 + n * 80 + shopScroll <= 450 and coins >= tower.price and placing == '':
                            coins -= tower.price
                            placing = tower.name
                            selected = None
                        n += 1

                if 775 <= mx <= 975 and 500 <= my <= 530:
                    global projectiles, piercingProjectiles, HP, MapSelect

                    enemies = []
                    projectiles = []
                    piercingProjectiles = []
                    towers = []
                    HP = 100
                    coins = 50
                    selected = None
                    placing = ''
                    nextWave = 299
                    wave = 0
                    win = False
                    MapSelect = True

                if 295 <= mx <= 595 and 485 <= my <= 570:
                    if issubclass(type(selected), Towers):
                        n = (my - 485) // 30
                        cost = type(selected).upgradePrices[n]
                        if coins >= cost and wave + 1 >= selected.req and not selected.upgrades[n]:
                            coins -= cost
                            selected.upgrades[n] = True
            elif event.button == 4:
                if mx > 800 and my < 450:
                    shopScroll = min(0, shopScroll + 10)
            elif event.button == 5:
                if mx > 800 and my < 450:
                    maxScroll = len([tower for tower in Towers.__subclasses__() if wave + 1 >= tower.req]) * 80 - 450
                    if maxScroll > 0:
                        shopScroll = max(-maxScroll, shopScroll - 10)

    save()


def save():
    pickle.dump([enemies, projectiles, piercingProjectiles, towers, HP, coins, placing, nextWave, wave, MapSelect, Map, PBs, win], open('save.txt', 'wb'))


def load():
    global enemies, projectiles, piercingProjectiles, towers, HP, coins, placing, nextWave, wave, MapSelect, Map, PBs, win

    try:
        enemies, projectiles, piercingProjectiles, towers, HP, coins, placing, nextWave, wave, MapSelect, Map, PBs, win = pickle.load(open('save.txt', 'rb'))
    except FileNotFoundError:
        open('save.txt', 'w')
    except (EOFError, ValueError, UnpicklingError):
        pass

    for m in Maps:
        if m.name not in PBs.keys():
            PBs[m.name] = None


load()
while True:
    mx, my = pygame.mouse.get_pos()

    if MapSelect:
        screen.fill((68, 68, 68))

        screen.blit(font.render('Map Select', True, (255, 255, 255)), (450, 25))

        for n in range(len(Maps)):
            pygame.draw.rect(screen, Maps[n].backgroundColor, (10, 40 * n + 60, 980, 30))
            if 10 <= mx <= 980 and 40 * n + 60 < my <= 40 * n + 90:
                pygame.draw.rect(screen, (128, 128, 128), (10, 40 * n + 60, 980, 30), 5)
            else:
                pygame.draw.rect(screen, (0, 0, 0), (10, 40 * n + 60, 980, 30), 3)
            screen.blit(font.render(Maps[n].name.upper(), True, (0, 0, 0)), (20, 62 + n * 40))
            screen.blit(font.render(f'(Best: {PBs[Maps[n].name]})', True, (225, 255, 0) if PBs[Maps[n].name] == 100 else (0, 0, 0)), (800, 62 + n * 40))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if 10 <= mx <= 980:
                        for n in range(len(Maps)):
                            if 40 * n + 60 <= my <= 40 * n + 90:
                                Map = Maps[n]
                                MapSelect = False
    else:
        if not win:
            main()
        else:
            cont = False
            save()
            if PBs[Map.name] is None:
                PBs[Map.name] = HP
            elif PBs[Map.name] < HP:
                PBs[Map.name] = HP
            FinalHP = HP
            enemies = []
            projectiles = []
            piercingProjectiles = []
            towers = []
            HP = 100
            coins = 50
            selected = None
            clickOffset = []
            placing = ''
            nextWave = 299
            wave = 0
            win = False
            MapSelect = True

            while True:
                screen.fill((32, 32, 32))
                screen.blit(largeFont.render(f'You Win!', True, (255, 255, 255)), (320, 100))
                screen.blit(font.render(f'Your Final Score: {FinalHP}', True, (255, 255, 255)), (350, 300))
                screen.blit(font.render(f'Press [SPACE] to continue!', True, (255, 255, 255)), (325, 350))
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            cont = True
                    elif event.type == pygame.QUIT:
                        quit()

                clock.tick(60)
                if cont:
                    break
