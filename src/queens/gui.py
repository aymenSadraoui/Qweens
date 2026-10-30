"""Queens GUI application."""

import argparse
import sys
import time

try:
    import tkinter as tk
except ImportError:  # pragma: no cover - depends on the user's Python install
    sys.exit(
        "Tkinter is not available in this Python install.\n"
        "  Linux (Debian/Ubuntu): sudo apt install python3-tk\n"
        "  macOS (Homebrew):      brew install python-tk\n"
        "  Windows / python.org installers include it by default."
    )

from .queens_logic import EMPTY, MARK, MAX_SIZE, MIN_SIZE, QUEEN, Game

CELL = 64  # pixel size of one square
PAD = 6  # margin around the board inside the canvas
THIN = "#777777"  # thin grid lines
THICK = "#000000"  # borders between regions
INK = "#1a1a1a"  # queens
ALERT = "#d90000"  # conflicting queens

PALETTE = [
    "#ff7b60",  # coral
    "#ffc992",  # peach
    "#96bfff",  # blue
    "#b3dfa0",  # green
    "#dfa0df",  # purple
    "#fff780",  # yellow
    "#b9b29e",  # taupe
    "#a3d6d2",  # teal
    "#e0e0e0",  # light gray
]

# Crown outline in unit coordinates (0..1 in both directions).
CROWN = [
    (0.00, 1.00),
    (0.00, 0.30),
    (0.25, 0.58),
    (0.50, 0.05),
    (0.75, 0.58),
    (1.00, 0.30),
    (1.00, 1.00),
]


def format_time(seconds):
    seconds = int(seconds)
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


class QueensApp:
    def __init__(self, root, size=8, seed=None):
        self.root = root
        self.size = max(MIN_SIZE, min(MAX_SIZE, size))
        self.game = Game(self.size, seed)  # first puzzle (seed is optional)
        self.start = time.monotonic()
        self.final = None  # elapsed seconds once solved

        root.title("Queens")
        root.resizable(False, False)

        top = tk.Frame(root, padx=10, pady=8)
        top.pack(fill="x")
        tk.Button(top, text="New game", command=self.new_game).pack(side="left")
        tk.Button(top, text="Clear", command=self.clear).pack(side="left", padx=4)
        tk.Button(top, text="Hint", command=self.hint).pack(side="left")
        tk.Button(top, text="-", width=2, command=lambda: self.change_size(-1)).pack(
            side="left", padx=(14, 0)
        )
        self.size_var = tk.StringVar()
        tk.Label(top, textvariable=self.size_var, width=5).pack(side="left")
        tk.Button(top, text="+", width=2, command=lambda: self.change_size(1)).pack(
            side="left"
        )
        self.timer_var = tk.StringVar(value="00:00")
        tk.Label(top, textvariable=self.timer_var, font=("Helvetica", 16, "bold")).pack(
            side="right"
        )

        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(padx=10)

        self.status_var = tk.StringVar()
        tk.Label(
            root, textvariable=self.status_var, font=("Helvetica", 12, "bold")
        ).pack(pady=(8, 0))
        tk.Label(
            root,
            text="Left click: X, queen, empty  |  Right click: empty  |  keys: N C H + -",
            fg="#555555",
        ).pack(pady=(0, 8))

        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-2>", self.on_right_click)  # right click on macOS
        self.canvas.bind("<Button-3>", self.on_right_click)
        root.bind("<Key>", self.on_key)

        self.start_game()
        self.tick()

    # ---- actions -------------------------------------------------------
    def new_game(self):
        self.status_var.set("Generating puzzle...")
        self.root.update_idletasks()
        self.game = Game(self.size)
        self.start_game()

    def start_game(self):
        """Reset the timer and canvas for the puzzle in self.game."""
        self.start = time.monotonic()
        self.final = None
        side = self.size * CELL + 2 * PAD
        self.canvas.config(width=side, height=side)
        self.size_var.set(f"{self.size}x{self.size}")
        self.refresh()

    def clear(self):
        was_solved = self.game.solved
        self.game.clear()
        if was_solved:
            self.start = time.monotonic()
            self.final = None
        self.refresh()

    def hint(self):
        self.game.hint()
        self.refresh()

    def change_size(self, delta):
        new_size = max(MIN_SIZE, min(MAX_SIZE, self.size + delta))
        if new_size != self.size:
            self.size = new_size
            self.new_game()

    # ---- events --------------------------------------------------------
    def cell_at(self, event):
        col = (event.x - PAD) // CELL
        row = (event.y - PAD) // CELL
        if 0 <= row < self.size and 0 <= col < self.size:
            return row, col
        return None

    def on_left_click(self, event):
        cell = self.cell_at(event)
        if cell:
            self.game.cycle(*cell)
            self.refresh()

    def on_right_click(self, event):
        cell = self.cell_at(event)
        if cell:
            self.game.clear_cell(*cell)
            self.refresh()

    def on_key(self, event):
        key = (event.char or "").lower()
        if key == "n":
            self.new_game()
        elif key == "c":
            self.clear()
        elif key == "h":
            self.hint()
        elif key in ("+", "="):
            self.change_size(1)
        elif key in ("-", "_"):
            self.change_size(-1)

    # ---- timer ---------------------------------------------------------
    def elapsed(self):
        if self.final is not None:
            return self.final
        return time.monotonic() - self.start

    def tick(self):
        self.timer_var.set(format_time(self.elapsed()))
        self.root.after(200, self.tick)

    # ---- drawing -------------------------------------------------------
    def refresh(self):
        game = self.game
        if game.solved and self.final is None:
            self.final = time.monotonic() - self.start
        bad = game.conflicts()
        self.draw(bad)
        self.timer_var.set(format_time(self.elapsed()))
        if game.solved:
            self.status_var.set(
                f"Solved in {format_time(self.final)}!  Press N for a new puzzle."
            )
        else:
            text = f"Queens: {len(game.queens())}/{game.n}"
            if bad:
                text += "  -  conflict! (red queens break a rule)"
            self.status_var.set(text)

    def draw(self, bad):
        game = self.game
        n = game.n
        cv = self.canvas
        cv.delete("all")

        for r in range(n):
            for c in range(n):
                x0, y0 = PAD + c * CELL, PAD + r * CELL
                cv.create_rectangle(
                    x0,
                    y0,
                    x0 + CELL,
                    y0 + CELL,
                    fill=PALETTE[game.grid[r][c]],
                    outline=THIN,
                    width=1,
                )

        # Thick lines wherever two neighbouring cells belong to different regions.
        for r in range(n):
            for c in range(n):
                x0, y0 = PAD + c * CELL, PAD + r * CELL
                if c + 1 < n and game.grid[r][c] != game.grid[r][c + 1]:
                    cv.create_line(
                        x0 + CELL, y0, x0 + CELL, y0 + CELL, width=4, fill=THICK
                    )
                if r + 1 < n and game.grid[r][c] != game.grid[r + 1][c]:
                    cv.create_line(
                        x0, y0 + CELL, x0 + CELL, y0 + CELL, width=4, fill=THICK
                    )
        cv.create_rectangle(
            PAD, PAD, PAD + n * CELL, PAD + n * CELL, outline=THICK, width=4
        )

        for r in range(n):
            for c in range(n):
                state = game.marks[r][c]
                x0, y0 = PAD + c * CELL, PAD + r * CELL
                if state == MARK:
                    m = CELL * 0.30
                    cv.create_line(
                        x0 + m,
                        y0 + m,
                        x0 + CELL - m,
                        y0 + CELL - m,
                        width=3,
                        fill="#333333",
                    )
                    cv.create_line(
                        x0 + CELL - m,
                        y0 + m,
                        x0 + m,
                        y0 + CELL - m,
                        width=3,
                        fill="#333333",
                    )
                elif state == QUEEN:
                    is_bad = (r, c) in bad
                    self.draw_crown(x0, y0, ALERT if is_bad else INK)
                    if is_bad:
                        cv.create_rectangle(
                            x0 + 3,
                            y0 + 3,
                            x0 + CELL - 3,
                            y0 + CELL - 3,
                            outline=ALERT,
                            width=3,
                        )

        if game.solved:
            cx = cy = PAD + n * CELL / 2
            cv.create_text(
                cx + 2,
                cy + 2,
                text="SOLVED!",
                fill="white",
                font=("Helvetica", 40, "bold"),
            )
            cv.create_text(
                cx, cy, text="SOLVED!", fill="#0a6b0a", font=("Helvetica", 40, "bold")
            )

    def draw_crown(self, x0, y0, color):
        size = CELL * 0.56
        left = x0 + (CELL - size) / 2
        top = y0 + (CELL - size) / 2
        points = []
        for ux, uy in CROWN:
            points.extend((left + ux * size, top + uy * size))
        self.canvas.create_polygon(points, fill=color, outline=color)
        radius = size * 0.07
        for ux, uy in (CROWN[1], CROWN[3], CROWN[5]):
            px, py = left + ux * size, top + uy * size
            self.canvas.create_oval(
                px - radius,
                py - radius,
                px + radius,
                py + radius,
                fill=color,
                outline=color,
            )


def main():
    parser = argparse.ArgumentParser(description="Queens puzzle game")
    parser.add_argument(
        "--size",
        type=int,
        default=8,
        choices=range(MIN_SIZE, MAX_SIZE + 1),
        metavar=f"{MIN_SIZE}-{MAX_SIZE}",
        help="board size (default 8)",
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="seed for a reproducible first puzzle"
    )
    args = parser.parse_args()
    root = tk.Tk()
    QueensApp(root, args.size, args.seed)
    root.mainloop()


if __name__ == "__main__":
    main()
