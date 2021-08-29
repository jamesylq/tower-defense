from tower_defense.maps import *
from tower_defense.constants import *
from tower_defense.functions import *


def update(info, gameInfo, PowerUps):
    for attr in ['win', 'lose', 'mapSelect', 'totalWaves', 'pausedFrom', 'settingsPrev'] + gameAttrs:     # Redundant Attributes
        if hasattr(info, attr):
            delattr(info, attr)

    for attr, default in defaults['statistics'].items():        # Update Statistics
        try:
            info.statistics[attr] = info.statistics[attr]
        except KeyError:
            if attr == 'totalWins':
                try:
                    info.statistics[attr] = sum([val for val in info.statistics['wins'].values()])
                except KeyError:
                    info.statistics[attr] = 0
            else:
                info.statistics[attr] = default

    for attr, default in defaults['achievements'].items():          # Update Achievements
        try:
            info.achievements[attr] = info.achievements[attr]
        except KeyError:
            info.achievements[attr] = default

    for powerUp, default in defaults['powerUps'].items():           # Update Powerups
        try:
            info.powerUps[powerUp] = info.powerUps[powerUp]
        except KeyError:
            info.powerUps[powerUp] = default

    for tower in gameInfo.towers:       # Update pre-2.4
        if not hasattr(tower, 'ID'):
            setattr(tower, 'ID', gameInfo.towers.index(tower))

    for tower in gameInfo.towers:
        if not hasattr(tower, 'targeting'):
            setattr(tower, 'targeting', targetingCycle[0])

    if info.powerUpData is not None:        # Update Powerups
        PowerUps = info.powerUpData

    info.PBs = updateDict(info.PBs, [Map.name for Map in Maps])     # Update PBs

    info.statistics['mapsBeat'] = len([m for m in info.PBs.keys() if type(info.PBs[m]) is int])     # Update Statistic

    foundUnlocked = False           # Update for new Map
    for Map in Maps:
        if Map.name not in info.PBs.keys():
            info.PBs[Map.name] = LOCKED

        if info.PBs[Map.name] != LOCKED:
            foundUnlocked = True

        elif not foundUnlocked:
            info.PBs[Map.name] = None

    Maps.reverse()

    foundCompleted = False
    for Map in Maps:
        if foundCompleted and info.PBs[Map.name] == LOCKED:
            info.PBs[Map.name] = None

        elif type(info.PBs[Map.name]) is int:
            foundCompleted = True

    Maps.reverse()

    if not hasAllUnlocked(info):        # Update Sandboxmode
        gameInfo.sandboxMode = False

    return [info, gameInfo, PowerUps]
