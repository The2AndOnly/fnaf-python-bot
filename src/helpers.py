'''Helper functions for the FNAF bot'''

import time
import pyautogui as pg
import psutil

from .configs import COORDINATES

# Monkey patch for pyautogui's "pixelMatchesColor" function
def customPMC(x=0, y=0, expectedRGBColor=(0, 0, 0), tolerance=0, sample=None):
    if isinstance(x, pg.collections.abc.Sequence) and len(x) == 2:
        raise TypeError('pixelMatchesColor() has updated and no longer accepts a tuple of (x, y) values for the first argument. Pass these arguments as two separate arguments instead: pixelMatchesColor(x, y, rgb) instead of pixelMatchesColor((x, y), rgb)')

    pix = pg.pixel(x, y) if sample == None else sample
    if len(pix) == 3 or len(expectedRGBColor) == 3:  # RGB mode
        r, g, b = pix[:3]
        exR, exG, exB = expectedRGBColor[:3]
        return (abs(r - exR) <= tolerance) and (abs(g - exG) <= tolerance) and (abs(b - exB) <= tolerance)
    elif len(pix) == 4 and len(expectedRGBColor) == 4:  # RGBA mode
        r, g, b, a = pix
        exR, exG, exB, exA = expectedRGBColor
        return (
            (abs(r - exR) <= tolerance)
            and (abs(g - exG) <= tolerance)
            and (abs(b - exB) <= tolerance)
            and (abs(a - exA) <= tolerance)
        )
    else:
        assert False, (
            'Color mode was expected to be length 3 (RGB) or 4 (RGBA), but pixel is length %s and expectedRGBColor is length %s'  # noqa
            % (len(pix), len(expectedRGBColor))
        )

def moveMouse(coords):
    pg.moveTo(coords[0] * pg.size()[0], coords[1] * pg.size()[1])

def clickMouse():
    pg.mouseDown()
    time.sleep(0.02)
    pg.mouseUp()
    time.sleep(0.02)

def getPosition():
    width, height = pg.size()
    return (pg.position().x / width, pg.position().y / height)

def getPixel(coords, sc):
    width, height = sc.size
    x = int(COORDINATES[coords][0] * width)
    y = int(COORDINATES[coords][1] * height)
    return sc.getpixel((x, y))

# Checks if a process with the given name is running
def isRunning(name):
    for i in psutil.process_iter(["name"]):
        if i.info["name"] == name:
            return True
    return False
