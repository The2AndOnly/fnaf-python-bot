import time
import psutil
import threading
from Bot.FNAF1.beatfnaf1 import gameLoop, state

if __name__ == "__main__":
    # listener = keyboard.Listener(on_press = onPress)
    # listener.start()

    print("Program started! Waiting for game to open...")

    # Wait for the game to open before starting anything
    def isRunning(name):
        print("Checking if process is running...")
        for i in psutil.process_iter(["name"]):
            if i.info["name"] == name:
                return True
        return False

    while True:
        time.sleep(2.0)
        if isRunning("FiveNightsatFreddys.exe"):
            print("Game detected! Starting bot...")
            break

    # Wait 5 seconds to make sure the game is open in fullscreen
    
    time.sleep(1.0)
    gameloopProcess = threading.Thread(target=gameLoop, daemon=True) # daemon kills it when the main thread exits
    detectProcess = threading.Thread(target=state.detectStates, daemon=True)
    gameloopProcess.start()
    detectProcess.start()

    # If one of them dies, the main thread also dies
    gameloopProcess.join()
    detectProcess.join()