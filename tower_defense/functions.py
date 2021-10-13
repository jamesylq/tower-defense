import pygame

from typing import *

from tower_defense.constants import *


def updateDict(d: dict, l: list) -> dict:
    """Re-order the items in d based on the items in l and deletes redundant items."""

    newDict = {}
    oldDict = d.copy()

    keys = list(oldDict.keys())
    values = list(oldDict.values())

    for item in l:
        try:
            index = keys.index(item)
            newDict[keys[index]] = values[index]
        except ValueError:
            continue

    return newDict


@overload
def removeCharset(s: str, charset: List[str]) -> str: ...
@overload
def removeCharset(s: str, charset: str) -> str: ...

def removeCharset(s, charset) -> str:
    """Remove all charaters in charset from s and returns the result."""

    for char in charset:
        s = s.replace(char, '')

    return s


def durationToString(duration: SupportsFloat) -> str:
    """Takes a duration in seconds and returns a string in the format h:mm:ss or mm:ss."""

    duration = round(duration)

    h = math.floor(duration // 3600)
    m = math.floor((duration - h * 3600) // 60)
    s = math.floor(duration - h * 3600 - m * 60)

    m2dStr = f'0{m}' if m < 10 else str(m)
    s2dStr = f'0{s}' if s < 10 else str(s)

    if h > 0:
        return f'{h}:{m2dStr}:{s2dStr}'
    else:
        return f'{m2dStr}:{s2dStr}'


def durationToStr(duration: SupportsFloat) -> str:
    """Alias for durationToString(duration)."""
    return durationToString(duration)


def hexToRGB(hexString: str) -> Tuple[int, int, int]:
    """Converts a hexadecimal color value to RGB."""

    hexString = removeCharset(hexString, ['0x', '#'])

    if len(hexString) > 6:
        raise ValueError('RGB input error')

    if len(hexString) == 6:
        r, g, b = hexString[:2], hexString[2:4], hexString[4:]

    elif len(hexString) == 5:
        r, g, b = hexString[0], hexString[1:3], hexString[3:]

    else:
        r = '0'
        if len(hexString) == 4:
            g, b = hexString[:2], hexString[2:]

        elif len(hexString) == 3:
            g, b = hexString[0], hexString[1:]

        else:
            g, b = '0', hexString

    return int(r, 16), int(g, 16), int(b, 16)
