import os
import time

from .office_state import officeState
from .helpers import moveMouse, clickMouse
from .configs import COORDINATES as coordinates, Screen

class GameState:
    '''
    Class to represent the state of the game and control the flow of the game.
    DO NOT INSTANTIATE, use `gameState` instead.
    '''

    def __init__(self):
        self.screen = Screen.TITLE
        self.numStars = 0
    
    def detectStars(self):
        numStars = self.numStars
        time.sleep(numStars if numStars > 0 else 1)
        return numStars

    # This controls the flow of the game
    def loop(self):
        # Wait for the title screen
        while True:
            while True:
                time.sleep(1.0)
                if self.screen in (Screen.TITLE, Screen.OFFICE):
                    break
            if self.screen == Screen.TITLE:
                # Detect how many stars there are
                stars = self.detectStars()
                key = {0: "continue", 1: "sixthNight", 2: "customNight"}[stars]
                if stars == 3:
                    os._exit(1)
                if key:
                    moveMouse(coordinates[key])
                clickMouse()
                time.sleep(1.0)
                if stars == 2:
                    # Set the mode to 20/20/20/20
                    time.sleep(3.0)
                    for i in range(4):
                        moveMouse(coordinates[["freddyArrow","bonnieArrow","chicaArrow","foxyArrow"][i]])
                        for _ in range([19, 17, 17, 19][i]):
                            time.sleep(1.0)
                            clickMouse()
                    moveMouse(coordinates["ready"])
                    clickMouse()
                self.screen = Screen.OFFICE
            if self.screen == Screen.OFFICE:
                # Start office loop after 3 seconds
                time.sleep(3.0)
                officeState.loop()
                time.sleep(1.0)
                self.inOffice = False

gameState = GameState()
