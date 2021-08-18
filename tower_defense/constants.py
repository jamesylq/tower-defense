# Imports
import math

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

# Enemy Property Constants
bosses = ['A', 'B', 'C', 'D']
onlyExplosiveTiers = ['7', 'D']
resistant = ['9']
freezeImmune = ['E']

# Math Constants
SQRT2 = math.sqrt(2)
RECIPROCALSQRT2 = 1 / SQRT2
SIN45 = SQRT2 / 2
COS45 = SQRT2 / 2

# Misc. Constants
rainbowColors = [[255, 0, 0], [0, 127, 0], [255, 255, 0], [0, 255, 0], [0, 0, 255], [46, 43, 95], [139, 0, 255]]
rainbowShift = [[0, 0.127, 0], [0.255, 0.127, 0], [-0.255, 0, 0], [0, -0.255, 0.255], [0.046, 0.043, -0.16], [0.093, -0.043, 0.16], [0.116, 0, -0.255]]

LOCKED = 'LOCKED'
