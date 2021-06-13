import pygame
import maps
import math
import random


screen = pygame.display.set_mode((1000, 600))
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()
font = pygame.font.SysFont('Ubuntu Mono', 20)
largeFont = pygame.font.SysFont('Ubuntu Mono', 200)
pygame.display.set_caption('Tower Defense')

Map = maps.DESERT
waves = [
    '000',
    '11100000',
    '11111222000',
    '1111100022222333',
    '333333333333333333333',
    '22222222222222222222222223333333333333333333333333',
    '444444444444444444444',
    '5555555555555555555554444444444'
]
colors = [0xFF0000, 0x0000DD, 0x00FF00, 0xFFFF00, 0xFF1493, 0x444444]
damages = [1, 2, 3, 4, 5, 6]
speed = [1, 1, 2, 3, 5, 7]

enemies = []
projectiles = []
towers = []
HP = 100
coins = 50
selected = None
clickOffset = []
placing = ''
nextWave = 299
wave = 0
win = False


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
                pygame.draw.rect(screen, 0xffffbf, (295, 485 + 30 * n, 300, 30))
            pygame.draw.rect(screen, (128, 128, 128), (295, 485 + 30 * n, 300, 30), 5)
        screen.blit(font.render('Upgrades:', True, 0), (200, 475))
        screen.blit(font.render('Longer Range      [$30]', True, (32, 32, 32)), (300, 485))
        screen.blit(font.render('More Bullets      [$20]', True, (32, 32, 32)), (300, 515))
        screen.blit(font.render('Explosive Shots   [$75]', True, (32, 32, 32)), (300, 545))


class IceTower(Towers):
    name = 'Ice Tower'
    color = (32, 32, 200)
    req = 2
    price = 30

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.range = 125

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

    def attack(self):
        if self.timer >= (100 if self.upgrades[1] else 200):
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
                pygame.draw.rect(screen, 0xffffbf, (295, 485 + 30 * n, 300, 30))
            pygame.draw.rect(screen, (128, 128, 128), (295, 485 + 30 * n, 300, 30), 5)
        screen.blit(font.render('Upgrades:', True, 0), (200, 475))
        screen.blit(font.render('Longer Range      [$20]', True, (32, 32, 32)), (300, 485))
        screen.blit(font.render('More Bullets      [$15]', True, (32, 32, 32)), (300, 515))
        screen.blit(font.render('Longer Freeze     [$35]', True, (32, 32, 32)), (300, 545))


class BombTower(Towers):
    name = 'Bomb Tower'
    color = 0
    req = 4
    price = 100

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
                pygame.draw.rect(screen, 0xffffbf, (295, 485 + 30 * n, 300, 30))
            pygame.draw.rect(screen, (128, 128, 128), (295, 485 + 30 * n, 300, 30), 5)
        screen.blit(font.render('Upgrades:', True, 0), (200, 475))
        screen.blit(font.render('Longer Range      [$30]', True, (32, 32, 32)), (300, 485))
        screen.blit(font.render('More Bombs        [$20]', True, (32, 32, 32)), (300, 515))
        screen.blit(font.render('Bigger Explosions [$75]', True, (32, 32, 32)), (300, 545))


class Wizard(Towers):
    name = 'Wizard'
    color = (255, 255, 0)
    req = 6
    price = 250

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.range = 125
        self.lightning = [0, None, None, None]
        self.lightningTimer = 0

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

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
            self.lightningTimer = 0
            self.lightning = [50, getTarget(self.x, self.y, 1000)]
            if type(self.lightning[1]) is Enemy:
                self.lightning.append(getTarget(self.lightning[1].x, self.lightning[1].y, 1000, [self.lightning[1]]))
                if type(self.lightning[2]) is Enemy:
                    self.lightning.append(getTarget(self.lightning[2].x, self.lightning[2].y, 1000, [self.lightning[1], self.lightning[2]]))

            for n in range(3):
                try:
                    self.lightning[n + 1].kill()
                except (AttributeError, IndexError):
                    if n == 0:
                        self.lightningTimer = 50
                    return
        elif self.upgrades[1]:
            self.lightningTimer += 1

    def update(self):
        if self.upgrades[0]:
            self.range = 200

    def GUIUpgrades(self):
        for n in range(3):
            if self.upgrades[n]:
                pygame.draw.rect(screen, 0xffffbf, (295, 485 + 30 * n, 300, 30))
            pygame.draw.rect(screen, (128, 128, 128), (295, 485 + 30 * n, 300, 30), 5)
        screen.blit(font.render('Upgrades:', True, 0), (200, 475))
        screen.blit(font.render('Longer Range      [$50]', True, (32, 32, 32)), (300, 485))
        screen.blit(font.render('Lightning Zap     [$75]', True, (32, 32, 32)), (300, 515))
        screen.blit(font.render('Big Blast Radius  [$100]', True, (32, 32, 32)), (300, 545))


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
        if self.explosiveRadius > 0:
            self.color = 0
        elif self.freeze:
            self.color = 0x0000BB
        else:
            self.color = 0xBBBBBB

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

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 3)

    def explode(self, centre):
        for enemy in enemies:
            if enemy == centre:
                continue

            if abs(enemy.x - self.x) ** 2 + abs(enemy.y - self.y) ** 2 < self.explosiveRadius ** 2:
                enemy.kill()


class Enemy:
    def __init__(self, tier: int, spawn: [int, int], line: [[int, int], [int, int]]):
        self.tier = tier
        self.x, self.y = spawn
        self.line = line
        self.delete = False
        self.totalMovement = 0
        self.freezeTimer = 0

    def move(self):
        if self.freezeTimer > 0:
            self.freezeTimer -= 1
            return

        if self.line[0][0] > self.line[1][0]:
            self.x = max(self.x - 1, self.line[1][0])
        elif self.line[0][0] < self.line[1][0]:
            self.x = min(self.x + 1, self.line[1][0])
        elif self.line[0][1] > self.line[1][1]:
            self.y = max(self.y - 1, self.line[1][1])
        elif self.line[0][1] < self.line[1][1]:
            self.y = min(self.y + 1, self.line[1][1])
        else:
            return

        self.totalMovement += 1

    def update(self):
        global HP

        for projectile in projectiles:
            if abs(self.x - projectile.x) ** 2 + abs(self.y - projectile.y) ** 2 < 100:
                if projectile.freeze:
                    projectiles.remove(projectile)
                    self.freezeTimer = 99 if projectile.parent.upgrades[2] else 50
                else:
                    projectiles.remove(projectile)
                    if projectile.explosiveRadius > 0:
                        projectile.explode(self)
                    self.kill()

        if [self.x, self.y] == self.line[1]:
            try:
                self.line[0] = self.line[1]
                self.line[1] = Map.path[Map.path.index(self.line[1]) + 1]
            except IndexError:
                self.kill(False)
                HP -= damages[self.tier]
                updateEnemies()

    def draw(self):
        pygame.draw.circle(screen, colors[self.tier], (self.x, self.y), 10)

    def kill(self, spawnNew: bool = True):
        global enemies, coins

        self.delete = True
        if self.tier == 0:
            coins += 3
        else:
            coins += 1
            if spawnNew:
                enemies.append(Enemy(self.tier - 1, (self.x, self.y), self.line))


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

    pygame.draw.rect(screen, 0xAAAAAA, (0, 450, 1000, 150))

    screen.blit(font.render(f'Health: {HP} HP', True, 0), (10, 545))
    screen.blit(font.render(f'Coins: {coins}', True, 0), (10, 570))
    screen.blit(font.render(f'Wave {wave + 1}', True, 0), (900, 570))

    for tower in towers:
        tower.draw()

    if win:
        screen.blit(largeFont.render('You win!', True, 0), (100, 150))
    else:
        if selected is not None:
            original = pygame.transform.scale(pygame.image.load('Resources/Range.png'), (selected.range * 2, selected.range * 2))
            modified = original.copy()
            modified.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
            screen.blit(modified, (selected.x - selected.range, selected.y - selected.range))

        for enemy in enemies:
            enemy.draw()

        for projectile in projectiles:
            projectile.draw()

        pygame.draw.rect(screen, 0xDDDDDD, (800, 0, 200, 450))

        n = 0
        for towerType in Towers.__subclasses__():
            if wave + 1 >= towerType.req:
                screen.blit(font.render(f'{towerType.name} (${towerType.price})', True, 0), (810, 10 + 80 * n))
                pygame.draw.rect(screen, 0xBBBBBB, (945, 30 + 80 * n, 42, 42))
                pygame.draw.circle(screen, towerType.color, (966, 51 + 80 * n), 15)
                pygame.draw.line(screen, 0, (800, 80 + 80 * n), (1000, 80 + 80 * n), 3)
                pygame.draw.rect(screen, 0x888888, (810, 40 + 80 * n, 100, 30))
                screen.blit(font.render('Buy New', True, 0), (820, 42 + 80 * n))
            n += 1

        for wizard in [tower for tower in towers if type(tower) is Wizard]:
            if wizard.lightning[0] > 0:
                wizard.lightning[0] -= 1
                try:
                    pygame.draw.line(screen, (191, 0, 255), [wizard.x, wizard.y], [wizard.lightning[1].x, wizard.lightning[1].y], 3)
                    pygame.draw.line(screen, (191, 0, 255), [wizard.lightning[1].x, wizard.lightning[1].y], [wizard.lightning[2].x, wizard.lightning[2].y], 3)
                    pygame.draw.line(screen, (191, 0, 255), [wizard.lightning[2].x, wizard.lightning[2].y], [wizard.lightning[3].x, wizard.lightning[3].y], 3)
                except AttributeError:
                    pass

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


def spawn(wave: int):
    for char in waves[wave]:
        enemies.append(Enemy(int(char), Map.path[0], [Map.path[0], Map.path[1]]))

        for n in range(18):
            main()


def updateEnemies():
    global enemies

    enemies = [enemy for enemy in enemies if not enemy.delete]


def main():
    global coins, selected, clickOffset, wave, nextWave, placing, win

    if len(enemies) == 0:
        if nextWave <= 0:
            spawn(wave)
            nextWave = 300
        else:
            if nextWave == 300:
                coins += 100
                wave += 1
                if wave == len(waves):
                    win = True
            nextWave -= 0.5 if pygame.key.get_pressed()[pygame.K_SPACE] else 1

    mx, my = pygame.mouse.get_pos()

    clock.tick(300 if pygame.key.get_pressed()[pygame.K_SPACE] else 60)
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
                    prices = {
                        'Turret': 50,
                        'Ice Tower': 30,
                        'Bomb Tower': 100,
                        'Wizard': 250
                    }

                    n = 0
                    for tower, cost in prices.items():
                        if 40 + n * 80 <= my <= 70 + n * 80 and coins >= cost:
                            coins -= cost
                            placing = tower
                            selected = None
                        n += 1

                elif 295 <= mx <= 595 and 485 <= my <= 570:
                    upgrades = {
                        Turret: [30, 20, 75],
                        IceTower: [20, 15, 35],
                        BombTower: [30, 20, 75],
                        Wizard: [50, 75, 100]
                    }

                    if issubclass(type(selected), Towers):
                        n = (my - 485) // 30
                        cost = upgrades[type(selected)][n]
                        if coins >= cost and wave + 1 >= selected.req and not selected.upgrades[n]:
                            coins -= cost
                            selected.upgrades[n] = True


while True:
    if not win:
        main()
    else:
        if pygame.event.get(pygame.QUIT):
            quit()

        clock.tick(60)
        draw()
