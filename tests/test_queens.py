"""Tests for the Queens game logic. Run with:  python -m unittest -v"""
import unittest

from queens.queens_logic import (
    EMPTY,
    MARK,
    MAX_SIZE,
    MIN_SIZE,
    QUEEN,
    Game,
    count_solutions,
    find_conflicts,
    generate_puzzle,
    is_solved,
    solve,
)


def regions_connected(grid):
    n = len(grid)
    for reg in range(n):
        cells = {(r, c) for r in range(n) for c in range(n) if grid[r][c] == reg}
        if not cells:
            return False
        seen, stack = set(), [next(iter(cells))]
        while stack:
            r, c = stack.pop()
            if (r, c) in seen:
                continue
            seen.add((r, c))
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (r + dr, c + dc) in cells:
                    stack.append((r + dr, c + dc))
        if seen != cells:
            return False
    return True


class GeneratorTests(unittest.TestCase):
    def test_every_size_has_exactly_one_solution(self):
        for n in range(MIN_SIZE, MAX_SIZE + 1):
            for seed in range(3):
                with self.subTest(n=n, seed=seed):
                    grid, sol = generate_puzzle(n, seed=seed)
                    self.assertEqual(len(grid), n)
                    self.assertEqual({v for row in grid for v in row}, set(range(n)))
                    self.assertTrue(regions_connected(grid))
                    self.assertEqual(count_solutions(grid, 5), 1)
                    self.assertEqual(solve(grid), sol)
                    self.assertTrue(is_solved(grid, list(enumerate(sol))))

    def test_same_seed_gives_same_puzzle(self):
        self.assertEqual(generate_puzzle(6, seed=7), generate_puzzle(6, seed=7))


class RuleTests(unittest.TestCase):
    GRID = [
        [0, 0, 1, 1],
        [0, 2, 1, 1],
        [2, 2, 3, 3],
        [2, 2, 3, 3],
    ]

    def test_diagonal_touch_is_a_conflict(self):
        self.assertEqual(find_conflicts(self.GRID, [(0, 0), (1, 1)]), {(0, 0), (1, 1)})

    def test_same_row_column_region_conflict(self):
        self.assertEqual(len(find_conflicts(self.GRID, [(0, 0), (0, 3)])), 2)  # row
        self.assertEqual(len(find_conflicts(self.GRID, [(0, 0), (3, 0)])), 2)  # column
        # (1, 1) and (3, 0): different row and column, not touching, same region.
        self.assertEqual(find_conflicts(self.GRID, [(1, 1), (3, 0)]), {(1, 1), (3, 0)})

    def test_far_apart_queens_have_no_conflict(self):
        self.assertEqual(find_conflicts(self.GRID, [(0, 0), (2, 3)]), set())

    def test_incomplete_board_is_not_solved(self):
        self.assertFalse(is_solved(self.GRID, [(0, 0)]))


class GameTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(6, seed=1)

    def test_cycle_goes_empty_mark_queen_empty(self):
        g = self.game
        states = []
        for _ in range(4):
            g.cycle(0, 0)
            states.append(g.marks[0][0])
        self.assertEqual(states, [MARK, QUEEN, EMPTY, MARK])

    def test_right_click_clears(self):
        self.game.cycle(2, 2)
        self.game.clear_cell(2, 2)
        self.assertEqual(self.game.marks[2][2], EMPTY)

    def test_placing_the_solution_wins_and_locks_the_board(self):
        g = self.game
        for r, c in enumerate(g.solution):
            g.cycle(r, c)
            g.cycle(r, c)  # empty -> X -> queen
        self.assertTrue(g.solved)
        before = [row[:] for row in g.marks]
        for r in range(g.n):
            for c in range(g.n):
                g.cycle(r, c)       # ignored once solved
                g.clear_cell(r, c)  # ignored once solved
        self.assertEqual(g.marks, before)
        self.assertEqual(len(g.queens()), g.n)

    def test_wrong_queens_report_conflicts(self):
        g = self.game
        g.cycle(0, 0); g.cycle(0, 0)
        g.cycle(1, 1); g.cycle(1, 1)
        self.assertEqual(g.conflicts(), {(0, 0), (1, 1)})
        self.assertFalse(g.solved)

    def test_hints_eventually_solve_the_puzzle(self):
        g = self.game
        g.cycle(0, 0); g.cycle(0, 0)  # maybe a wrong queen
        for _ in range(g.n + 1):
            g.hint()
        self.assertTrue(g.solved)
        self.assertEqual(sorted(g.queens()), sorted(enumerate(g.solution)))

    def test_clear_resets_everything(self):
        g = self.game
        for r, c in enumerate(g.solution):
            g.cycle(r, c); g.cycle(r, c)
        g.clear()
        self.assertFalse(g.solved)
        self.assertEqual(g.queens(), [])


if __name__ == "__main__":
    unittest.main()
