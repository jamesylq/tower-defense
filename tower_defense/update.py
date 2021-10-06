import os
import glob
import pickle

from tower_defense.maps import *
from tower_defense.constants import *
from tower_defense.functions import *


curr_path = os.path.dirname(__file__)


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

    for tower in gameInfo.towers:       # Update pre-2.8
        if not hasattr(tower, 'targeting'):
            setattr(tower, 'targeting', targetingCycle[0])

    if 'One Line Challenge' not in info.PBs.keys() and 'The End' in info.PBs.keys():        # Update pre-2.10
        info.PBs['One Line Challenge'] = info.PBs['The End']
        try:
            info.statistics['wins']['One Line Challenge'] = info.statistics['wins']['The End']
        except KeyError:
            pass

    if len(info.skinsEquipped) < 2:          # Update pre-3.4
        while len(info.skinsEquipped) < 2:
            info.skinsEquipped.append(None)

    if os.path.exists(os.path.join(curr_path, 'replay-files')):         # Update pre-3.7
        try:
            os.mkdir(os.path.join(curr_path, '..', 'replay-files'))

        except FileExistsError:
            pass

        else:
            replayFiles = [p for p in os.listdir(os.path.join(curr_path, 'replay-files')) if p.endswith('.txt')]

            for replayFile in replayFiles:
                replayFileData = pickle.load(open(os.path.join(curr_path, 'replay-files', replayFile), 'rb'))

                open(os.path.join(curr_path, '..', 'replay-files', replayFile), 'w')
                pickle.dump(replayFileData, open(os.path.join(curr_path, '..', 'replay-files', replayFile), 'wb'))

                os.remove(os.path.join(curr_path, 'replay-files', replayFile))

        finally:
            os.rmdir(os.path.join(curr_path, 'replay-files'))
            print(f'Relocated replay files to {os.path.join(curr_path, "..", "replay-files")}')

    if os.path.exists(os.path.join(curr_path, 'save.txt')):         # Update pre-3.7
        open(os.path.join(curr_path, '..', 'save.txt'), 'w')

        saveFileData = pickle.load(open(os.path.join(curr_path, 'save.txt'), 'rb'))
        pickle.dump(saveFileData, open(os.path.join(curr_path, '..', 'save.txt'), 'wb'))

        print(f'Relocated save.txt to {os.path.join(curr_path, "..", "save.txt")}')

    if os.path.exists(os.path.join(curr_path, 'game.txt')):         # Update pre-3.7
        open(os.path.join(curr_path, '..', 'game.txt'), 'w')

        gameFileData = pickle.load(open(os.path.join(curr_path, 'game.txt'), 'rb'))
        pickle.dump(gameFileData, open(os.path.join(curr_path, '..', 'game.txt'), 'wb'))

        print(f'Relocated game.txt to {os.path.join(curr_path, "..", "game.txt")}')

    if info.powerUpData is not None:        # Update Powerups
        PowerUps = info.powerUpData

    info.PBs = updateDict(info.PBs, [Map.name for Map in Maps])     # Update PBs

    info.statistics['mapsBeat'] = len([m for m in info.PBs.keys() if type(info.PBs[m]) is int])     # Update Statistics

    foundUnlocked = False           # Update Maps
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

    return [info, gameInfo, PowerUps]
