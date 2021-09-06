import os
import math
import pygame
import random

from typing import *

curr_path = os.path.dirname(__file__)
resource_path = os.path.join(curr_path, 'resources')


class Skin:
    def __init__(self, name: str, icon: str, skins: Dict[List[str], list], price: int, size: Tuple[int, int] = None):
        self.name = name
        self.skins = {}
        for k, v in skins.items():
            textures = []
            for i in range(8):
                texture = pygame.image.load(os.path.join(resource_path, v[0]))
                scaledTexture = pygame.transform.scale(texture, v[1])
                rotatedTexture = pygame.transform.rotate(scaledTexture, i * 45)
                textures.append(rotatedTexture)
            self.skins[k] = textures
        self.price = price

        self.imageTexture = pygame.image.load(os.path.join(resource_path, icon))
        if size is not None:
            self.imageTexture = pygame.transform.scale(self.imageTexture, size)

        width, height = self.imageTexture.get_size()
        self.imageTexture = pygame.transform.scale(self.imageTexture, (width, height))

        width, height = self.imageTexture.get_size()
        if width > height:
            self.smallImageTexture = pygame.transform.scale(self.imageTexture, (85, math.ceil(85 * height / width)))
        elif height > width:
            self.smallImageTexture = pygame.transform.scale(self.imageTexture, (math.ceil(85 * width / height), 85))
        else:
            self.smallImageTexture = pygame.transform.scale(self.imageTexture, (85, 85))

    def roll(self) -> bool:
        return random.randint(1, 100) <= self.chance


def getSkin(skinName: str):
    for skin in skins:
        if skin.name == skinName:
            return skin


def getNotUnlockedSkin(info):
    notUnlocked = [skin for skin in skins if skin.name not in info.skins]
    if notUnlocked:
        return random.choice(notUnlocked)


skins = [
    Skin('BTD6 MOAB Class Skin', 'MOAB.png', {
        ('Enemy', 'A'): ['MOAB.png', (89, 57)],
        ('Enemy', 'B'): ['BFB.png', (140, 99)],
        ('Enemy', 'C'): ['DDT.png', (109, 75)],
        ('Enemy', 'D'): ['BAD.png', (175, 127)]
    }, 2499, (115, 75))
]
