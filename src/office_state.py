import time

from .helpers import moveMouse, clickMouse
from .configs import COORDINATES as coordinates

class OfficeState:
    '''
    Class to represent the state of the office and control the flow of the night.
    DO NOT INSTANTIATE, use `officeState` instead.
    '''

    def __init__(self):
        self.facingRight = False
        self.cameraUp = False
        self.lightOn = False
        self.leftDoorClosed = False
        self.rightDoorClosed = False
        self.anamatronicAtDoor = False
        self.foxyCheck = 0
        self.timedOut = False
    
    def isCamUp(self):
        return self.cameraUp
    def isFacingRight(self):
        return self.facingRight
    def isNotFacingRight(self):
        return not self.facingRight
    
    def waitUntil(self, condition, maxTime):
        self.timedOut = False
        endTime = time.time() + maxTime
        while not condition():
            time.sleep(0.01)
            if time.time() >= endTime:
                self.timedOut = True
                break
    
    def toggleButton(self, button):
        moveMouse(coordinates[button])
        if "left" in button:
            self.waitUntil(self.isNotFacingRight, 5.0)
        if "right" in button:
            self.waitUntil(self.isFacingRight, 5.0)
        clickMouse()

    def toggleCamera(self):
        moveMouse((0.43072916666666666, 0.98))
        time.sleep(0.1)
        moveMouse((0.43072916666666666, 0.85))

    def camera(self, cam):
        moveMouse(coordinates[cam])
        clickMouse()
    
    def camFlip(self):
        self.toggleCamera()
        self.waitUntil(self.isCamUp, 5.0)
        self.foxyCheck += 1
        self.toggleCamera()
    
    def lightCheck(self, light):
        self.toggleButton(light)
        self.lightOn = True
        moveMouse((coordinates[light][0] + 0.01, coordinates[light][1]))
        time.sleep(0.15)
        clickMouse()
        self.lightOn = False
    
    def checkFoxy(self):
        self.foxyCheck = 0
        # Open camera and wait for it to open
        self.toggleCamera()
        self.waitUntil(self.isCamUp, 5.0)
        # Switch to the west hall briefly to make Foxy run if he's there
        self.camera("westHall")
        time.sleep(0.05)
        self.camera("hallCorner")
        time.sleep(0.05)
        # Close the camera
        self.toggleCamera()
        # Close the left door
        if not self.leftDoorClosed:
            self.leftDoorClosed = True
            self.toggleButton("leftDoor")
        else:
            time.sleep(0.5)
        # Continue game loop starting with checking Chica
        self.checkChica()
        self.camFlip()

    def checkChica(self):
        # Check right light
        self.lightCheck("rightLight")
        # Toggle door accordingly
        if self.anamatronicAtDoor and not self.rightDoorClosed:
            self.rightDoorClosed = True
            self.toggleButton("rightDoor")
        elif self.rightDoorClosed and not self.anamatronicAtDoor:
            self.rightDoorClosed = False
            self.toggleButton("rightDoor")
        self.anamatronicAtDoor = False
    
    # Controls the night gameplay
    def loop(self):
        # Initialize variables
        self.foxyCheck = 0
        self.leftDoorClosed = False
        self.rightDoorClosed = False
        # East hall corner at the start of the night
        self.toggleCamera()
        self.waitUntil(self.isCamUp, 5.0)
        if self.timedOut:
            return
        self.camera("hallCorner")
        time.sleep(0.01)
        self.toggleCamera()
        while True:
            # Check left light
            self.lightCheck("leftLight")
            if self.timedOut:
                break
            # Toggle door accordingly
            if self.anamatronicAtDoor and not self.leftDoorClosed:
                self.leftDoorClosed = True
                self.toggleButton("leftDoor")
                if self.timedOut:
                    break
            elif self.leftDoorClosed and not self.anamatronicAtDoor:
                self.leftDoorClosed = False
                self.toggleButton("leftDoor")
                if self.timedOut:
                    break
            self.anamatronicAtDoor = False
            # Flip camera
            self.camFlip()
            if self.timedOut:
                break
            # If haven't checked foxy in a while, then do that instead of checking Chica
            if self.foxyCheck >= 50:
                if not self.rightDoorClosed:
                    self.rightDoorClosed = True
                    self.toggleButton("rightDoor")
                    if self.timedOut:
                        break
                else:
                    time.sleep(0.5)
                self.checkFoxy()
                if self.timedOut:
                    break
            else:
                self.checkChica()
                # Flip camera or check Foxy
                if self.foxyCheck >= 40 and self.rightDoorClosed:
                    self.checkFoxy()
                    if self.timedOut:
                        break
                else:
                    self.camFlip()
                    if self.timedOut:
                        break
            time.sleep(0.01)

officeState = OfficeState()
