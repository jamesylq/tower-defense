class Map:
    def __init__(self, path, name, backgroundColor, pathColor):
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
    0x136D15,
    0x9B7653
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
    0xAA6C23,
    0xB29705
)
