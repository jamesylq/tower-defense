import pygame


class PhysicalPowerUp:
    class Spike:
        def __init__(self, x, y, parent):
            self.x = x
            self.y = y
            self.parent = parent

        def update(self, gameInfo: list):
            for enemy in gameInfo.enemies:
                if enemy.isBoss:
                    if abs(self.x - enemy.x) ** 2 + abs(self.y - enemy.y) ** 2 <= 484:
                        enemy.kill(bossDamage=25)
                        self.parent.objects.remove(self)
                        break
                else:
                    if abs(self.x - enemy.x) ** 2 + abs(self.y - enemy.y) ** 2 <= 144:
                        enemy.kill()
                        self.parent.objects.remove(self)
                        break

        def draw(self, screen, *, sx: int = 0, sy: int = 0):
            pygame.draw.circle(screen, (0, 0, 0), (self.x + sx, self.y + sy), 3)

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

        def draw(self, screen, *, sx: int = 0, sy: int = 0):
            pygame.draw.line(screen, (191, 0, 255), (500, -200), (self.x + sx, self.y + sy), 3)

    def __init__(self):
        self.objects = []

    def update(self, gameInfo):
        for obj in self.objects:
            if type(obj) is PhysicalPowerUp.Spike:
                obj.update(gameInfo)

            if type(obj) is PhysicalPowerUp.Lightning:
                obj.update()

    def draw(self, screen):
        for obj in self.objects:
            obj.draw(screen)
