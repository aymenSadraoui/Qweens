# Queens (LinkedIn-style puzzle) in Python

Place exactly one queen in every **row**, **column** and **colored region**.
Queens may never touch each other, not even diagonally.
Every generated puzzle has exactly **one** solution.

## Run it

Requires Python 3.8+ with Tkinter (included with the python.org installers
for Windows and macOS).

```
python queens.py              # 8x8 board
python queens.py --size 6     # 5 to 9
python queens.py --seed 42    # reproducible first puzzle
```

In VS Code: open this folder, open `queens.py`, press **F5** (a launch
configuration is included) or click the "Run Python File" button.

If Python says Tkinter is missing: on Debian/Ubuntu run
`sudo apt install python3-tk`, on macOS with Homebrew run
`brew install python-tk`.

## Controls

| Action | Result |
| --- | --- |
| Left click | cycle a cell: empty, X, queen, empty |
| Right click | empty the cell |
| `N` | new puzzle |
| `C` | clear the board |
| `H` | hint (removes wrong queens, places one correct queen) |
| `+` / `-` | bigger / smaller board (5x5 to 9x9) |

Queens that break a rule are drawn in red. The timer stops when you solve it.

## Files

- `queens_logic.py` - puzzle generator, solver, rule checks, game state (no GUI)
- `queens.py` - the Tkinter window
- `test_queens.py` - unit tests: `python -m unittest -v`
