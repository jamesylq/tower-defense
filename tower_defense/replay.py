from tower_defense.constants import *


class Update:
    def __init__(self, updateType, ticks: int, data: list):
        self.updateType = updateType
        self.ticks = ticks

        if self.updateType == HEAL:
            self.heal = data[0]

        if self.updateType == GAINCOINS:
            self.coins = data[0]

        if self.updateType == SELLTOWER:
            self.ID = data[0]

        if self.updateType == PLACETOWER:
            self.towerType = data[0]
            self.x, self.y = data[1]
            self.ID = data[2]

        if self.updateType == USEABILITY:
            self.ID = data[0]

        if self.updateType == SPAWNSPIKE:
            self.x, self.y = data[0]

        if self.updateType == USEPOWERUP:
            self.powerUpType = data[0]

        if self.updateType == UPGRADETOWER:
            self.path = data[0]
            self.ID = data[1]

        if self.updateType == PAUSEICETOWER:
            self.ID = data[0]
