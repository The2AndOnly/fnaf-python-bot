"""
FNAF 1 Browser Autoplayer - adapted for the irv77/hd_fnaf HTML5 port.
Plays FNAF 1 in the browser automatically using pixel detection + pyautogui.

SETUP:
  1. Open https://irv77.github.io/hd_fnaf/1/ in your browser.
  2. Press F11 to make the browser truly fullscreen.
  3. Start a night manually (so you're past any intro).
  4. Run this script. Press Enter when prompted.

DEBUG KEYS (while running):
  p = print normalized mouse position (for calibration)
  c = print RGB color under cursor (for calibration)
  q = quit
"""

import os
import time
import threading
import psutil
import pyautogui as pg
from pynput import keyboard

# =========================================================================
# CONFIG
# =========================================================================

# DUMB_MODE: Skip Bonnie detection, just blindly close left door on a 2s cycle.
# Useful for testing right-side (Chica) logic without the Bonnie bug.
DUMB_MODE = False

# DEBUG_LOG: Print every pixel color detectStates reads, with labels.
# Useful for calibrating without staring at the game yourself.
DEBUG_LOG = True

# SAVE_SCREENSHOTS: Save periodic screenshots + death screenshots to a folder
# so you can review what happened later instead of watching in real time.
# Saves to ./fnaf_screenshots/ in the same directory as this script.
SAVE_SCREENSHOTS = True

# =========================================================================

import os as _os_for_screenshots
SCREENSHOT_DIR = _os_for_screenshots.path.join(
    _os_for_screenshots.path.dirname(_os_for_screenshots.path.abspath(__file__)),
    "fnaf_screenshots"
)
if SAVE_SCREENSHOTS:
    _os_for_screenshots.makedirs(SCREENSHOT_DIR, exist_ok=True)

_recent_screenshots = []  # Rolling buffer of the last N screenshots for death capture
_screenshot_counter = 0

def saveScreenshot(screenshot, label="periodic"):
    """Save a screenshot with a timestamp and label to the screenshots folder."""
    global _screenshot_counter
    if not SAVE_SCREENSHOTS or screenshot is None:
        return
    try:
        _screenshot_counter += 1
        timestamp = time.strftime("%H%M%S")
        filename = f"{timestamp}_{_screenshot_counter:04d}_{label}.png"
        path = _os_for_screenshots.path.join(SCREENSHOT_DIR, filename)
        screenshot.save(path)
    except Exception as e:
        print(f"Screenshot save failed: {e}")


# Disable FAILSAFE so jumpscares don't crash the script by flinging cursor.
pg.FAILSAFE = False

# Globals for state tracking across threads
facingRight = False
cameraUp = False
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
lightOn = False

# NOTE: These coordinates assume the game fills the ENTIRE screen.
# Press F11 in your browser for true fullscreen before starting.
# If pixels/clicks are off, use the debug keys ('p' and 'c') to recalibrate.
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
    "bonnieCheckDoor" : (0.12, 0.39),
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
        assert False, 'Color mode was expected to be length 3 (RGB) or 4 (RGBA), but pixel is length %s and expectedRGBColor is length %s' % (len(pix), len(expectedRGBColor))

pg.pixelMatchesColor = customPMC


def normalizedToPixel(coord, screenSize=None):
    """Convert normalized (0-1) coord to pixel coord based on screen size."""
    if screenSize is None:
        screenSize = pg.size()
    return (int(coord[0] * screenSize[0]), int(coord[1] * screenSize[1]))


def getPixel(name, screenshot=None):
    """Get the pixel RGB at a named coordinate, from a screenshot or live."""
    if screenshot is None:
        px, py = normalizedToPixel(coordinates[name])
        return pg.pixel(px, py)
    else:
        w, h = screenshot.size
        px = int(coordinates[name][0] * w)
        py = int(coordinates[name][1] * h)
        return screenshot.getpixel((px, py))


def clickAt(name):
    """Click at a named normalized coordinate."""
    px, py = normalizedToPixel(coordinates[name])
    pg.click(px, py)


def moveTo(name):
    """Move mouse to a named normalized coordinate without clicking."""
    px, py = normalizedToPixel(coordinates[name])
    pg.moveTo(px, py)


# =========================================================================
# DEBUG KEYBOARD LISTENER
# =========================================================================

def onKeyPress(key):
    global timedOut
    try:
        if key.char == 'q':
            print("Quit requested.")
            timedOut = True
            return False
        elif key.char == 'p':
            x, y = pg.position()
            sw, sh = pg.size()
            nx, ny = x / sw, y / sh
            print(f"Mouse: ({x}, {y}) normalized=({nx:.6f}, {ny:.6f})")
        elif key.char == 'c':
            x, y = pg.position()
            rgb = pg.pixel(x, y)
            print(f"Color at ({x}, {y}): RGB{rgb}")
    except AttributeError:
        pass


# =========================================================================
# FOXY CHECKING
# =========================================================================

def checkFoxy():
    """Check pirate cove for Foxy. Returns True if he's there (safe)."""
    global cameraUp, foxyCheck
    # This function is called with camera already up on west hall view
    # Just count iterations for now - real implementation would check pixels
    foxyCheck += 1
    return True


# =========================================================================
# BONNIE CHECKING
# =========================================================================

def checkBonnie():
    """Check if Bonnie is at the left door using blue-signature detection."""
    global robotAtDoor
    if DUMB_MODE:
        return
    try:
        r, g, b = pg.pixel(*normalizedToPixel(coordinates["bonnieCheckDoor"]))[:3]
        brightness = r + g + b
        # Bonnie signature: blue-purple face (B > R, B > G, non-black)
        if b > r + 10 and b > g + 10 and brightness > 60:
            robotAtDoor = True
    except Exception:
        pass


# =========================================================================
# STATE DETECTION THREAD
# =========================================================================

def detectStates():
    global facingRight
    global robotAtDoor
    global cameraUp
    global onTitle
    global star1
    global star2
    global star3
    global inOffice
    global lightOn

    lastLogTime = 0.0
    lastScreenshotTime = 0.0
    lastInOffice = False

    while True:
        if timedOut:
            return

        screenshot = None

        try:
            screenshot = pg.screenshot()
        except: pass

        # Maintain rolling buffer of last 5 screenshots for death capture
        if screenshot and SAVE_SCREENSHOTS:
            _recent_screenshots.append((time.time(), screenshot))
            if len(_recent_screenshots) > 5:
                _recent_screenshots.pop(0)

        try:
            if screenshot:
                # Are we facing the right? (used to know where mouse is)
                pixelCheck = getPixel("rightDoor", screenshot)
                facingRight = pg.pixelMatchesColor(expectedRGBColor=(35, 33, 33), sample=pixelCheck, tolerance=100)

                # Are cameras up?
                pixelCheck = getPixel("cameraCheck", screenshot)
                cameraUp = pg.pixelMatchesColor(expectedRGBColor=(67, 67, 67), sample=pixelCheck, tolerance=25)

                # Is the light on? (check left door area brightness)
                pixelCheck = getPixel("leftDoor", screenshot)
                lightOn = pg.pixelMatchesColor(expectedRGBColor=(147, 147, 146), sample=pixelCheck, tolerance=80)

                # Check for Chica at right door
                if lightOn and facingRight:
                    pixelCheck = getPixel("chicaCheck", screenshot)
                    if pg.pixelMatchesColor(expectedRGBColor=(86, 95, 9), sample=pixelCheck, tolerance=50):
                        robotAtDoor = True
                    else:
                        # Only check for Bonnie when door is open.
                        # HD port insight: Bonnie's face reads as dark blue-purple,
                        # like RGB (79, 95, 147) at his snout between the eyes.
                        # Empty hallway reads (0,0,0) or warm gray.
                        # Camera-edge false positives read as neutral gray like
                        # (67, 67, 67) - bright but NOT blue-dominant.
                        # So we detect Bonnie via a "blue dominance" signature:
                        # B must be meaningfully higher than both R and G.
                        if not leftDoorClosed:
                            r, g, b = getPixel("bonnieCheckDoor", screenshot)[:3]
                            brightness = r + g + b
                            # Bonnie signature: blue-purple face
                            # - B > R + 10 (blue channel dominant over red)
                            # - B > G + 10 (blue channel dominant over green)
                            # - Some minimum brightness to reject pure black
                            if b > r + 10 and b > g + 10 and brightness > 60:
                                robotAtDoor = True

                pixelCheck = getPixel("titleCheck", screenshot)
                onTitle = pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck, tolerance=30)

                pixelCheck = getPixel("star1", screenshot)
                star1 = pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck, tolerance=30)
                if star1:
                    pixelCheck = getPixel("star2", screenshot)
                    star2 = pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck, tolerance=30)
                if star2:
                    pixelCheck = getPixel("star3", screenshot)
                    star3 = pg.pixelMatchesColor(expectedRGBColor=(255, 255, 255), sample=pixelCheck, tolerance=30)

                pixelCheck = getPixel("officeCheck", screenshot)
                inOffice = pg.pixelMatchesColor(expectedRGBColor=(71, 233, 65), sample=pixelCheck, tolerance=40)

                # Debug logging - prints the actual RGB values every 2s so we can
                # calibrate without staring at the game.
                if DEBUG_LOG and (time.time() - lastLogTime > 2.0):
                    lastLogTime = time.time()
                    try:
                        bd = getPixel("bonnieCheckDoor", screenshot)
                        bd_brightness = bd[0] + bd[1] + bd[2]
                        # Blue-dominance check: does this look like Bonnie?
                        bd_is_bonnie = (bd[2] > bd[0] + 10 and bd[2] > bd[1] + 10 and bd_brightness > 60)
                        cc = getPixel("chicaCheck", screenshot)
                        ld = getPixel("leftDoor", screenshot)
                        rd = getPixel("rightDoor", screenshot)
                        cam = getPixel("cameraCheck", screenshot)
                        off = getPixel("officeCheck", screenshot)
                        print(f"[PIXELS] bonnieDoor={bd} (br={bd_brightness} bonnie?={bd_is_bonnie}) chica={cc} leftDoor={ld} "
                              f"rightDoor={rd} cam={cam} office={off} | "
                              f"facingRight={facingRight} camUp={cameraUp} "
                              f"inOffice={inOffice} robotAtDoor={robotAtDoor} "
                              f"lightOn={lightOn}")
                    except: pass

                # Periodic screenshot save (every 5s while in office)
                if SAVE_SCREENSHOTS and inOffice and (time.time() - lastScreenshotTime > 5.0):
                    lastScreenshotTime = time.time()
                    saveScreenshot(screenshot, label="periodic")

                # Death capture: inOffice just went from True to False without
                # warning (and we're not on title screen). That's a jumpscare.
                # Save the last few screenshots from the rolling buffer so we
                # can see what was on screen just before Bonnie (or whoever) struck.
                if SAVE_SCREENSHOTS and lastInOffice and not inOffice and not onTitle:
                    print("!!! DEATH DETECTED - saving last 5 screenshots from buffer")
                    for i, (t, sc) in enumerate(_recent_screenshots):
                        saveScreenshot(sc, label=f"death_frame{i}")
                lastInOffice = inOffice
        except Exception as e:
            # Don't die on a single bad frame
            pass

        time.sleep(0.1)


# =========================================================================
# OFFICE LOOP THREAD - does door checks while in office
# =========================================================================

def officeLoop():
    global leftDoorClosed, rightDoorClosed, robotAtDoor

    try:
        lastLeftCheck = 0
        lastRightCheck = 0

        while not timedOut:
            if not inOffice:
                time.sleep(0.2)
                continue

            now = time.time()

            if DUMB_MODE:
                # Just cycle the left door closed/open on a 2s timer
                if now - lastLeftCheck > 2.0:
                    lastLeftCheck = now
                    if not leftDoorClosed:
                        clickAt("leftDoor")
                        leftDoorClosed = True
                    else:
                        clickAt("leftDoor")
                        leftDoorClosed = False
                time.sleep(0.1)
                continue

            # --- LEFT SIDE: check for Bonnie via light flash ---
            if now - lastLeftCheck > 2.0:
                lastLeftCheck = now
                robotAtDoor = False
                # Flash left light
                moveTo("leftLight")
                pg.mouseDown()
                time.sleep(0.3)

                # Three checks while light is on
                for _ in range(3):
                    checkBonnie()
                    time.sleep(0.05)

                pg.mouseUp()

                # React to detection
                if robotAtDoor and not leftDoorClosed:
                    clickAt("leftDoor")
                    leftDoorClosed = True
                elif not robotAtDoor and leftDoorClosed:
                    clickAt("leftDoor")
                    leftDoorClosed = False
                robotAtDoor = False

            # --- RIGHT SIDE: check for Chica via light flash ---
            if now - lastRightCheck > 2.0:
                lastRightCheck = now
                robotAtDoor = False
                moveTo("rightLight")
                pg.mouseDown()
                time.sleep(0.3)
                # detectStates will set robotAtDoor if Chica is visible
                time.sleep(0.1)
                pg.mouseUp()

                if robotAtDoor and not rightDoorClosed:
                    clickAt("rightDoor")
                    rightDoorClosed = True
                elif not robotAtDoor and rightDoorClosed:
                    clickAt("rightDoor")
                    rightDoorClosed = False
                robotAtDoor = False

            time.sleep(0.1)
    except Exception as e:
        print(f"officeLoop crashed: {e}")


# =========================================================================
# GAME LOOP THREAD - handles title screens / night progression
# =========================================================================

def gameLoop():
    global leftDoorClosed, rightDoorClosed

    while not timedOut:
        try:
            if onTitle:
                print(f"Title screen detected. Stars: {int(star1) + int(star2) + int(star3)}. Clicking Continue.")
                # Reset door state for new night
                leftDoorClosed = False
                rightDoorClosed = False
                clickAt("continue")
                time.sleep(2.0)

                # If we've got 3 stars (beat night 5), try for 6th night
                if star3:
                    print("3 stars detected - attempting 6th night.")
                    time.sleep(1.0)

            time.sleep(0.3)
        except Exception as e:
            print(f"gameLoop error: {e}")
            time.sleep(0.5)


# =========================================================================
# MAIN
# =========================================================================

def main():
    print("=" * 60)
    print("FNAF Browser Autoplayer")
    print("=" * 60)
    print("SETUP:")
    print("  1. Open FNAF in your browser.")
    print("  2. Press F11 to make the browser truly fullscreen.")
    print("  3. Start the night manually (so you're past any intro).")
    print("  4. Come back here and hit Enter.")
    print()
    print("DEBUG KEYS (work any time the script is running):")
    print("  p = print mouse position (normalized 0-1)")
    print("  c = print RGB color under the cursor")
    print("  q = quit the script")
    print("=" * 60)
    input("Press Enter when the browser is open and the game is loaded...")

    # We can't easily tell which browser is running, so just check if any
    # common browser process is alive. If not, warn the user but continue.
    browsers = ["chrome.exe", "firefox.exe", "msedge.exe", "brave.exe", "opera.exe"]
    running = [p.name().lower() for p in psutil.process_iter(['name'])]
    if not any(b in running for b in browsers):
        print("WARNING: No common browser process detected. Continuing anyway.")
    else:
        print("Browser detected.")

    print("Switch to the browser window NOW. Starting in 5 seconds...")
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    print("Starting!")

    # Start keyboard listener (daemon so it dies with main thread)
    listener = keyboard.Listener(on_press=onKeyPress)
    listener.daemon = True
    listener.start()

    # Start worker threads
    t1 = threading.Thread(target=detectStates, daemon=True)
    t2 = threading.Thread(target=officeLoop, daemon=True)
    t3 = threading.Thread(target=gameLoop, daemon=True)
    t1.start()
    t2.start()
    t3.start()

    # Keep main alive until quit
    try:
        while not timedOut:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass

    print("Exiting.")


if __name__ == "__main__":
    main()
