This program can complete Fnaf 1 and unlock 3 stars without user input. Even if a night is failed, it will attempt it again. Please note that this wasn't made with the intention of being a cheat to unlock everything. (You can easily do that by editing the save file.)

This program was made and tested on Windows 11 using Python version 3.14.3

Required modules:
- pyautogui
- pillow (for pyautogui)
- psutil (For detecting when the app opens; not needed to beat the game)

How to run:

First, have Python with pip installed: https://www.python.org/downloads/

Next, create a virtual environment and install the dependencies:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Finally, run the program:

```bash
python beatfnaf1.py
```

Now just open FiveNightsatFreddys.exe and after a while it should start automatically moving the mouse and clicking to control the game. The program may break if you attempt to interfere with it while it's running.

To quit the program: Press `esc` to close the game, then press `ctrl + c` in the console to terminate the script.
NOTE: To (possibly) make it run faster, it doesn't detect when the game closes. So be aware that when you close the game, the mouse may still move around and click on things.

The program will quit automatically if 3 stars are detected on the menu.
