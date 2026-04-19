This program can complete FNAF 1 and unlock 3 stars without user input. Even if a night is failed, it will attempt it again. Please note that this wasn't made with the intention of being a cheat to unlock everything. (You can easily do that by editing the save file.)

This program was made and tested on Windows 11 using Python version 3.14.3

Required modules:
- keyboard (for adding a hotkey to terminate the script when `esc` is pressed; not necessary to beat the game)
- mouse
- mss
- psutil (for detecting when the app opens; also not necessary to beat the game)

How to run:

First, make sure you have Python with pip installed: https://www.python.org/downloads/.

Then, download this repo (or just beatfnaf1.py and requirements.txt).

Next, install the dependencies:

```bash
pip install -r requirements.txt
```

Finally, run the program:

```bash
python src/
```

Now just open FiveNightsatFreddys.exe, and after a while the script should start automatically moving and clicking the mouse to control the game. The program may break if you attempt to interfere with it while it's running.

To quit the program: Pressing `esc` will close the game and terminate the script.

The program will quit automatically if 3 stars are detected on the menu.