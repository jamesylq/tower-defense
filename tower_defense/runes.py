import os
import pygame
import random

from typing import *

from tower_defense.constants import *


curr_path = os.path.dirname(__file__)
resource_path = os.path.join(curr_path, 'resources')

explosionImages = [pygame.image.load(os.path.join(resource_path, f'explosion-{p}.png')) for p in range(3)]


class Rune:
    def __init__(self, name: str, dropChance: float, lore: str, shopPrice: int = 0, imageName: str = 'rune.png'):
        self.name = name
        self.dropChance = dropChance
        self.shopPrice = shopPrice
        self.lore = lore

        try:
            self.imageTexture = pygame.image.load(os.path.join(resource_path, imageName))
        except FileNotFoundError:
            self.imageTexture = pygame.image.load(os.path.join(resource_path, 'rune.png'))

        if self.imageTexture.get_size() != (99, 99):
            self.imageTexture = pygame.transform.scale(self.imageTexture, (99, 99))

        self.smallImageTexture = pygame.transform.scale(self.imageTexture, (66, 66))

    def roll(self, info) -> bool:
        if random.randint(1, 100) <= self.dropChance and self.name not in info.runes:
            return True
        return False

    def draw(self, screen, x: int, y: int, size: int = 99):
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

        def draw(self, screen):
            pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), 2)

    class IceRuneEffect:
        def __init__(self, x: int, y: int):
            self.x = x
            self.y = y
            self.visibleTicks = 50

        def draw(self, screen):
            pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y), 2)

    class GoldRuneEffect:
        def __init__(self, x: int, y: int):
            self.x = x
            self.y = y
            self.visibleTicks = 50

        def draw(self, screen):
            pygame.draw.circle(screen, (255, 255, 0), (self.x, self.y), 2)

    class LightningRuneEffect:
        def __init__(self, x: int, y: int):
            self.x = x
            self.y = y
            self.visibleTicks = 50

        def draw(self, screen):
            pygame.draw.line(screen, (191, 0, 255), (self.x, self.y), (500, -200), 3)

    class ShrinkRuneEffect:
        def __init__(self, x: int, y: int, radius: int, color: Tuple[int], camo: bool, regen: bool):
            self.x = x
            self.y = y
            self.radius = radius
            self.color = color
            self.visibleTicks = 50
            self.camo = camo
            self.regen = regen

        def draw(self, screen):
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius * self.visibleTicks // 50)
            color = None
            if self.camo and self.regen:
                color = (187, 11, 255)
            elif self.camo:
                color = (0, 0, 0)
            elif self.regen:
                color = (255, 105, 180)

            if color is not None:
                pygame.draw.circle(screen, color, (self.x, self.y), self.radius * self.visibleTicks // 50, 2)

    class LeapRuneEffect:
        def __init__(self, x: int, y: int, radius: int, color: Tuple[int], camo: bool, regen: bool):
            self.x = x
            self.y = y
            self.radius = radius
            self.color = color
            self.visibleTicks = 50
            self.camo = camo
            self.regen = regen

        def draw(self, screen):
            pygame.draw.circle(screen, self.color, (self.x, self.y - 600 + 12 * self.visibleTicks), self.radius)
            color = None
            if self.camo and self.regen:
                color = (187, 11, 255)
            elif self.camo:
                color = (0, 0, 0)
            elif self.regen:
                color = (255, 105, 180)

            if color is not None:
                pygame.draw.circle(screen, color, (self.x, self.y - 600 + 12 * self.visibleTicks), self.radius, 2)

    class ExplosionRuneEffect:
        def __init__(self, x: int, y: int):
            self.x = x
            self.y = y
            self.visibleTicks = 15

        def draw(self, screen):
            frame = explosionImages[(15 - self.visibleTicks) // 5]
            screen.blit(frame, frame.get_rect(center=[self.x, self.y]))

    def __init__(self, info):
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
            self.effects.append(self.ShrinkRuneEffect(target.x, target.y, 25 if target.isBoss else 12, enemyColors[str(target.tier)] if color is None else color, target.camo, target.regen))

        elif self.rune == 'Leap Rune':
            self.effects.append(self.LeapRuneEffect(target.x, target.y, 25 if target.isBoss else 12, enemyColors[str(target.tier)] if color is None else color, target.camo, target.regen))

        elif self.rune == 'Explosion Rune':
            self.effects.append(self.ExplosionRuneEffect(target.x, target.y))

    def draw(self, screen):
        for effect in self.effects:
            effect.draw(screen)
            effect.visibleTicks -= 1

            if effect.visibleTicks == 0:
                self.effects.remove(effect)

    def update(self, info):
        self.rune = info.equippedRune


Runes = [
    Rune('null', 0, 'A glitched rune. How did you get this?'),
    Rune('Blood Rune', 15, 'The rune forged by the Blood Gods.', 100, 'blood_rune.png'),
    Rune('Ice Rune', 12, 'A rune as cold as ice.', 100, 'ice_rune.png'),
    Rune('Gold Rune', 8, 'The rune of the wealthy - Classy!', 100, 'gold_rune.png'),
    Rune('Leap Rune', 8, 'Jump!', 150, 'leap_rune.png'),
    Rune('Lightning Rune', 5, 'Legends say it was created by Zeus himself.', 150, 'lightning_rune.png'),
    Rune('Explosion Rune', 5, 'BOOM!', 150, 'explosion_rune.png'),
    Rune('Shrink Rune', 3, 'This magical rune compresses its foes!', 175, 'shrink_rune.png'),
    Rune('Rainbow Rune', 2, 'A rainbow tail forms behind your cursor!', 200, 'rainbow_rune.png')
]
