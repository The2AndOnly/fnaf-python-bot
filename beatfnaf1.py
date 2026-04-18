import pyautogui as pg
import psutil
import threading
import time
import os

pg.PAUSE = 0.05

facingRight = False
cameraUp = False
lightOn = False
leftDoorClosed = False
rightDoorClosed = False
robotAtDoor = False
foxyCheck = 0
onTitle = False
star1 = False
star2 = False
star3 = False
inOffice = False
timedOut = False

coordinates = {
    "leftLight" : (0.033854166666666664, 0.6351851851851852),
    "rightLight" : (0.9598958333333333, 0.6527777777777778),
    "leftDoor" : (0.05572916666666667, 0.4222222222222222),
    "rightDoor" : (0.9614583333333333, 0.4444444444444444),
    "westHall" : (0.7765625, 0.8453703703703703),
    "hallCorner" : (0.8557291666666667, 0.9009259259259259),
    "cameraCheck" : (0.9380208333333333, 0.6157407407407407),
    "chicaCheck" : (0.6697916666666667, 0.5333333333333333),
    "bonnieCheck1" : (0.38177083333333334, 0.40185185185185185),
    "bonnieCheck2" : (0.38229166666666664, 0.4666666666666667),
    "bonnieCheckDoor" : (0.12604166666666666, 0.3574074074074074),
    "titleCheck" : (0.1375, 0.6),
    "continue" : (0.21145833333333333, 0.687962962962963),
    "sixthNight" : (0.20572916666666666, 0.7851851851851852),
    "customNight" : (0.26614583333333336, 0.8842592592592593),
    "star1" : (0.15729166666666666, 0.47685185185185186),
    "star2" : (0.21666666666666667, 0.4759259259259259),
    "star3" : (0.27291666666666664, 0.4703703703703704),
    "officeCheck" : (0.09895833333333333, 0.9361111111111111),
    "freddyArrow" : (0.23385416666666667, 0.687037037037037),
    "bonnieArrow" : (0.45208333333333334, 0.6861111111111111),
    "chicaArrow" : (0.6770833333333334, 0.6824074074074075),
    "foxyArrow" : (0.8958333333333334, 0.687962962962963),
    "ready" : (0.8901041666666667, 0.9120370370370371)
}

# Monkey patch for pyautogui's "pixelMatchesColor" function
def customPMC(x=0, y=0, expectedRGBColor=(0, 0, 0), tolerance=0, sample=None):
    if isinstance(x, pg.collections.abc.Sequence) and len(x) == 2:
        raise TypeError('pixelMatchesColor() has updated and no longer accepts a tuple of (x, y) values for the first argument. Pass these arguments as two separate arguments instead: pixelMatchesColor(x, y, rgb) instead of pixelMatchesColor((x, y), rgb)')

    pix = pg.pixel(x, y) if sample == None else sample
    if len(pix) == 3 or len(expectedRGBColor) == 3: # RGB mode
        r, g, b = pix[:3]
        exR, exG, exB = expectedRGBColor[:3]
        return (abs(r - exR) <= tolerance) and (abs(g - exG) <= tolerance) and (abs(b - exB) <= tolerance)
    elif len(pix) == 4 and len(expectedRGBColor) == 4: # RGBA mode
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
pg.pixelMatchesColor = customPMC

def toggleButton(button):
    moveMouse(coordinates[button])
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
    moveMouse(coordinates[cam])
    clickMouse()

# Functions for detecting states
def isCamUp():
    return cameraUp

def isFacingRight():
    return facingRight

def isNotFacingRight():
    return not facingRight

# Controls the night gameplay
def officeLoop():
    global robotAtDoor
    global leftDoorClosed
    global rightDoorClosed
    global foxyCheck

    # Initialize variables
    foxyCheck = 0
    leftDoorClosed = False
    rightDoorClosed = False

    # East hall corner at the start of the night
    toggleCamera()
    waitUntil(isCamUp, 5.0)
    if timedOut: return
    camera("hallCorner")
    time.sleep(0.01)
    toggleCamera()

    while True:
        # Check left light
        lightCheck("leftLight")
        if timedOut: break

        # Toggle door accordingly
        if robotAtDoor and not leftDoorClosed:
            leftDoorClosed = True
            toggleButton("leftDoor")
            if timedOut: break
        elif leftDoorClosed and not robotAtDoor:
            leftDoorClosed = False
            toggleButton("leftDoor")
            if timedOut: break
        robotAtDoor = False

        # Flip camera
        camFlip()
        if timedOut: break

        # If haven't checked foxy in a while, then do that instead of checking Chica
        if foxyCheck >= 50:
            if not rightDoorClosed:
                rightDoorClosed = True
                toggleButton("rightDoor")
                if timedOut: break
            else:
                time.sleep(0.5)
            checkFoxy()
            if timedOut: break
        else:
            checkChica()

            # Flip camera or check Foxy
            if foxyCheck >= 40 and rightDoorClosed:
                checkFoxy()
                if timedOut: break
            else:
                camFlip()
                if timedOut: break

        time.sleep(0.01)

def camFlip():
    global foxyCheck

    toggleCamera()
    waitUntil(isCamUp, 5.0)
    foxyCheck += 1
    toggleCamera()

def lightCheck(light):
    global lightOn

    toggleButton(light)
    lightOn = True
    moveMouse((coordinates[light][0] + 0.01, coordinates[light][1]))
    time.sleep(0.15)
    clickMouse()
    lightOn = False

def checkFoxy():
    global foxyCheck
    global leftDoorClosed

    foxyCheck = 0
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
    if not leftDoorClosed:
        leftDoorClosed = True
        toggleButton("leftDoor")
    else:
        time.sleep(0.5)
    # Continue game loop starting with checking Chica
    checkChica()
    camFlip()

def checkChica():
    global rightDoorClosed
    global robotAtDoor

    # Check right light
    lightCheck("rightLight")

    # Toggle door accordingly
    if robotAtDoor and not rightDoorClosed:
        rightDoorClosed = True
        toggleButton("rightDoor")
    elif rightDoorClosed and not robotAtDoor:
        rightDoorClosed = False
        toggleButton("rightDoor")
    robotAtDoor = False

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

def getPixel(coords, sc):
    width, height = sc.size
    return sc.getpixel((int(coordinates[coords][0] * width), int(coordinates[coords][1] * height)))

def detectStars():
    starCheck = 0
    for _ in range(10):
        if star1: starCheck += 1
        time.sleep(0.1)
    if starCheck == 10:
        starCheck = 0
        for _ in range(10):
            if star2: starCheck += 1
            time.sleep(0.1)
        if starCheck == 10:
            starCheck = 0
            for _ in range(10):
                if star3: starCheck += 1
                time.sleep(0.1)
            return 3 if starCheck == 10 else 2
        else: return 1
    else: return 0

def waitUntil(condition, maxTime):
    global timedOut

    timedOut = False
    endTime = time.time() + maxTime
    while not condition():
        time.sleep(0.01)
        if time.time() >= endTime:
            timedOut = True
            break

# This controls the flow of the game
def gameLoop():
    global onTitle
    global inOffice

    # Wait for the title screen
    while True:
        while True:
            time.sleep(1.0)
            if onTitle or inOffice: break

        if onTitle and not inOffice:
            # Detect how many stars there are
            stars = detectStars()
            
            key = {0: "continue", 1: "sixthNight", 2: "customNight"}.get(stars)
            
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
            
            onTitle = False

        if inOffice:
            # Start office loop after 3 seconds
            time.sleep(3.0)
            officeLoop()
            time.sleep(1.0)
            inOffice = False
    
# This loop is for checking states of the game and setting variables
def detectStates():
    global facingRight
    global robotAtDoor
    global cameraUp
    global onTitle
    global star1
    global star2
    global star3
    global inOffice

    while True:
        # Getting a screenshot instead of calling pixel()
        # Without try it could throw a KeyboardInterrupt error
        screenshot = None

        try:
            screenshot = pg.screenshot()
        except: pass

        try:
            if screenshot:
                # If left door button in frame, then facing left
                pixelCheck = getPixel("leftDoor", screenshot)
                if pg.pixelMatchesColor(expectedRGBColor=(109, 0, 0), sample=pixelCheck, tolerance=50):
                    facingRight = False
                if pg.pixelMatchesColor(expectedRGBColor=(29, 107, 0), sample=pixelCheck, tolerance=80):
                    facingRight = False

                # If right door button in frame, then facing right
                pixelCheck = getPixel("rightDoor", screenshot)
                if pg.pixelMatchesColor(expectedRGBColor=(163, 0, 0), sample=pixelCheck, tolerance=50):
                    facingRight = True
                if pg.pixelMatchesColor(expectedRGBColor=(35, 128, 0), sample=pixelCheck, tolerance=80):
                    facingRight = True

                # If restroom button in frame, then camera is open
                pixelCheck = getPixel("cameraCheck", screenshot)
                cameraUp = pg.pixelMatchesColor(expectedRGBColor=(66, 66, 66), sample=pixelCheck, tolerance=2)

                # Detect animatronics at the door
                if lightOn:
                    if facingRight:
                        pixelCheck = getPixel("chicaCheck", screenshot)
                        if pg.pixelMatchesColor(expectedRGBColor=(86, 95, 9), sample=pixelCheck, tolerance=20):
                            robotAtDoor = True
                    else: # Facing left
                        # If door closed, check for Bonnie's shadow
                        if leftDoorClosed:
                            bonniePixel1 = getPixel("bonnieCheck1", screenshot)
                            bonniePixel2 = getPixel("bonnieCheck2", screenshot)
                            if pg.pixelMatchesColor(expectedRGBColor=(0, 0, 0), sample=bonniePixel1) and\
                                pg.pixelMatchesColor(expectedRGBColor=(30, 42, 65), sample=bonniePixel2, tolerance=5):
                                robotAtDoor = True
                        else:
                            pixelCheck = getPixel("bonnieCheckDoor", screenshot)
                            if pg.pixelMatchesColor(expectedRGBColor=(54, 37, 63), sample=pixelCheck, tolerance=10):
                                robotAtDoor = True
                
                # Detect if you're on the title screen
                pixelCheck = getPixel("titleCheck", screenshot)
                onTitle = pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck)

                # Detect the stars on the menu
                pixelCheck = getPixel("star1", screenshot)
                star1 = pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck)
                if star1:
                    pixelCheck = getPixel("star2", screenshot)
                    star2 = pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck)
                if star2:
                    pixelCheck = getPixel("star3", screenshot)
                    star3 = pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck)
                
                # Detect if inside the office
                pixelCheck = getPixel("officeCheck", screenshot)
                inOffice = pg.pixelMatchesColor(expectedRGBColor=(35, 235, 31), sample=pixelCheck, tolerance=5)
        except: pass

        time.sleep(0.05)

if __name__ == "__main__":
    print("Program started! Waiting for game to open...")

    # Wait for the game to open before starting anything
    def isRunning(name):
        for i in psutil.process_iter(["name"]):
            if i.info["name"] == name:
                return True
        return False

    while True:
        time.sleep(2.0)
        if isRunning("FiveNightsatFreddys.exe"):
            break

    # Wait 5 seconds to make sure the game is open in fullscreen
    time.sleep(5.0)
    moveMouse((0.6, 0.6))

    gameloopProcess = threading.Thread(target=gameLoop)
    detectProcess = threading.Thread(target=detectStates)
    gameloopProcess.start()
    detectProcess.start()