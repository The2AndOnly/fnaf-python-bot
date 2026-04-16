import time

import pyautogui as pg

from .configs import Screen
from .helpers import getPixel
from .game_state import gameState
from .office_state import officeState

# Game's life cycle: checks states and sets variables
def gameLifeCycle():
    while True:
        # Getting a screenshot instead of calling pixel()
        # Without try it could throw a KeyboardInterrupt error
        screenshot = None
        try:
            screenshot = pg.screenshot()
            if not screenshot:
                pass
            # If left door button in frame, then facing left
            pixelCheck = getPixel("leftDoor", screenshot)
            isRed = pg.pixelMatchesColor(expectedRGBColor=(109, 0, 0), sample=pixelCheck, tolerance=50)
            isGreen = pg.pixelMatchesColor(expectedRGBColor=(29, 107, 0), sample=pixelCheck, tolerance=80)
            if isRed or isGreen:
                officeState.facingRight = False
            # If right door button in frame, then facing right
            pixelCheck = getPixel("rightDoor", screenshot)
            isRed = pg.pixelMatchesColor(expectedRGBColor=(163, 0, 0), sample=pixelCheck, tolerance=50)
            isGreen = pg.pixelMatchesColor(expectedRGBColor=(35, 128, 0), sample=pixelCheck, tolerance=80)
            if isRed or isGreen:
                officeState.facingRight = True
            # If restroom button in frame, then camera is open
            pixelCheck = getPixel("cameraCheck", screenshot)
            officeState.cameraUp = pg.pixelMatchesColor(expectedRGBColor=(66, 66, 66), sample=pixelCheck, tolerance=2)
            # Detect animatronics at the door
            if officeState.lightOn:
                if officeState.facingRight:
                    pixelCheck = getPixel("chicaCheck", screenshot)
                    if pg.pixelMatchesColor(expectedRGBColor=(86, 95, 9), sample=pixelCheck, tolerance=20):
                        officeState.anamatronicAtDoor = True
                else: # Facing left
                    # If door closed, check for Bonnie's shadow
                    if officeState.leftDoorClosed:
                        bonniePixel1 = getPixel("bonnieCheck1", screenshot)
                        bonniePixel2 = getPixel("bonnieCheck2", screenshot)
                        pixel1Black = pg.pixelMatchesColor(expectedRGBColor=(0, 0, 0),
                                                           sample=bonniePixel1)
                        pixel2Blue = pg.pixelMatchesColor(expectedRGBColor=(30, 42, 65),
                                                          sample=bonniePixel2, tolerance=5)
                        if pixel1Black and pixel2Blue:
                            officeState.anamatronicAtDoor = True
                    else:
                        pixelCheck = getPixel("bonnieCheckDoor", screenshot)
                        if pg.pixelMatchesColor(expectedRGBColor=(54, 37, 63),
                                                sample=pixelCheck, tolerance=10):
                            officeState.anamatronicAtDoor = True
            # Detect if on title screen
            pixelCheck = getPixel("titleCheck", screenshot)
            onTitle = pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck)
            if onTitle:
                gameState.screen = Screen.TITLE
            # Detect stars on menu
            stars = 0
            pixelCheck = getPixel("star1", screenshot)
            star1 = pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck)
            if star1:
                stars += 1
                pixelCheck = getPixel("star2", screenshot)
                star2 = pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck)
                if star2:
                    stars += 1
                    pixelCheck = getPixel("star3", screenshot)
                    star3 = pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck)
                    stars += int(star3)
            gameState.numStars = stars
            # Detect if inside the office
            pixelCheck = getPixel("officeCheck", screenshot)
            inOffice = pg.pixelMatchesColor(expectedRGBColor=(35, 235, 31),
                                            sample=pixelCheck, tolerance=5)
            if inOffice:
                gameState.screen = Screen.OFFICE
        except:
            pass
        time.sleep(0.05)
