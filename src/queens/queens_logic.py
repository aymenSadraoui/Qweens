"""Game logic for Queens: puzzle generation, solving and validation.

Rules:
  * N x N board divided into N colored regions.
  * Place exactly one queen in every row, column and region.
  * No two queens may touch, not even diagonally.
"""

import random


def random_solution(n, rng):
    """Random queen placement: one per row/column, no two touching.

    Returns a list `sol` where sol[row] = column, or None on failure.
    """
    cols = []
    used = set()

    def backtrack(row):
        if row == n:
            return True
        options = list(range(n))
        rng.shuffle(options)
        for c in options:
            if c in used:
                continue
            if row > 0 and abs(c - cols[-1]) <= 1:
                continue
            cols.append(c)
            used.add(c)
            if backtrack(row + 1):
                return True
            cols.pop()
            used.discard(c)
        return False

    return cols[:] if backtrack(0) else None


def grow_regions(n, sol, rng):
    """Grow n connected regions, each seeded on one queen of `sol`."""
    grid = [[-1] * n for _ in range(n)]
    for r, c in enumerate(sol):
        grid[r][c] = r
    remaining = n * n - n
    while remaining > 0:
        candidates = []
        for r in range(n):
            for c in range(n):
                if grid[r][c] != -1:
                    continue
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < n and 0 <= cc < n and grid[rr][cc] != -1:
                        candidates.append((r, c, grid[rr][cc]))
        r, c, reg = rng.choice(candidates)
        grid[r][c] = reg
        remaining -= 1
    return grid


def count_solutions(grid, limit=2):
    """Count valid solutions of the puzzle, stopping once `limit` is reached."""
    n = len(grid)
    count = 0
    cols = []
    used_cols = set()
    used_regions = set()

    def backtrack(row):
        nonlocal count
        if count >= limit:
            return
        if row == n:
            count += 1
            return
        for c in range(n):
            if c in used_cols:
                continue
            if row > 0 and abs(c - cols[-1]) <= 1:
                continue
            reg = grid[row][c]
            if reg in used_regions:
                continue
            cols.append(c)
            used_cols.add(c)
            used_regions.add(reg)
            backtrack(row + 1)
            cols.pop()
            used_cols.discard(c)
            used_regions.discard(reg)

    backtrack(0)
    return count


def solve(grid):
    """Return the first solution found as a list sol[row] = column, or None."""
    n = len(grid)
    cols = []
    used_cols = set()
    used_regions = set()

    def backtrack(row):
        if row == n:
            return True
        for c in range(n):
            if c in used_cols:
                continue
            if row > 0 and abs(c - cols[-1]) <= 1:
                continue
            reg = grid[row][c]
            if reg in used_regions:
                continue
            cols.append(c)
            used_cols.add(c)
            used_regions.add(reg)
            if backtrack(row + 1):
                return True
            cols.pop()
            used_cols.discard(c)
            used_regions.discard(reg)
        return False

    return cols[:] if backtrack(0) else None


def _region_connected(grid, reg, skip):
    """True if region `reg` stays 4-connected when cell `skip` is removed."""
    n = len(grid)
    cells = {
        (r, c)
        for r in range(n)
        for c in range(n)
        if grid[r][c] == reg and (r, c) != skip
    }
    if not cells:
        return False
    start = next(iter(cells))
    seen = set()
    stack = [start]
    while stack:
        r, c = stack.pop()
        if (r, c) in seen:
            continue
        seen.add((r, c))
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (r + dr, c + dc)
            if nxt in cells and nxt not in seen:
                stack.append(nxt)
    return len(seen) == len(cells)


def _make_unique(grid, sol, rng, iterations=4000, cap=40):
    """Repair `grid` in place by moving boundary cells between regions.

    Queen cells of `sol` are never moved, so `sol` always stays a valid
    solution; each accepted move never increases the number of solutions.
    Returns True once the puzzle has exactly one solution.
    """
    n = len(grid)
    fixed = {(r, c) for r, c in enumerate(sol)}
    current = count_solutions(grid, cap)
    for _ in range(iterations):
        if current == 1:
            return True
        r = rng.randrange(n)
        c = rng.randrange(n)
        if (r, c) in fixed:
            continue
        old = grid[r][c]
        options = []
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < n and 0 <= cc < n and grid[rr][cc] != old:
                options.append(grid[rr][cc])
        if not options:
            continue
        if not _region_connected(grid, old, (r, c)):
            continue
        new = rng.choice(options)
        grid[r][c] = new
        cnt = count_solutions(grid, cap)
        if cnt <= current:
            current = cnt
        else:
            grid[r][c] = old
    return current == 1


def generate_puzzle(n, seed=None, max_attempts=2000):
    """Generate a puzzle with exactly one solution.

    Returns (grid, solution) where grid[r][c] is the region id (0..n-1) and
    solution[r] is the column of the queen in row r.
    """
    rng = random.Random(seed)
    for _ in range(max_attempts):
        sol = random_solution(n, rng)
        if sol is None:
            continue
        grid = grow_regions(n, sol, rng)
        if _make_unique(grid, sol, rng) and count_solutions(grid, 2) == 1:
            return grid, sol
    raise RuntimeError("Could not generate a puzzle with a unique solution")


def find_conflicts(grid, queens):
    """Return the set of (row, col) queens that break a rule.

    `queens` is an iterable of (row, col).
    """
    queens = list(queens)
    bad = set()
    for i in range(len(queens)):
        r1, c1 = queens[i]
        for j in range(i + 1, len(queens)):
            r2, c2 = queens[j]
            if (
                r1 == r2
                or c1 == c2
                or grid[r1][c1] == grid[r2][c2]
                or (abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1)
            ):
                bad.add((r1, c1))
                bad.add((r2, c2))
    return bad


def is_solved(grid, queens):
    """True when the queens form a complete, valid solution."""
    queens = list(queens)
    n = len(grid)
    if len(queens) != n:
        return False
    if find_conflicts(grid, queens):
        return False
    rows = {r for r, _ in queens}
    cols = {c for _, c in queens}
    regs = {grid[r][c] for r, c in queens}
    return len(rows) == n and len(cols) == n and len(regs) == n


MIN_SIZE = 5
MAX_SIZE = 9

EMPTY, MARK, QUEEN = 0, 1, 2  # cell states: blank, X marker, queen


class Game:
    """State of one Queens puzzle being played (no graphics here)."""

    def __init__(self, n, seed=None):
        self.n = n
        self.grid, self.solution = generate_puzzle(n, seed)
        self.marks = [[EMPTY] * n for _ in range(n)]
        self.solved = False
        self._rng = random.Random()

    def queens(self):
        return [
            (r, c)
            for r in range(self.n)
            for c in range(self.n)
            if self.marks[r][c] == QUEEN
        ]

    def conflicts(self):
        return find_conflicts(self.grid, self.queens())

    def _update_solved(self):
        self.solved = is_solved(self.grid, self.queens())

    def cycle(self, r, c):
        """Left click: empty -> X -> queen -> empty."""
        if self.solved:
            return
        self.marks[r][c] = (self.marks[r][c] + 1) % 3
        self._update_solved()

    def clear_cell(self, r, c):
        """Right click: empty the cell."""
        if self.solved:
            return
        self.marks[r][c] = EMPTY
        self._update_solved()

    def clear(self):
        """Remove every queen and X from the board."""
        self.marks = [[EMPTY] * self.n for _ in range(self.n)]
        self.solved = False

    def hint(self):
        """Remove wrong queens, then place one correct queen.

        Returns the (row, col) placed, or None if nothing was needed.
        """
        if self.solved:
            return None
        for r in range(self.n):
            for c in range(self.n):
                if self.marks[r][c] == QUEEN and self.solution[r] != c:
                    self.marks[r][c] = EMPTY
        missing = [
            (r, c) for r, c in enumerate(self.solution) if self.marks[r][c] != QUEEN
        ]
        placed = None
        if missing:
            placed = self._rng.choice(missing)
            self.marks[placed[0]][placed[1]] = QUEEN
        self._update_solved()
        return placed
