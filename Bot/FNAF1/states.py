import time
import pyautogui as pg
from Bot.FNAF1.constants import COORDINATES
from Engine.exceptions import StateCaptureError
from Engine.game_state import GameState
from Engine.vision import Vision

class FNAF1State(GameState):
    def __init__(self):
        super().__init__()

        # Set the self.vision object to be used for state detection, passing in the coordinates from the constants file
        self.vision = Vision(COORDINATES)
        
        # Define all the variables that will be used to track the state of the game
        self.facingRight = False
        self.cameraUp = False
        self.lightOn = False
        self.leftDoorClosed = False
        self.rightDoorClosed = False
        self.robotAtDoor = False
        self.foxyCheck = 0
        self.onTitle = False
        self.star1 = False
        self.star2 = False
        self.star3 = False
        self.inOffice = False

    def detectStars(self):
        if not self.get("star1"): return 0
        if not self.get("star2"): return 1
        if not self.get("star3"): return 2
        return 3

    # This loop is for checking states of the game and setting variables
    def detectStates(self):
        while True:
            # Getting a screenshot instead of calling pixel()
            # Without try it could throw a KeyboardInterrupt error
            screenshot = None

            try:
                screenshot = pg.screenshot()
            except Exception as e:
                print(f"Error taking screenshot: {e}")


            try:
                if screenshot:
                    # If left door button in frame, then facing left
                    pixelCheck = self.vision.getPixel("leftDoor", screenshot)
                    if pg.pixelMatchesColor(expectedRGBColor=(109, 0, 0), sample=pixelCheck, tolerance=50):
                        self.set("facingRight", False)
                    if pg.pixelMatchesColor(expectedRGBColor=(29, 107, 0), sample=pixelCheck, tolerance=80):
                        self.set("facingRight", False)

                    # If right door button in frame, then facing right
                    pixelCheck = self.vision.getPixel("rightDoor", screenshot)
                    if pg.pixelMatchesColor(expectedRGBColor=(163, 0, 0), sample=pixelCheck, tolerance=50):
                        self.set("facingRight", True)
                    if pg.pixelMatchesColor(expectedRGBColor=(35, 128, 0), sample=pixelCheck, tolerance=80):
                        self.set("facingRight", True)

                    # If restroom button in frame, then camera is open
                    pixelCheck = self.vision.getPixel("cameraCheck", screenshot)
                    self.set("cameraUp", pg.pixelMatchesColor(expectedRGBColor=(66, 66, 66), sample=pixelCheck, tolerance=2))

                    # Detect animatronics at the door
                    if self.get("lightOn"):
                        if self.get("facingRight"):
                            pixelCheck = self.vision.getPixel("chicaCheck", screenshot)
                            if pg.pixelMatchesColor(expectedRGBColor=(86, 95, 9), sample=pixelCheck, tolerance=20):
                                self.set("robotAtDoor", True)
                        else: # Facing left
                            # If door closed, check for Bonnie's shadow
                            if self.get("leftDoorClosed"):
                                bonniePixel1 = self.vision.getPixel("bonnieCheck1", screenshot)
                                bonniePixel2 = self.vision.getPixel("bonnieCheck2", screenshot)
                                if pg.pixelMatchesColor(expectedRGBColor=(0, 0, 0), sample=bonniePixel1) and\
                                    pg.pixelMatchesColor(expectedRGBColor=(30, 42, 65), sample=bonniePixel2, tolerance=5):
                                    self.set("robotAtDoor", True)
                            else:
                                pixelCheck = self.vision.getPixel("bonnieCheckDoor", screenshot)
                                if pg.pixelMatchesColor(expectedRGBColor=(54, 37, 63), sample=pixelCheck, tolerance=10):
                                    self.set("robotAtDoor", True)
                    
                    # Detect if you're on the title screen
                    pixelCheck = self.vision.getPixel("titleCheck", screenshot)
                    self.set("onTitle", pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck))

                    # Detect the stars on the menu
                    pixelCheck = self.vision.getPixel("star1", screenshot)
                    self.set("star1", pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck))
                    if self.get("star1"):
                        pixelCheck = self.vision.getPixel("star2", screenshot)
                        self.set("star2", pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck))
                    if self.get("star2"):
                        pixelCheck = self.vision.getPixel("star3", screenshot)
                        self.set("star3", pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck))

                    # Detect if inside the office
                    pixelCheck = self.vision.getPixel("officeCheck", screenshot)
                    self.set("inOffice", pg.pixelMatchesColor(expectedRGBColor=(35, 235, 31), sample=pixelCheck, tolerance=5))
                
            except Exception as e:
                raise StateCaptureError(f"Error capturing game state at {e}")

            time.sleep(0.05)