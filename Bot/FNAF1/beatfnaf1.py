import pyautogui as pg
# from pynput import keyboard
import time
import os

from Engine.input import *
from Engine.exceptions import TimeoutError

from Bot.FNAF1.states import FNAF1State
from Bot.FNAF1.constants import COORDINATES # import the COORDINATES from the constants file

pg.PAUSE = 0.05

state = FNAF1State()

def toggleButton(button):
    moveMouse(COORDINATES[button])
    if "left" in button:
        waitUntil(isNotFacingRight, 5.0)
    if "right" in button:
        waitUntil(isFacingRight, 5.0)
    clickMouse()

def toggleCamera():
    moveMouse((0.43072916666666666, 0.98))
    time.sleep(0.1)
    moveMouse((0.43072916666666666, 0.85))

def camera(cam):
    moveMouse(COORDINATES[cam])
    clickMouse()

# Functions for detecting states
def isCamUp():
    return state.get("cameraUp")
def isFacingRight():
    return state.get("facingRight")
def isNotFacingRight():
    return not isFacingRight()

def camFlip():
    toggleCamera()
    waitUntil(isCamUp, 5.0)
    state.set("foxyCheck", state.get("foxyCheck") + 1)
    toggleCamera()

def lightCheck(light):
    toggleButton(light)
    state.set("lightOn", True)
    moveMouse((COORDINATES[light][0] + 0.01, COORDINATES[light][1]))
    time.sleep(0.15)
    clickMouse()
    state.set("lightOn", False)

def checkFoxy():
    state.set("foxyCheck", 0)

    # Open camera and wait for it to open
    toggleCamera()
    waitUntil(isCamUp, 5.0)
    # Switch to the west hall briefly to make Foxy run if he's there
    camera("westHall")
    time.sleep(0.05)
    camera("hallCorner")
    time.sleep(0.05)
    # Close the camera
    toggleCamera()
    # Close the left door
    if not state.get("leftDoorClosed"):
        state.set("leftDoorClosed", True)
        toggleButton("leftDoor")
    else:
        time.sleep(0.5)
    # Continue game loop starting with checking Chica
    checkChica()
    camFlip()

def checkChica():
    # Check right light
    lightCheck("rightLight")

    # Toggle door accordingly
    if state.get("robotAtDoor") and not state.get("rightDoorClosed"):
        state.set("rightDoorClosed", True)
        toggleButton("rightDoor")
    elif state.get("rightDoorClosed") and not state.get("robotAtDoor"):
        state.set("rightDoorClosed", False)
        toggleButton("rightDoor")
    state.set("robotAtDoor", False)

# Controls the night gameplay
def officeLoop():

    # Initialize variables
    state.set("foxyCheck", 0)
    state.set("leftDoorClosed", False)
    state.set("rightDoorClosed", False)

    # East hall corner at the start of the night
    toggleCamera()
    waitUntil(isCamUp, 5.0)
    camera("hallCorner")
    time.sleep(0.01)
    toggleCamera()
    try:
        while True:
            # Check left light
            lightCheck("leftLight")

            # Toggle door accordingly
            if state.get("robotAtDoor") and not state.get("leftDoorClosed"):
                state.set("leftDoorClosed", True)
                toggleButton("leftDoor")
            elif state.get("leftDoorClosed") and not state.get("robotAtDoor"):
                state.set("leftDoorClosed", False)
                toggleButton("leftDoor")
            state.set("robotAtDoor", False)

            # Flip camera
            camFlip()

            # If haven't checked foxy in a while, then do that instead of checking Chica
            if state.get("foxyCheck") >= 40:
                if not state.get("rightDoorClosed"):
                    state.set("rightDoorClosed", True)
                    toggleButton("rightDoor")
                else:
                    time.sleep(0.5)
                checkFoxy()
            else:
                checkChica()

                # Flip camera or check Foxy
                if state.get("foxyCheck") >= 30 and state.get("rightDoorClosed"):
                    checkFoxy()
                else:
                    camFlip()

            time.sleep(0.01)
    except TimeoutError as e:
        print(f"Office loop timed out: {e}")

def setUpMaxMode(): # 4/20 Mode
    for i in range(4):
        moveMouse(COORDINATES[["freddyArrow","bonnieArrow","chicaArrow","foxyArrow"][i]])
        for _ in range(20):
            if state.get("inOffice"): return # If you got bored and just forced a manual click on 'READY' it should exit
            time.sleep(1.0)
            clickMouse()

# This controls the flow of the game
def gameLoop():
    # Wait for the title screen
    while True:
        while True:
            time.sleep(1.0)
            if state.get("onTitle") or state.get("inOffice"): break

        if state.get("onTitle") and not state.get("inOffice"):
            # Detect how many stars there are
            stars = state.detectStars()
            match stars:
                case 0:
                    moveMouse(COORDINATES["continue"])
                case 1:
                    moveMouse(COORDINATES["sixthNight"])
                case 2:
                    moveMouse(COORDINATES["customNight"])
                    # Set the mode to 20/20/20/20
                    
                    clickMouse()
                    time.sleep(3.0)
                    
                    setUpMaxMode()

                    moveMouse(COORDINATES["ready"])
                case 3:
                    os._exit(1)
            clickMouse()
            time.sleep(1.0)
            state.set("onTitle", False)

        if state.get("inOffice"):
            # Start office loop after 3 seconds
            time.sleep(3.0)
            officeLoop()
            time.sleep(1.0)
            state.set("inOffice", False)