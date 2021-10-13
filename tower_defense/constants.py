# Imports
import math
import random

from tower_defense.maps import *

# Enemy General Constants
waves = [
    '00' * 3,
    '00' * 5 + '01' * 3,
    '01' * 5,
    '01' * 6 + '02' * 6,
    '02' * 5,
    '02' * 3 + '03' * 5,
    '03' * 10,
    '04' * 10,
    '24' * 10,
    '05' * 15,
    '06' * 15,
    '26' * 25,
    '27' * 15,
    '09' * 3,
    '08' * 2,
    '09' * 10,
    '14' * 5,
    '15' * 15,
    '08' * 3,
    '0A',
    '18' * 5,
    '18' * 4 + '09' * 4 + '18' * 4,
    '28' * 10,
    '38' * 15,
    '0A' * 2,
    '0A' * 3,
    '38' * 50,
    '47' * 25,
    '4A',
    '0B',
    '48' * 50,
    '4A' * 2,
    '49' * 10,
    '0B' * 2,
    '0B' * 3,
    '0B' * 5,
    '0B' * 10,
    '4A' * 10,
    '4B',
    '1C',
    '1C' * 3,
    '49' * 50,
    '1C' * 5,
    '1C' * 10,
    ('47' * 10 + '48' * 10) * 10,
    '5C' * 3,
    '5C' * 5,
    '5C' * 10,
    '78' * 50,
    '0D',
    '0D' * 2,
    '0D' * 3 + '1C' * 3,
    '0D' * 5 + '1C' * 3,
    '4D',
    '4D' * 2,
    '4D' * 3,
    '5C' * 25,
    '4D' * 5,
    '4D' * 10,
    '0E'
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
    'D': (64, 64, 0),
    'E': (255, 128, 0)
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
    '8': 50,
    '9': 16,
    'A': 200,
    'B': 420,
    'C': 200,
    'D': 2000,
    'E': 5000
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
    'A': 1,     # True Speed: 1/2
    'B': 1,     # True Speed: 1/5
    'C': 1,
    'D': 1,     # True Speed: 1/3
    'E': 1
}

trueHP = {
    '8': 25,
    '9': 10,
    'A': 250,
    'B': 800,
    'C': 420,
    'D': 8500,
    'E': 60000
}

bossCoins = {
    'A': 150,
    'B': 250,
    'C': 100,
    'D': 500
}

bossFreezes = {
    'A': 2,
    'B': 5,
    'C': 0,
    'D': 3,
    'E': 16
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
    '08': '06' * 2,
    '09': '04' * 3,
    '0A': '08' * 4,
    '0B': '0A' * 2,
    '0D': '0B' * 4,
    '0E': '1C' * 3 + '0D' * 2,
    '10': None,
    '11': '10',
    '12': '11',
    '13': '12',
    '14': '13',
    '15': '14' * 2,
    '16': '15' * 2,
    '17': '16' * 3,
    '18': '16' * 2,
    '19': '14' * 3,
    '1C': '38' * 4,
    '20': None,
    '21': '20',
    '22': '21',
    '23': '22',
    '24': '23',
    '25': '24' * 2,
    '26': '25' * 2,
    '27': '26' * 3,
    '28': '26' * 2,
    '30': None,
    '31': '30',
    '32': '31',
    '33': '32',
    '34': '33',
    '35': '34' * 2,
    '36': '35' * 2,
    '38': '36' * 2,
    '40': None,
    '41': '40',
    '42': '41',
    '43': '42',
    '44': '43',
    '45': '44' * 2,
    '46': '45' * 2,
    '47': '46' * 3,
    '48': '46' * 2,
    '49': '44' * 3,
    '4A': '48' * 4,
    '4B': '4A' * 2,
    '4D': '4B' * 4,
    '50': None,
    '51': '50',
    '52': '51',
    '53': '52',
    '54': '53',
    '55': '54' * 2,
    '56': '55' * 2,
    '58': '56' * 2,
    '5C': '58' * 4,
    '70': None,
    '71': '70',
    '72': '71',
    '73': '72',
    '74': '73',
    '75': '74' * 2,
    '76': '75' * 2,
    '78': '76' * 2,
}
strengthPath = ['0', '1', '2', '3', '4', '5', '6', '7', '9', '8', 'A', 'B', 'C', 'D', 'E']
regenPath = ['0', '1', '2', '3', '4', '5', '6', '8']
regenUpdateTimer = 50

# Enemy Property Constants
onlyExplosiveTiers = ['7', 'C']
bosses = ['A', 'B', 'C', 'D', 'E']
freezeImmune = ['6'] + bosses
resistant = ['9', 'C']
forceCamo = ['C']

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

# Targeting Constants
STRONG = 'STRONG'
CLOSE = 'CLOSE'
FIRST = 'FIRST'
LAST = 'LAST'

targetingCycle = [FIRST, STRONG, CLOSE, LAST]

# Achievement Constants
achievementRequirements = {
    'beatMaps': {
        'attr': 'mapsBeat',
        'tiers': [1, len(Maps) // 2, len(Maps)]
    },
    'pops': {
        'attr': 'pops',
        'tiers': [1000, 100000, 1000000]
    },
    'wins': {
        'attr': 'totalWins',
        'tiers': [5, 20, 50]
    },
    'spendCoins': {
        'attr': 'coinsSpent',
        'tiers': [10000, 100000, 1000000]
    },
    'killBosses': {
        'attr': 'bossesKilled',
        'tiers': [1, 50, 500]
    }
}

achievements = {
    'beatMaps': {
        'names': ['First Map!', 'Map Conqueror', 'Master of The End'],
        'rewards': [50, 100, 250],
        'lore': 'Beat [%] unique maps!'
    },
    'pops': {
        'names': ['Balloon Popper', 'Balloon Fighter', 'Balloon Exterminator'],
        'rewards': [75, 200, 1000],
        'lore': 'Pop [%] balloons!'
    },
    'wins': {
        'names': ['Tower-defense Rookie', 'Tower-defense Pro', 'Tower-defense Legend'],
        'rewards': [85, 250, 1250],
        'lore': 'Win [%] games!'
    },
    'spendCoins': {
        'names': ['Money Spender', 'Rich Player', 'Millionaire!'],
        'rewards': [75, 150, 400],
        'lore': 'Spend [%] coins!'
    },
    'killBosses': {
        'names': ['Slayer', 'Large Enemies Popper', 'Boss Exterminator'],
        'rewards': [100, 250, 750],
        'lore': 'Kill [%] bosses!'
    }
}

# Misc. Constants
LOCKED = 'LOCKED'
INFINITYSTR = '∞'

rainbowColors = [[255, 0, 0], [0, 127, 0], [255, 255, 0], [0, 255, 0], [0, 0, 255], [46, 43, 95], [139, 0, 255]]
rainbowShift = [[-0.255, 0.127, 0], [0.255, 0.127, 0], [-0.255, 0, 0], [0, -0.255, 0.255], [0.046, 0.043, -0.16], [0.093, -0.043, 0.16], [0.116, 0, -0.255]]

gameAttrs = ['enemies', 'projectiles', 'piercingProjectiles', 'towers', 'HP', 'coins', 'selected', 'placing', 'nextWave', 'wave', 'shopScroll', 'spawnleft', 'spawndelay', 'ticksSinceNoEnemies', 'ticks', 'towersPlaced', 'replayRefresh', 'Map', 'doubleReloadTicks', 'FinalHP', 'spawnPath']
playerAttrs = ['mapMakerData', 'statistics', 'achievements', 'mapsBeat', 'runes',  'equippedRune', 'newRunes', 'powerUps', 'powerUpData', 'tokens', 'lastOpenShop', 'shopData', 'gameReplayData', 'sandboxMode', 'status', 'PBs', 'claimedAchievementRewards', 'cosmeticPage', 'skins', 'skinsEquipped', 'tutorialPhase']
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
    'status': 'tutorial',
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
        'beatMaps': 0,
        'killBosses': 0
    },
    'claimedAchievementRewards': {
        'pops': 0,
        'wins': 0,
        'spendCoins': 0,
        'beatMaps': 0,
        'killBosses': 0
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
    'replayRefresh': 0,
    'spawnPath': 0,
    'cosmeticPage': 'runes',
    'skins': [],
    'skinsEquipped': [None, None],
    'tutorialPhase': 0
}
