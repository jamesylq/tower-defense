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

Map = maps.PLAINS
rounds = [
    '000',
    '11100000',
    '11111222000',
    '1111100022222333',
    '333333333333333333333',
    '22222222222222222222222223333333333333333333333333',
    '444444444444444444444'
]
colors = [0xFF0000, 0x0000DD, 0x00FF00, 0xFFFF00, 0xFF1493]
damages = [1, 2, 3, 4, 5]
speed = [1, 1, 2, 3, 5]

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
    def __init__(self, name: str, x: int, y: int):
        self.name = name
        self.x = x
        self.y = y
        self.timer = 0
        self.upgrades = [False, False, False]


class Turret(Towers):
    color = (128, 128, 128)

    def __init__(self, x: int, y: int):
        super().__init__('Turret', x, y)
        self.range = 100

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

    def attack(self):
        if self.timer >= (25 if self.upgrades[1] else 50):
            try:
                tx, ty = getTarget(self.x, self.y, self.range)
                projectiles.append(Projectile(self, self.x, self.y, tx, ty, explosiveRadius=30 if self.upgrades[2] else 0))
                self.timer = 0
            except TypeError:
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
    color = (32, 32, 200)

    def __init__(self, x: int, y: int):
        super().__init__('Ice Tower', x, y)
        self.range = 125

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

    def attack(self):
        if self.timer >= (100 if self.upgrades[1] else 200):
            try:
                tx, ty = getTarget(self.x, self.y, self.range)
                projectiles.append(Projectile(self, self.x, self.y, tx, ty, freeze=True))
                self.timer = 0
            except TypeError:
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
    color = 0

    def __init__(self, x: int, y: int):
        super().__init__('Bomb Tower', x, y)
        self.range = 50

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

    def attack(self):
        if self.timer >= (125 if self.upgrades[1] else 250):
            try:
                tx, ty = getTarget(self.x, self.y, self.range)
                projectiles.append(Projectile(self, self.x, self.y, tx, ty, explosiveRadius=50))
                self.timer = 0
            except TypeError:
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
            self.x -= 1
        elif self.line[0][0] < self.line[1][0]:
            self.x += 1
        elif self.line[0][1] > self.line[1][1]:
            self.y -= 1
        else:
            self.y += 1
        self.totalMovement += 1

    def update(self):
        global HP

        for projectile in projectiles:
            if abs(self.x - projectile.x) ** 2 + abs(self.y - projectile.y) ** 2 < 100:
                if projectile.freeze:
                    projectiles.remove(projectile)
                    self.freezeTimer = 99 if projectile.parent.upgrades[2] else 50
                    return
                else:
                    projectiles.remove(projectile)
                    if projectile.explosiveRadius > 0:
                        projectile.explode(self)
                    self.kill()
                    return

        if [self.x, self.y] == self.line[1]:
            try:
                self.line[0] = self.line[1]
                self.line[1] = Map.path[Map.path.index(self.line[1]) + 1]
            except IndexError:
                HP -= damages[self.tier]
                self.kill(False)

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


def getTarget(x: int, y: int, radius: int) -> [int, int]:
    currMaxEnemy, currMaxValue = None, 0
    for enemy in enemies:
        if abs(enemy.x - x) ** 2 + abs(enemy.y - y) ** 2 <= radius ** 2:
            if currMaxValue < enemy.totalMovement:
                currMaxEnemy = enemy
                currMaxValue = enemy.totalMovement
    try:
        return [currMaxEnemy.x, currMaxEnemy.y]
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
        screen.blit(largeFont.render('You win!', True, (255, 255, 0)), (100, 150))
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

        screen.blit(font.render('Turret ($50)', True, 0), (810, 10))
        pygame.draw.rect(screen, 0xBBBBBB, (945, 30, 42, 42))
        pygame.draw.circle(screen, Turret.color, (966, 51), 15)
        pygame.draw.line(screen, 0, (800, 80), (1000, 80), 3)
        pygame.draw.rect(screen, 0x888888, (810, 40, 100, 30))
        screen.blit(font.render('Buy New', True, 0), (820, 42))

        if wave >= 1:
            screen.blit(font.render('Ice Tower ($30)', True, 0), (810, 90))
            pygame.draw.rect(screen, 0xBBBBBB, (945, 110, 42, 42))
            pygame.draw.circle(screen, IceTower.color, (966, 131), 15)
            pygame.draw.line(screen, 0, (800, 160), (1000, 160), 3)
            pygame.draw.rect(screen, 0x888888, (810, 120, 100, 30))
            screen.blit(font.render('Buy New', True, 0), (820, 122))
        if wave >= 3:
            screen.blit(font.render('Bomb Tower ($100)', True, 0), (810, 170))
            pygame.draw.rect(screen, 0xBBBBBB, (945, 190, 42, 42))
            pygame.draw.circle(screen, BombTower.color, (966, 211), 15)
            pygame.draw.line(screen, 0, (800, 240), (1000, 240), 3)
            pygame.draw.rect(screen, 0x888888, (810, 200, 100, 30))
            screen.blit(font.render('Buy New', True, 0), (820, 202))

        if issubclass(type(selected), Towers):
            selected.GUIUpgrades()

        if placing != '':
            screen.blit(font.render(f'Click anywhere on the map to place the {placing}!', True, 0), (275, 480))

    pygame.display.update()


def move():
    global enemies

    nextIter = []

    for enemy in enemies:
        for i in range(speed[enemy.tier]):
            enemy.update()
            enemy.move()
            enemy.update()

        if not enemy.delete:
            nextIter.append(enemy)

    for tower in towers:
        tower.update()
        tower.attack()

    for projectile in projectiles:
        projectile.move()

    enemies = nextIter


def spawn(wave: int):
    global win

    try:
        for char in rounds[wave]:
            enemies.append(Enemy(int(char), Map.path[0], [Map.path[0], Map.path[1]]))

            for n in range(18):
                main()
    except IndexError:
        win = True


def main():
    global coins, selected, clickOffset, wave, nextWave, placing

    if len(enemies) == 0:
        if nextWave <= 0:
            spawn(wave)
            nextWave = 300
        else:
            if nextWave == 300:
                coins += 100
                wave += 1
            nextWave -= 0.5 if pygame.key.get_pressed()[pygame.K_SPACE] else 1

    mx, my = pygame.mouse.get_pos()

    clock.tick(120 if pygame.key.get_pressed()[pygame.K_SPACE] else 60)
    draw()
    move()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if mx <= 800 and my <= 450:
                    if placing == 'Turret':
                        placing = ''
                        towers.append(Turret(mx, my))
                    elif placing == 'Ice Tower':
                        placing = ''
                        towers.append(IceTower(mx, my))
                    elif placing == 'Bomb Tower':
                        placing = ''
                        towers.append(BombTower(mx, my))
                    else:
                        for tower in towers:
                            if abs(tower.x - mx) ** 2 + abs(tower.y - my) ** 2 <= 225:
                                selected = tower
                                clickOffset = [mx - tower.x, my - tower.y]
                                return
                        selected = None

                if 810 <= mx <= 910:
                    if 40 <= my <= 70:
                        if coins >= 50:
                            coins -= 50
                            placing = 'Turret'
                            selected = None

                    elif 120 <= my <= 150:
                        if coins >= 30:
                            coins -= 30
                            placing = 'Ice Tower'
                            selected = None

                    elif 200 <= my <= 230:
                        if coins >= 100:
                            coins -= 100
                            placing = 'Bomb Tower'
                            selected = None

                elif 295 <= mx <= 595 and 485 <= my <= 570:
                    n = (my - 485) // 30
                    if type(selected) is Turret:
                        if n == 0:
                            if coins >= 30 and not selected.upgrades[0]:
                                coins -= 30
                                selected.upgrades[0] = True
                            return
                        elif n == 1:
                            if coins >= 20 and not selected.upgrades[1]:
                                coins -= 20
                                selected.upgrades[1] = True
                            return
                        elif n == 2:
                            if coins >= 75 and not selected.upgrades[2]:
                                coins -= 75
                                selected.upgrades[2] = True
                            return
                    elif type(selected) is IceTower:
                        if n == 0:
                            if coins >= 20 and not selected.upgrades[0]:
                                coins -= 20
                                selected.upgrades[0] = True
                            return
                        elif n == 1:
                            if coins >= 15 and not selected.upgrades[1]:
                                coins -= 15
                                selected.upgrades[1] = True
                            return
                        elif n == 2:
                            if coins >= 35 and not selected.upgrades[2]:
                                coins -= 35
                                selected.upgrades[2] = True
                            return
                    elif type(selected) is BombTower:
                        if n == 0:
                            if coins >= 30 and not selected.upgrades[0]:
                                coins -= 30
                                selected.upgrades[0] = True
                            return
                        elif n == 1:
                            if coins >= 20 and not selected.upgrades[1]:
                                coins -= 20
                                selected.upgrades[1] = True
                            return
                        elif n == 2:
                            if coins >= 75 and not selected.upgrades[2]:
                                coins -= 75
                                selected.upgrades[2] = True
                            return


while True:
    if not win:
        main()
    else:
        if pygame.event.get(pygame.QUIT):
            quit()

        clock.tick(60)
        draw()
