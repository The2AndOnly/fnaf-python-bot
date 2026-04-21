import os
import threading
import time

import keyboard
import psutil

from src.game import terminate_on_error, game_loop, update_states

def is_running(name):
    for i in psutil.process_iter(["name"]):
        if i.info["name"] == name:
            return True
    return False

keyboard.add_hotkey("esc", lambda: os._exit(0))

print("Program started! Waiting for game to open...")

# Wait for the game to open before starting anything
while True:
    time.sleep(2)
    if is_running("FiveNightsatFreddys.exe"):
        break

# Wait 5 seconds to make sure the game is open in fullscreen
time.sleep(5)

game_loop_thread = threading.Thread(target=terminate_on_error, args=(game_loop,))
update_states_thread = threading.Thread(target=terminate_on_error, args=(update_states,))
game_loop_thread.start()
update_states_thread.start()