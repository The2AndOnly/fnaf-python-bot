## Description

This program can complete the first Five Nights at Freddy's game and unlock 3 stars without user input. Even if a night is failed, it will attempt it again. Please note that this wasn't made with the intention of being a cheat to unlock everything. (You can easily do that by editing the save file.)

This program was made and tested on `Windows 11` using `Python 3.14.3`

## How to run:

First, install `uv` from the GitHub (https://github.com/astral-sh/uv), using an install script in the docs (https://docs.astral.sh/uv/getting-started/installation), or  with `pip`: 
```bash
pip install uv
```
Second, ensure you have an applicable version of `Python` (>=3.14.3) installed:
```bash
uv python install <version>
```

Next, install the dependencies:

```bash
uv sync
```

Finally, run the program:

```bash
uv run beatfnaf1.py
```

Now just open FiveNightsatFreddys.exe and after a while it should start automatically moving the mouse and clicking to control the game. The program may break if you attempt to interfere with it while it's running.

To quit the program: Press `esc` to close the game, then press `ctrl + c` in the console to terminate the script.
NOTE: To (possibly) make it run faster, it doesn't detect when the game closes. So be aware that when you close the game, the mouse may still move around and click on things.

The program will quit automatically if 3 stars are detected on the menu.