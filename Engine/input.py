import pyautogui as pg
import time
from Engine.exceptions import TimeoutError

def moveMouse(coords):
    pg.moveTo(
            coords[0] * pg.size()[0],
            coords[1] * pg.size()[1]
        )

def clickMouse():
    pg.mouseDown()
    time.sleep(0.02)
    pg.mouseUp()
    time.sleep(0.02)

def getPosition():
    width, height = pg.size()
    return (pg.position().x / width, pg.position().y / height)

def waitUntil(condition, maxTime):
    endTime = time.time() + maxTime
    while not condition():
        time.sleep(0.01)
        if time.time() >= endTime:
            raise TimeoutError(f"Timed out waiting for {condition.__name__}")