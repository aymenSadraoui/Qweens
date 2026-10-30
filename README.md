<h1 align="center">👑 Qweens</h1>

<p align="center">
  An unlimited Queens puzzle game in Python.<br>
  Every board is freshly generated and has exactly one solution.
</p>

<p align="center">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="Python 3.8+" src="https://img.shields.io/badge/python-3.8%2B-3776AB?logo=python&logoColor=white">
  <img alt="No dependencies" src="https://img.shields.io/badge/dependencies-none-brightgreen">
  <img alt="Made for fun" src="https://img.shields.io/badge/made%20for-fun-ff7b60">
</p>

---

## Why Qweens?

The daily Queens puzzle on LinkedIn is great, but it gives you **one board a day**, and one a day is never enough. So I built Qweens: a version that generates a brand new puzzle every time you press `N`, so you can play for as long as you like, at any board size from 5x5 to 9x9.

It is a hobby project, made for fun. It is not affiliated with LinkedIn.

## The rules

Place exactly one queen in every **row**, **column**, and **colored region**.
Queens may never touch each other, not even diagonally.

Every generated puzzle has exactly **one** solution, so you never need to guess.

## Run it

Requires Python 3.8 or newer with Tkinter (included with the python.org installers for Windows and macOS). There is nothing else to install.

```bash
git clone https://github.com/aymenSadraoui/Qweens.git
cd Qweens

python queens.py              # 8x8 board
python queens.py --size 6     # any size from 5 to 9
python queens.py --seed 42    # reproducible first puzzle
```

If you use [uv](https://docs.astral.sh/uv/) and [just](https://github.com/casey/just), `just run` starts the game, and `just run 6 7` starts a 6x6 board with seed 7. Note that `just run` defaults to seed 42, so it always shows the same first puzzle. Press `N` for a new one.

In VS Code, open `queens.py` and click the **Run Python File** button.

**Tkinter missing?** On Debian/Ubuntu run `sudo apt install python3-tk`. On macOS with Homebrew run `brew install python-tk`.

## Controls

| Action | Result |
| --- | --- |
| Left click | cycle a cell: empty, X, queen, empty |
| Right click | empty the cell |
| `N` | new puzzle |
| `C` | clear the board |
| `H` | hint (removes wrong queens, then places one correct queen) |
| `+` / `-` | bigger / smaller board (5x5 to 9x9) |

Queens that break a rule are drawn in red. The timer stops when you solve the puzzle.

## How it works

The generator builds a puzzle backwards, so a solution is guaranteed to exist:

1. **Place the queens first.** A backtracking search finds a random arrangement with one queen per row and column and no two touching.
2. **Grow the regions.** Each queen seeds one colored region, and the regions expand cell by cell until the board is full. Every region stays connected.
3. **Make the solution unique.** A solver counts the solutions of the board. While there is more than one, the generator moves boundary cells between neighboring regions (never the queen cells, never breaking a region's connectivity) and keeps every change that does not increase the count.
4. **Verify.** A puzzle is only accepted once the solver confirms exactly one solution. Otherwise the generator starts over.

The puzzle logic lives in `queens_logic.py` and has no GUI code, so it is easy to test and reuse.

## Development

```bash
uv run pytest        # run the test suite (12 tests)
```

The tests cover the generator (every size has exactly one solution, connected regions, same seed gives the same puzzle), the rule checks (rows, columns, regions and diagonal touching) and the game state (clicking, hints, solving, clearing).

Two things to know:

- Run the tests with `pytest`, not `python -m unittest` from the repository root. The top-level `queens.py` launcher would shadow the `queens` package there.
- Importing the package also imports the GUI, so Tkinter must be installed even to run the tests.

## Project layout

```
Qweens/
├── queens.py                  # launcher: python queens.py
├── src/queens/
│   ├── __init__.py            # package entry point
│   ├── __main__.py            # python -m queens
│   ├── queens_logic.py        # puzzle generator, solver, rule checks, game state (no GUI)
│   └── gui.py                 # the Tkinter window
├── tests/test_queens.py       # unit tests
├── justfile                   # `just run` shortcut
├── pyproject.toml             # project metadata
└── LICENSE                    # MIT
```

## License

Qweens is open source under the [MIT License](LICENSE). Play it, share it, fork it, change it, learn from it. It was made for fun, and you can use it just for fun too.
