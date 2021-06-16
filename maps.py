class Map:
    def __init__(self, path: list, name: str, backgroundColor: int, pathColor: int):
        self.name = name
        self.path = path
        self.backgroundColor = backgroundColor
        self.pathColor = pathColor


PLAINS = Map(
    [
        [25, 0],
        [25, 375],
        [500, 375],
        [500, 25],
        [350, 25],
        [350, 175],
        [750, 175],
        [750, 0]
    ],
    "Plains",
    (19, 109, 21),
    (155, 118, 83)
)

DESERT = Map(
    [
        [0, 25],
        [750, 25],
        [750, 200],
        [25, 200],
        [25, 375],
        [800, 375]
    ],
    "Desert",
    (170, 108, 35),
    (178, 151, 5)
)

POND = Map(
    [
        [0, 25],
        [700, 25],
        [700, 375],
        [100, 375],
        [100, 75],
        [800, 75]
    ],
    "Pond",
    (6, 50, 98),
    (0, 0, 255)
)

LAVA_SPIRAL = Map(
    [
        [300, 225],
        [575, 225],
        [575, 325],
        [125, 325],
        [125, 125],
        [675, 125],
        [675, 425],
        [25, 425],
        [25, 0]
    ],
    "Lava Spiral",
    (207, 16, 32),
    (255, 140, 0)
)

THE_END = Map(
    [
        [0, 225],
        [800, 225]
    ],
    "The End",
    (100, 100, 100),
    (200, 200, 200)
)
