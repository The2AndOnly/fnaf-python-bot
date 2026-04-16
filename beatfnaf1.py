import pyautogui as pg
# from pynput import keyboard
import threading
import time

from src import PG_PAUSE, customPMC, isRunning, moveMouse, gameState, gameLifeCycle

pg.PAUSE = PG_PAUSE
pg.pixelMatchesColor = customPMC

# def onPress(key):
#     try:
#         match key.char:
#             case 'p':
#                 print(f"{getPosition()[0]}, {getPosition()[1]}")
#             case 'c':
#                 screenshot = pg.screenshot()
#                 width, height = screenshot.size
#                 print(screenshot.getpixel((int(getPosition()[0] * width), int(getPosition()[1] * height))))
#             case '1':
#                 moveMouse(coordinates["ready"])
#             case '2':
#                 moveMouse(coordinates["star2"])
#             case '3':
#                 moveMouse(coordinates["star3"])
#     except: pass
#     try:
#         if key == keyboard.Key.space:
#             officeLoop()
#     except: pass

def main():
    # listener = keyboard.Listener(on_press = onPress)
    # listener.start()
    print("Program started! Waiting for game to open...")
    # Wait for the game to open before starting anything
    while True:
        time.sleep(2.0)
        if isRunning("FiveNightsatFreddys.exe"):
            break
    # Wait 5 seconds to make sure the game is open in fullscreen
    time.sleep(5.0)
    moveMouse((0.6, 0.6))
    gameloopProcess = threading.Thread(target=gameState.loop)
    lifeCycle = threading.Thread(target=gameLifeCycle)
    gameloopProcess.start()
    lifeCycle.start()


if __name__ == "__main__":
    main()
