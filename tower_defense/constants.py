# Imports
import math

from tower_defense.maps import *

# Enemy General Constants
waves = [
    '00' * 3,
    '00' * 5 + '01' * 3,
    '01' * 5,
    '02' * 12,
    '03' * 15,
    '04' * 15,
    '05' * 20,
    '06' * 20,
    '06' * 50,
    '0A',
    '26' * 25,
    '07' * 50,
    '08' * 25,
    '09' * 3,
    '0B',
    '09' * 25,
    '10' * 3,
    '16' * 25,
    '17' * 25,
    '18' * 25,
    '19' * 25,
    '1A' * 2,
    '18' * 50,
    '25' * 10,
    '19' * 50,
    '28' * 50,
    '0A' * 3,
    '0A' * 5,
    '0A' * 8,
    '0C',
    '0C' * 2,
    '0C' * 3,
    '0C' * 5,
    '0C' * 10,
    '0D'
]

enemyColors = {
    '0': (255, 0, 0),
    '1': (0, 0, 221),
    '2': (0, 255, 0),
    '3': (255, 255, 0),
    '4': (255, 20, 147),
    '5': (68, 68, 68),
    '6': (255, 255, 255),
    '7': (16, 16, 16),
    '8': (110, 38, 14),
    '9': (255, 127, 0),
    'A': (146, 43, 62),
    'B': (191, 64, 191),
    'C': (211, 47, 47),
    'D': (64, 64, 64)
}

damages = {
    '0': 1,
    '1': 2,
    '2': 3,
    '3': 4,
    '4': 5,
    '5': 11,
    '6': 23,
    '7': 70,
    '8': 116,
    '9': 16,
    'A': 30,
    'B': 90,
    'C': 150,
    'D': 750
}

speed = {
    '0': 1,
    '1': 1,
    '2': 2,
    '3': 2,
    '4': 3,
    '5': 4,
    '6': 3,
    '7': 2,
    '8': 2,
    '9': 2,
    'A': 1,     # True Speed: 1/3
    'B': 1,     # True Speed: 1/5
    'C': 1,
    'D': 1,     # True Speed: 1/2
    'E': 1      # True Speed: 1/10
}

trueHP = {
    '8': 10,
    '9': 10,
    'A': 2000,
    'B': 5000,
    'C': 3000,
    'D': 25000
}

bossCoins = {
    'A': 150,
    'B': 250,
    'C': 100,
    'D': 500
}

bossFreeze = {
    'A': 3,
    'B': 5,
    'C': 0,
    'D': 2
}

enemiesSpawnNew = {
    '00': None,
    '01': '00',
    '02': '01',
    '03': '02',
    '04': '03',
    '05': '04' * 2,
    '06': '05' * 2,
    '07': '06' * 3,
    '08': '06' * 5,
    '09': '04' * 3,
    '0A': '00' * 15,
    '0B': '03' * 20,
    '0C': '08' + '09' * 2,
    '0D': '0C' * 5,
    '10': None,
    '11': '10',
    '12': '11',
    '13': '12',
    '14': '13',
    '15': '14' * 2,
    '16': '15' * 2,
    '17': '16' * 3,
    '18': '16' * 5,
    '19': '14' * 3,
    '1A': '10' * 10,
    '20': None,
    '21': '20',
    '22': '21',
    '23': '22',
    '24': '23',
    '25': '24' * 2,
    '26': '25' * 2,
    '27': '26' * 3,
    '28': '26' * 5,
}
regenPath = ['0', '1', '2', '3', '4', '5', '6']
strengthPath = ['0', '1', '2', '3', '4', '5', '6', '7', '9', '8', 'A', 'B', 'C', 'D']

# Enemy Property Constants
onlyExplosiveTiers = ['7', 'D']
freezeImmune = ['6', 'C', 'D']
bosses = ['A', 'B', 'C', 'D']
resistant = ['9']

# Math Constants
SQRT2 = math.sqrt(2)
SQRT3 = math.sqrt(3)
RECIPROCALSQRT2 = 1 / SQRT2

SIN0 = 0
SIN30 = 0.5
SIN45 = SQRT2 / 2
SIN60 = SQRT3 / 2
SIN90 = 1
SIN120 = SIN60
SIN135 = SIN45
SIN150 = 0.5
SIN180 = 0
SIN210 = -0.5
SIN225 = -SIN135
SIN240 = -SIN120
SIN270 = -1
SIN300 = SIN240
SIN315 = SIN225
SIN330 = -0.5
SINDEGREES = {
    0: SIN0,
    30: SIN30,
    45: SIN45,
    60: SIN60,
    90: SIN90,
    120: SIN120,
    135: SIN135,
    150: SIN150,
    180: SIN180,
    210: SIN210,
    225: SIN225,
    240: SIN240,
    270: SIN270,
    300: SIN300,
    315: SIN315,
    330: SIN330
}

COS0 = 1
COS30 = SQRT3 / 2
COS45 = SQRT2 / 2
COS60 = 0.5
COS90 = 0
COS120 = -0.5
COS135 = -COS45
COS150 = -COS30
COS180 = -1
COS210 = COS150
COS225 = COS135
COS240 = -0.5
COS270 = 0
COS300 = 0.5
COS315 = -COS225
COS330 = -COS210
COSDEGREES = {
    0: COS0,
    30: COS30,
    45: COS45,
    60: COS60,
    90: COS90,
    120: COS120,
    135: COS135,
    150: COS150,
    180: COS180,
    210: COS210,
    225: COS225,
    240: COS240,
    270: COS270,
    300: COS300,
    315: COS315,
    330: COS330
}

# FPS Constants
MaxFPS = 100
ReplayFPS = 25
ReplayRefreshRate = MaxFPS // ReplayFPS

# Targeting constants
STRONG = 'STRONG'
CLOSE = 'CLOSE'
FIRST = 'FIRST'
LAST = 'LAST'

targetingCycle = [FIRST, STRONG, CLOSE, LAST]

# Misc. Constants
LOCKED = 'LOCKED'
rainbowColors = [[255, 0, 0], [0, 127, 0], [255, 255, 0], [0, 255, 0], [0, 0, 255], [46, 43, 95], [139, 0, 255]]
rainbowShift = [[-0.255, 0.127, 0], [0.255, 0.127, 0], [-0.255, 0, 0], [0, -0.255, 0.255], [0.046, 0.043, -0.16], [0.093, -0.043, 0.16], [0.116, 0, -0.255]]
gameAttrs = ['enemies', 'projectiles', 'piercingProjectiles', 'towers', 'HP', 'coins', 'selected', 'placing', 'nextWave', 'wave', 'shopScroll', 'spawnleft', 'spawndelay', 'ticksSinceNoEnemies', 'ticks', 'towersPlaced', 'replayRefresh', 'Map', 'doubleReloadTicks', 'FinalHP']
playerAttrs = ['mapMakerData', 'statistics', 'achievements', 'mapsBeat', 'runes',  'equippedRune', 'newRunes', 'powerUps', 'powerUpData', 'tokens', 'lastOpenShop', 'shopData', 'gameReplayData', 'sandboxMode', 'status', 'PBs']
defaults = {
    'enemies': [],
    'projectiles': [],
    'piercingProjectiles': [],
    'towers': [],
    'HP': 250,
    'FinalHP': None,
    'coins': 50,
    'selected': None,
    'placing': '',
    'nextWave': 299,
    'wave': 0,
    'shopScroll': 0,
    'spawnleft': '',
    'spawndelay': 9,
    'Map': None,
    'status': 'mapSelect',
    'PBs': {m.name: (None if Maps.index(m) == 0 else LOCKED) for m in Maps},
    'mapMakerData': {
        'name': '',
        'backgroundColor': '',
        'pathColor': '',
        'path': None,
        'field': None
    },
    'sandboxMode': False,
    'statistics': {
        'pops': 0,
        'towersPlaced': 0,
        'towersSold': 0,
        'enemiesMissed': 0,
        'wavesPlayed': 0,
        'wins': {},
        'losses': 0,
        'coinsSpent': 0,
        'totalWins': 0,
        'mapsBeat': 0,
        'bossesKilled': 0
    },
    'ticksSinceNoEnemies': 1,
    'achievements': {
        'pops': 0,
        'wins': 0,
        'spendCoins': 0,
        'beatMaps': 0
    },
    'mapsBeat': 0,
    'runes': [],
    'equippedRune': None,
    'newRunes': 0,
    'powerUps': {
        'lightning': 0,
        'spikes': 0,
        'antiCamo': 0,
        'heal': 0,
        'freeze': 0,
        'reload': 0
    },
    'powerUpData': None,
    'doubleReloadTicks': 0,
    'tokens': 0,
    'lastOpenShop': 0,
    'shopData': [],
    'gameReplayData': [],
    'ticks': 0,
    'towersPlaced': 0,
    'replayRefresh': 0
}
