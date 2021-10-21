import os
import math
import pytz
import pygame
import random
import datetime

from typing import *

curr_path = os.path.dirname(__file__)
resource_path = os.path.join(curr_path, 'resources')


class Skin:
    def __init__(self, name: str, icon: str, skins: Dict[List[str], list], price: int, skinType: str, *, iconSize: Tuple[int, int] = None):
        self.name = name

        self.skins = {}
        for k, v in skins.items():
            if k[0] == 'Enemy':
                textures = []
                for i in range(8):
                    texture = pygame.image.load(os.path.join(resource_path, 'skins', v[0]))
                    scaledTexture = pygame.transform.scale(texture, v[1])
                    rotatedTexture = pygame.transform.rotate(scaledTexture, i * 45)
                    textures.append(rotatedTexture)

                self.skins[k] = textures

            if k[0] == 'Tower':
                if type(v) is list:
                    textures = []
                    for s in v:
                        textures.append(pygame.image.load(os.path.join(resource_path, 'skins', s)))

                    self.skins[k] = textures

                else:
                    self.skins[k] = pygame.image.load(os.path.join(resource_path, 'skins', v))

        self.price = price
        self.skinType = skinType

        self.imageTexture = pygame.image.load(os.path.join(resource_path, 'skins', icon))
        if iconSize is not None:
            self.imageTexture = pygame.transform.scale(self.imageTexture, iconSize)

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
    for skin in Skins:
        if skin.name == skinName:
            return skin


def getNotUnlockedSkin(info):
    now = datetime.datetime.now(tz=pytz.timezone('Singapore'))
    notUnlocked = []
    for skin in Skins:
        if skin.name not in info.skins:
            if skin.name in specialSkins.keys():
                obtainableDates = specialSkins[skin.name]
                if obtainableDates[0][0] <= now.year <= obtainableDates[1][0] and obtainableDates[0][1] <= now.month <= obtainableDates[1][1] and obtainableDates[0][2] <= now.day <= obtainableDates[1][2]:
                    notUnlocked.append(skin)

            else:
                notUnlocked.append(skin)

    if notUnlocked:
        return random.choice(notUnlocked)


def loadSkin(skinName: str, towers: list) -> dict:
    skinObj = getSkin(skinName)
    if skinObj is None:
        return

    towerImages = {}
    for towerType in towers:
        if towerType.name in ['Turret', 'Sniper']:
            frames = []
            for n in range(4):
                frames.append(pygame.transform.rotate(skinObj.skins[('Tower', towerType.name)][0], n * 90))
                frames.append(pygame.transform.rotate(skinObj.skins[('Tower', towerType.name)][1], n * 90))

            towerImages[towerType.name] = frames

        else:
            towerImages[towerType.name] = skinObj.skins[('Tower', towerType.name)]

    return towerImages


Skins = [
    Skin('BTD6 MOAB Class Skin', 'MOAB.png', {
        ('Enemy', 'A'): ['MOAB.png', (89, 57)],
        ('Enemy', 'B'): ['BFB.png', (140, 99)],
        ('Enemy', 'C'): ['DDT.png', (109, 75)],
        ('Enemy', 'D'): ['ZOMG.png', (174, 112)],
        ('Enemy', 'E'): ['BAD.png', (175, 127)]
    }, 2499, 'Enemy', iconSize=(90, 75)),

    Skin('Christmas Towers Skin', 'christmas_skin_icon.png', {
        ('Tower', 'Turret'): ['christmas_turret.png', 'christmas_turret_45.png'],
        ('Tower', 'Ice Tower'): 'christmas_ice_tower.png',
        ('Tower', 'Spike Tower'): 'christmas_spike_tower.png',
        ('Tower', 'Bomb Tower'): 'christmas_bomb_tower.png',
        ('Tower', 'Banana Farm'): 'christmas_banana_farm.png',
        ('Tower', 'Bowler'): 'christmas_bowler.png',
        ('Tower', 'Wizard'): 'christmas_wizard.png',
        ('Tower', 'Inferno'): ['christmas_inferno.png', 'christmas_inactive_inferno.png'],
        ('Tower', 'Village'): 'christmas_village.png',
        ('Tower', 'Sniper'): ['christmas_sniper.png', 'christmas_sniper_45.png'],
        ('Tower', 'Elemental'): 'christmas_elemental.png'
    }, 0, 'Tower', iconSize=(75, 75)),

    Skin('Golden Towers Skin', os.path.join(os.pardir, 'gold_rune.png'), {
        ('Tower', 'Turret'): ['golden_turret.png', 'golden_turret_45.png'],
        ('Tower', 'Ice Tower'): 'golden_ice_tower.png',
        ('Tower', 'Spike Tower'): 'golden_spike_tower.png',
        ('Tower', 'Bomb Tower'): 'golden_bomb_tower.png',
        ('Tower', 'Banana Farm'): 'golden_banana_farm.png',
        ('Tower', 'Bowler'): 'golden_bowler.png',
        ('Tower', 'Wizard'): 'golden_wizard.png',
        ('Tower', 'Inferno'): ['golden_inferno.png', 'golden_inactive_inferno.png'],
        ('Tower', 'Village'): 'golden_village.png',
        ('Tower', 'Sniper'): ['golden_sniper.png', 'golden_sniper_45.png'],
        ('Tower', 'Elemental'): 'golden_elemental.png'
    }, 1499, 'Tower', iconSize=(75, 75)),

    Skin('Halloween Towers Skin', 'halloween_skin_icon.png', {
        ('Tower', 'Turret'): ['halloween_turret.png', 'halloween_turret_45.png'],
        ('Tower', 'Ice Tower'): 'halloween_ice_tower.png',
        ('Tower', 'Spike Tower'): 'halloween_spike_tower.png',
        ('Tower', 'Bomb Tower'): 'halloween_bomb_tower.png',
        ('Tower', 'Banana Farm'): 'halloween_banana_farm.png',
        ('Tower', 'Bowler'): 'halloween_bowler.png',
        ('Tower', 'Wizard'): 'halloween_wizard.png',
        ('Tower', 'Inferno'): ['halloween_inferno.png', 'halloween_inactive_inferno.png'],
        ('Tower', 'Village'): 'halloween_village.png',
        ('Tower', 'Sniper'): ['halloween_sniper.png', 'halloween_sniper_45.png'],
        ('Tower', 'Elemental'): 'halloween_elemental.png'
    }, 0, 'Tower', iconSize=(75, 75))
]

specialSkins = {
    'Christmas Towers Skin': [[2021, 12, 15], [2021, 12, 25]],
    'Halloween Towers Skin': [[2021, 10, 21], [2021, 10, 31]]
}
